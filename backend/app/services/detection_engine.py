from collections import deque, defaultdict
from datetime import datetime, timezone
from typing import List
from app.models import Severity, Alert

SQL_INJECTION_PATTERNS = [
    "union select", "select.*from", "or 1=1", "drop table",
    "xp_cmdshell", "exec(", "exec sp_", "';", "-- ", "1=1--",
    "admin'--", "' or '1'='1", "' or 1=1--",
]

SENSITIVE_PATHS = [
    "/admin", "/wp-admin", "/.env", "/.git",
    "/phpmyadmin", "/wp-login.php",
]

class SlidingWindow:
    def __init__(self, maxlen: int = 200):
        self.events = deque(maxlen=maxlen)

    def add(self, entry: dict):
        self.events.append(entry)

    def trim(self, window_sec: float):
        cutoff = datetime.now(timezone.utc).timestamp() - window_sec
        while self.events and self.events[0]["ts"] < cutoff:
            self.events.popleft()

    def count(self) -> int:
        return len(self.events)

class RuleEngine:
    def __init__(self):
        self.failed_ssh_by_ip: dict[str, SlidingWindow] = defaultdict(lambda: SlidingWindow(50))
        self.port_scan_by_ip: dict[str, SlidingWindow] = defaultdict(lambda: SlidingWindow(100))
        self.failed_logins_global = SlidingWindow(100)
        self.http_404_by_ip: dict[str, SlidingWindow] = defaultdict(lambda: SlidingWindow(100))

    def evaluate(self, entry: dict) -> list[dict]:
        alerts: list[dict] = []
        ts = entry["timestamp"].timestamp() if isinstance(entry["timestamp"], datetime) else entry["timestamp"]
        now_ts = datetime.now(timezone.utc).timestamp()
        ip = entry.get("source_ip") or "0.0.0.0"
        event_type = entry.get("event_type", "")
        severity = entry.get("severity", Severity.info)
        path = str(entry.get("parsed_fields", {}).get("path", ""))
        username = entry.get("username")

        # Brute force SSH
        if event_type in ("ssh_failed", "ssh_invalid_user") and ip:
            w = self.failed_ssh_by_ip[ip]
            w.add({"ts": ts})
            w.trim(60)
            if w.count() > 5:
                alerts.append({
                    "rule_name": "brute_force_ssh",
                    "severity": Severity.critical,
                    "description": f"Brute force SSH from {ip}: {w.count()} failed attempts in 60s",
                    "source_ip": ip,
                    "affected_user": username,
                })

        # Port scan
        if event_type in ("ssh_failed", "ssh_invalid_user", "ssh_accepted", "http_request") and ip:
            w = self.port_scan_by_ip[ip]
            w.add({"ts": ts, "port": entry.get("parsed_fields", {}).get("port", 0)})
            w.trim(30)
            if w.count() > 10:
                ports = len(set(e.get("port", 0) for e in w.events))
                if ports > 5:
                    alerts.append({
                        "rule_name": "port_scan",
                        "severity": Severity.critical,
                        "description": f"Port scan from {ip}: {w.count()} attempts to {ports} ports in 30s",
                        "source_ip": ip,
                        "affected_user": None,
                    })

        # SQL injection
        if event_type == "http_request" or event_type == "unknown":
            check_str = path + " " + entry.get("raw_message", "")
            for pat in SQL_INJECTION_PATTERNS:
                if pat.lower() in check_str.lower():
                    alerts.append({
                        "rule_name": "sql_injection",
                        "severity": Severity.critical,
                        "description": f"SQL injection attempt from {ip}: pattern '{pat}' in request",
                        "source_ip": ip,
                        "affected_user": None,
                    })
                    break

        # Off-hours login
        if event_type == "ssh_accepted" and ip:
            if isinstance(entry["timestamp"], datetime):
                h = entry["timestamp"].hour
            else:
                h = datetime.fromtimestamp(ts, tz=timezone.utc).hour
            if 0 <= h < 6:
                alerts.append({
                    "rule_name": "off_hours_login",
                    "severity": Severity.warning,
                    "description": f"Successful SSH login from {ip} during off-hours ({h}:00 UTC)",
                    "source_ip": ip,
                    "affected_user": username,
                })

        # Mass failed logins
        if event_type in ("ssh_failed", "ssh_invalid_user"):
            self.failed_logins_global.add({"ts": ts})
            self.failed_logins_global.trim(60)
            if self.failed_logins_global.count() > 20:
                ats = self.failed_logins_global.events
                latest_ts = max(e["ts"] for e in ats) if ats else ts
                if latest_ts > now_ts - 10:
                    alerts.append({
                        "rule_name": "mass_failed_logins",
                        "severity": Severity.warning,
                        "description": f"Mass failed logins: {self.failed_logins_global.count()} attempts in 60s",
                        "source_ip": None,
                        "affected_user": None,
                    })

        # Admin panel enumeration
        if event_type == "http_request":
            for sp in SENSITIVE_PATHS:
                if path.lower().startswith(sp):
                    alerts.append({
                        "rule_name": "admin_enumeration",
                        "severity": Severity.warning,
                        "description": f"Admin panel access attempt from {ip}: {path}",
                        "source_ip": ip,
                        "affected_user": None,
                    })
                    break

        # Path enumeration (404)
        sb = entry.get("parsed_fields", {})
        if sb.get("status") == 404 and ip:
            w = self.http_404_by_ip[ip]
            w.add({"ts": ts})
            w.trim(60)
            if w.count() > 15:
                alerts.append({
                    "rule_name": "path_enumeration",
                    "severity": Severity.warning,
                    "description": f"Path enumeration from {ip}: {w.count()} 404s in 60s",
                    "source_ip": ip,
                    "affected_user": None,
                })

        return alerts

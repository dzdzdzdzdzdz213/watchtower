import re
import json
from datetime import datetime, timezone
from typing import Optional
from app.models import Severity

SSH_FAILED = re.compile(
    r"(?P<timestamp>\w{3}\s+\d+\s+\d+:\d+:\d+)\s+"
    r"(?P<hostname>\S+)\s+sshd\[\d+\]:\s+"
    r"Failed\s+password\s+for\s+(invalid\s+user\s+)?"
    r"(?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)\s+port\s+(?P<port>\d+)"
)

SSH_ACCEPTED = re.compile(
    r"(?P<timestamp>\w{3}\s+\d+\s+\d+:\d+:\d+)\s+"
    r"(?P<hostname>\S+)\s+sshd\[\d+\]:\s+"
    r"Accepted\s+password\s+for\s+(?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)"
)

SSH_INVALID = re.compile(
    r"(?P<timestamp>\w{3}\s+\d+\s+\d+:\d+:\d+)\s+"
    r"(?P<hostname>\S+)\s+sshd\[\d+\]:\s+"
    r"Invalid\s+user\s+(?P<username>\S+)\s+from\s+(?P<source_ip>[\d.]+)"
)

NGINX_COMBINED = re.compile(
    r'(?P<source_ip>[\d.]+)\s+-\s+-\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>\w+)\s+(?P<path>\S+)\s+\S+"\s+'
    r'(?P<status>\d{3})\s+(?P<size>\d+|-)'
    r'(?:\s+"(?P<referer>[^"]*)"\s+"(?P<user_agent>[^"]*)")?'
)

SYSLOG_PRIORITY = re.compile(r"<(\d+)>")
SYSLOG_GENERIC = re.compile(
    r"(?P<timestamp>\w{3}\s+\d+\s+\d+:\d+:\d+)\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<process>\S+)(?:\[(?P<pid>\d+)\])?:\s+"
    r"(?P<message>.*)"
)

SENSITIVE_PATHS = re.compile(r"/(admin|wp-admin|\.env|\.git|phpmyadmin|wp-login\.php)", re.IGNORECASE)
SQL_INJECTION = re.compile(
    r"(union\s+select|select\s+.*\s+from|or\s+1=1|drop\s+table|xp_cmdshell|"
    r"exec\s*\(|exec\s+sp_|';|--\s|1=1--|admin'--)",
    re.IGNORECASE
)

SYSLOG_MONTHS = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
                 "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}

def _parse_syslog_ts(ts_str: str, year: int | None = None) -> datetime:
    parts = ts_str.strip().split()
    if len(parts) >= 3:
        mon = SYSLOG_MONTHS.get(parts[0][:3], 1)
        day = int(parts[1])
        time_parts = parts[2].split(":")
        h, m, s = int(time_parts[0]), int(time_parts[1]), int(time_parts[2].split(".")[0])
        if year is None:
            year = datetime.now(timezone.utc).year
        return datetime(year, mon, day, h, m, s, tzinfo=timezone.utc)
    return datetime.now(timezone.utc)

def _nginx_ts(ts_str: str) -> datetime:
    return datetime.strptime(ts_str.split(" ")[0], "%d/%b/%Y:%H:%M:%S").replace(tzinfo=timezone.utc)

def parse_log(line: str) -> dict:
    m = SSH_FAILED.search(line)
    if m:
        return {
            "timestamp": _parse_syslog_ts(m.group("timestamp")),
            "source_ip": m.group("source_ip"),
            "event_type": "ssh_failed",
            "severity": Severity.warning,
            "hostname": m.group("hostname"),
            "username": m.group("username"),
            "parsed_fields": {"port": int(m.group("port"))},
            "format_detected": "ssh",
        }

    m = SSH_ACCEPTED.search(line)
    if m:
        return {
            "timestamp": _parse_syslog_ts(m.group("timestamp")),
            "source_ip": m.group("source_ip"),
            "event_type": "ssh_accepted",
            "severity": Severity.info,
            "hostname": m.group("hostname"),
            "username": m.group("username"),
            "parsed_fields": {},
            "format_detected": "ssh",
        }

    m = SSH_INVALID.search(line)
    if m:
        return {
            "timestamp": _parse_syslog_ts(m.group("timestamp")),
            "source_ip": m.group("source_ip"),
            "event_type": "ssh_invalid_user",
            "severity": Severity.warning,
            "hostname": m.group("hostname"),
            "username": m.group("username"),
            "parsed_fields": {},
            "format_detected": "ssh",
        }

    m = NGINX_COMBINED.search(line)
    if m:
        path = m.group("path")
        status = int(m.group("status"))
        severity = Severity.warning if status >= 400 else Severity.info
        is_critical = False
        if SQL_INJECTION.search(path):
            severity = Severity.critical
            is_critical = True
        elif SENSITIVE_PATHS.search(path):
            severity = Severity.critical
        return {
            "timestamp": _nginx_ts(m.group("timestamp")),
            "source_ip": m.group("source_ip"),
            "event_type": "http_request" if not is_critical else "sql_injection" if SQL_INJECTION.search(path) else "admin_enumeration",
            "severity": severity,
            "hostname": None,
            "username": None,
            "parsed_fields": {
                "method": m.group("method"),
                "path": path,
                "status": status,
                "size": m.group("size"),
                "user_agent": m.group("user_agent") or "",
            },
            "format_detected": "nginx",
        }

    # Try JSON
    try:
        data = json.loads(line)
        if isinstance(data, dict):
            pf = {}
            def flatten(obj, prefix="", depth=0):
                if depth > 2:
                    return
                for k, v in obj.items():
                    key = f"{prefix}.{k}" if prefix else k
                    if isinstance(v, dict):
                        flatten(v, key, depth + 1)
                    else:
                        pf[key] = v
            flatten(data)
            ts = None
            for f in ["timestamp", "ts", "time", "date", "@timestamp"]:
                if f in pf:
                    try:
                        ts = datetime.fromisoformat(str(pf[f]).replace("Z", "+00:00"))
                    except (ValueError, TypeError):
                        pass
                    break
            return {
                "timestamp": ts or datetime.now(timezone.utc),
                "source_ip": str(pf.get("source_ip") or pf.get("src_ip") or pf.get("ip") or ""),
                "event_type": str(pf.get("event_type") or pf.get("event") or pf.get("type") or "json_log"),
                "severity": Severity.critical if str(pf.get("severity", "")).lower() == "critical"
                            else Severity.warning if str(pf.get("severity", "")).lower() == "warning"
                            else Severity.info,
                "hostname": str(pf.get("hostname") or pf.get("host") or ""),
                "username": str(pf.get("username") or pf.get("user") or ""),
                "parsed_fields": pf,
                "format_detected": "json",
            }
    except (json.JSONDecodeError, ValueError):
        pass

    # Generic syslog
    m = SYSLOG_GENERIC.search(line)
    if m:
        msg = m.group("message")
        sev = Severity.info
        if m.group("process"):
            prio_match = SYSLOG_PRIORITY.search(line)
            if prio_match:
                prio = int(prio_match.group(1))
                sev_val = prio & 7
                if sev_val <= 1:
                    sev = Severity.critical
                elif sev_val <= 4:
                    sev = Severity.warning
        return {
            "timestamp": _parse_syslog_ts(m.group("timestamp")),
            "source_ip": None,
            "event_type": "syslog",
            "severity": sev,
            "hostname": m.group("hostname"),
            "username": None,
            "parsed_fields": {"process": m.group("process") or "", "pid": m.group("pid") or "", "message": msg},
            "format_detected": "syslog",
        }

    # Fallback
    return {
        "timestamp": datetime.now(timezone.utc),
        "source_ip": None,
        "event_type": "unknown",
        "severity": Severity.info,
        "hostname": None,
        "username": None,
        "parsed_fields": {},
        "format_detected": "unknown",
    }

import asyncio
import random
from datetime import datetime, timedelta, timezone
from app.database import async_session, init_db
from app.models import Organization, LogEntry, Alert, Severity, AlertStatus
from app.services.auth import hash_password
from app.services.log_parser import parse_log
from app.services.detection_engine import RuleEngine

SEED_API_KEY = "00000000-0000-0000-0000-000000000001"

SSH_LINES = [
    'Jun  7 02:15:01 web-server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:02 web-server sshd[1234]: Failed password for invalid user admin from 10.0.0.5 port 22 ssh2',
    'Jun  7 02:15:03 web-server sshd[1235]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:04 web-server sshd[1236]: Accepted password for jdoe from 10.0.0.50 port 22 ssh2',
    'Jun  7 02:15:05 web-server sshd[1237]: Failed password for invalid user admin from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:06 web-server sshd[1238]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:07 web-server sshd[1239]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:08 web-server sshd[1240]: Failed password for invalid user test from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:09 web-server sshd[1241]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 02:15:10 web-server sshd[1242]: Failed password for root from 192.168.1.100 port 22 ssh2',
    'Jun  7 22:30:00 web-server sshd[2000]: Accepted password for jdoe from 10.0.0.50 port 22 ssh2',
    'Jun  8 03:00:00 web-server sshd[2100]: Accepted password for jdoe from 10.0.0.50 port 22 ssh2',
    'Jun  8 03:00:01 web-server sshd[2101]: Accepted password for admin from 10.0.0.5 port 22 ssh2',
]

NGINX_LINES = [
    '192.168.1.100 - - [07/Jun/2026:14:30:00 +0000] "GET / HTTP/1.1" 200 1234 "-" "Mozilla/5.0"',
    '192.168.1.100 - - [07/Jun/2026:14:30:01 +0000] "GET /admin HTTP/1.1" 403 52 "-" "Mozilla/5.0"',
    '192.168.1.100 - - [07/Jun/2026:14:30:02 +0000] "GET /wp-admin HTTP/1.1" 404 23 "-" "Mozilla/5.0"',
    '10.0.0.5 - - [07/Jun/2026:14:30:05 +0000] "GET /search?q=test%27+OR+1%3D1-- HTTP/1.1" 200 500 "-" "sqlmap/1.0"',
    '10.0.0.5 - - [07/Jun/2026:14:30:06 +0000] "GET /products?id=1+UNION+SELECT+1,2,3 HTTP/1.1" 200 999 "-" "sqlmap/1.0"',
    '10.0.0.5 - - [07/Jun/2026:14:30:07 +0000] "POST /login HTTP/1.1" 302 0 "-" "curl/8.0"',
    '192.168.1.100 - - [07/Jun/2026:14:30:10 +0000] "GET /.env HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:11 +0000] "GET /.git/config HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:12 +0000] "GET /phpmyadmin HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:13 +0000] "GET /test HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:14 +0000] "GET /backup HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:15 +0000] "GET /config HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:16 +0000] "GET /private HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:17 +0000] "GET /debug HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:18 +0000] "GET /logs HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:19 +0000] "GET /tmp HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:20 +0000] "GET /old HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:21 +0000] "GET /test2 HTTP/1.1" 404 23 "-" "nmap"',
    '192.168.1.100 - - [07/Jun/2026:14:30:22 +0000] "GET /admin/config HTTP/1.1" 403 52 "-" "nmap"',
]

JSON_LINES = [
    '{"timestamp": "2026-06-07T18:00:00Z", "source_ip": "10.0.0.99", "event_type": "firewall_block", "severity": "warning", "hostname": "fw-01", "message": "Blocked inbound connection from 45.33.32.156 port 8443"}',
    '{"timestamp": "2026-06-07T18:05:00Z", "source_ip": "10.0.0.99", "event_type": "firewall_block", "severity": "info", "hostname": "fw-01", "message": "Blocked inbound connection from 45.33.32.157 port 22"}',
    '{"timestamp": "2026-06-08T00:00:00Z", "source_ip": "10.0.0.5", "event_type": "login", "severity": "info", "username": "jdoe", "message": "User jdoe logged in via VPN"}',
    '{"timestamp": "2026-06-08T00:05:00Z", "source_ip": "10.0.0.5", "event_type": "login", "severity": "critical", "username": "admin", "message": "Failed VPN login for admin from 203.0.113.5"}',
]

SYSLOG_LINES = [
    '<13>Jun  7 08:00:00 kernel: [123456] CPU0: Core temperature above threshold',
    '<14>Jun  7 08:01:00 kernel: [123457] CPU0: Core temperature above threshold',
]

ALL_LINES = SSH_LINES + NGINX_LINES + JSON_LINES + SYSLOG_LINES

async def seed():
    await init_db()
    async with async_session() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(Organization).where(Organization.api_key == SEED_API_KEY)
        )
        existing = result.scalar_one_or_none()
        if existing:
            print("Seed org already exists, skipping")
            return

        org = Organization(
            name="DemoCorp",
            email="demo@watchtower.dev",
            password_hash=hash_password("demo1234"),
            api_key=SEED_API_KEY,
        )
        db.add(org)
        await db.flush()
        print(f"Created org: {org.name} (api_key: {org.api_key})")

        now = datetime.now(timezone.utc)
        rule_engine = RuleEngine()
        for i, line in enumerate(ALL_LINES):
            ts_offset = timedelta(hours=random.uniform(-48, 0))
            parsed = parse_log(line)
            entry = LogEntry(
                org_id=org.id,
                timestamp=parsed["timestamp"] if parsed["timestamp"] else (now + ts_offset),
                source_ip=parsed["source_ip"],
                event_type=parsed["event_type"],
                severity=parsed["severity"],
                raw_message=line,
                parsed_fields=parsed["parsed_fields"],
                hostname=parsed["hostname"],
                username=parsed["username"],
            )
            db.add(entry)

            alert_dicts = rule_engine.evaluate({
                "timestamp": entry.timestamp,
                "source_ip": entry.source_ip,
                "event_type": entry.event_type,
                "severity": entry.severity,
                "raw_message": line,
                "parsed_fields": parsed["parsed_fields"],
                "username": entry.username,
            })
            for ad in alert_dicts:
                alert = Alert(
                    org_id=org.id,
                    rule_name=ad["rule_name"],
                    severity=ad["severity"],
                    description=ad["description"],
                    source_ip=ad["source_ip"],
                    affected_user=ad["affected_user"],
                    first_seen=now + ts_offset,
                    last_seen=now + ts_offset,
                )
                db.add(alert)

        await db.commit()
        print(f"Seeded {len(ALL_LINES)} log entries")
        print("Login with: demo@watchtower.dev / demo1234")

if __name__ == "__main__":
    asyncio.run(seed())

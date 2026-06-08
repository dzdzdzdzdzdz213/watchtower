import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models import Organization, LogEntry, Alert, AlertStatus
from app.services.log_parser import parse_log
from app.services.detection_engine import RuleEngine
from app.services.websocket_manager import ws_manager
from app.routers.auth_router import DEV_EMAIL, DEV_API_KEY
from datetime import datetime, timezone, timedelta

router = APIRouter(tags=["ingest"])

rule_engine = RuleEngine()

class IngestRequest(BaseModel):
    logs: List[str]

@router.post("/ingest/{api_key}")
async def ingest_logs(api_key: str, req: IngestRequest, db: AsyncSession = Depends(get_db)):
    if api_key == DEV_API_KEY:
        parsed_count = len(req.logs)
        return {"ingested": parsed_count, "alerts_created": 0, "errors": []}
    try:
        result = await db.execute(select(Organization).where(Organization.api_key == uuid.UUID(api_key)))
        org = result.scalar_one_or_none()
        if not org:
            raise HTTPException(status_code=404, detail="Invalid API key")
        if len(req.logs) > 1000:
            raise HTTPException(status_code=422, detail="Max 1000 logs per request")

        parsed_count = 0
        alert_count = 0
        errors = []

        for line in req.logs:
            if not line.strip():
                continue
            try:
                parsed = parse_log(line.strip())
                entry = LogEntry(
                    org_id=org.id,
                    timestamp=parsed["timestamp"],
                    source_ip=parsed["source_ip"],
                    event_type=parsed["event_type"],
                    severity=parsed["severity"],
                    raw_message=line.strip(),
                    parsed_fields=parsed["parsed_fields"],
                    hostname=parsed["hostname"],
                    username=parsed["username"],
                )
                db.add(entry)
                parsed_count += 1

                alert_dicts = rule_engine.evaluate({
                    "timestamp": entry.timestamp,
                    "source_ip": entry.source_ip,
                    "event_type": entry.event_type,
                    "severity": entry.severity,
                    "raw_message": line.strip(),
                    "parsed_fields": parsed["parsed_fields"],
                    "username": entry.username,
                })
                for ad in alert_dicts:
                    dup_result = await db.execute(
                        select(Alert).where(
                            Alert.org_id == org.id,
                            Alert.rule_name == ad["rule_name"],
                            Alert.source_ip == ad["source_ip"],
                            Alert.status == AlertStatus.open,
                            Alert.last_seen > datetime.now(timezone.utc) - timedelta(minutes=5),
                        ).limit(1)
                    )
                    existing = dup_result.scalar_one_or_none()
                    if existing:
                        existing.last_seen = datetime.now(timezone.utc)
                        existing.log_count += 1
                    else:
                        alert = Alert(
                            org_id=org.id,
                            rule_name=ad["rule_name"],
                            severity=ad["severity"],
                            description=ad["description"],
                            source_ip=ad["source_ip"],
                            affected_user=ad["affected_user"],
                            first_seen=datetime.now(timezone.utc),
                            last_seen=datetime.now(timezone.utc),
                        )
                        db.add(alert)
                        alert_count += 1
                        await db.flush()
                        await ws_manager.broadcast(
                            str(org.api_key),
                            {
                                "type": "new_alert",
                                "alert": {
                                    "id": str(alert.id),
                                    "rule_name": alert.rule_name,
                                    "severity": alert.severity.value,
                                    "description": alert.description,
                                    "source_ip": alert.source_ip,
                                    "affected_user": alert.affected_user,
                                    "log_count": alert.log_count,
                                    "status": alert.status.value,
                                    "first_seen": alert.first_seen.isoformat(),
                                    "last_seen": alert.last_seen.isoformat(),
                                },
                            }
                        )
            except Exception as e:
                errors.append({"line": line[:100], "error": str(e)})

        await db.commit()
        return {"ingested": parsed_count, "alerts_created": alert_count, "errors": errors}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Invalid API key")

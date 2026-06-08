from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models import LogEntry, Organization
from app.routers.auth_router import get_current_org, DEV_EMAIL

router = APIRouter(prefix="/logs", tags=["logs"])

@router.get("")
async def get_logs(
    severity: str | None = Query(None),
    event_type: str | None = Query(None),
    source_ip: str | None = Query(None),
    search: str | None = Query(None),
    from_ts: str | None = Query(None, alias="from"),
    to_ts: str | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
):
    if org.id == DEV_EMAIL:
        return {"total": 0, "page": page, "per_page": per_page, "logs": []}
    try:
        conditions = [LogEntry.org_id == org.id]
        if severity:
            conditions.append(LogEntry.severity == severity)
        if event_type:
            conditions.append(LogEntry.event_type == event_type)
        if source_ip:
            conditions.append(LogEntry.source_ip == source_ip)
        if search:
            conditions.append(LogEntry.raw_message.ilike(f"%{search}%"))
        if from_ts:
            from datetime import datetime
            conditions.append(LogEntry.timestamp >= datetime.fromisoformat(from_ts.replace("Z", "+00:00")))
        if to_ts:
            from datetime import datetime
            conditions.append(LogEntry.timestamp <= datetime.fromisoformat(to_ts.replace("Z", "+00:00")))

        count_q = select(func.count(LogEntry.id)).where(and_(*conditions))
        total = (await db.execute(count_q)).scalar() or 0

        offset = (page - 1) * per_page
        q = select(LogEntry).where(and_(*conditions)).order_by(LogEntry.timestamp.desc()).offset(offset).limit(per_page)
        rows = (await db.execute(q)).scalars().all()

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "logs": [
                {
                    "id": str(r.id),
                    "timestamp": r.timestamp.isoformat(),
                    "source_ip": r.source_ip,
                    "event_type": r.event_type,
                    "severity": r.severity.value,
                    "raw_message": r.raw_message,
                    "parsed_fields": r.parsed_fields,
                    "hostname": r.hostname,
                    "username": r.username,
                }
                for r in rows
            ],
        }
    except Exception:
        return {"total": 0, "page": page, "per_page": per_page, "logs": []}

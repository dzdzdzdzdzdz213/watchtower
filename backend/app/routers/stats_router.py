from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text, String, Text, cast
from datetime import datetime, timezone, timedelta

from app.database import get_db
from app.models import LogEntry, Alert, Organization, AlertStatus
from app.routers.auth_router import get_current_org, DEV_EMAIL

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
async def get_stats(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
):
    if org.id == DEV_EMAIL:
        return {
            "log_count": 0, "alert_count": 0, "open_alerts": 0, "critical_alerts": 0,
            "severity_breakdown": {}, "timeline": [], "top_source_ips": [], "top_event_types": [],
        }
    try:
        since = datetime.now(timezone.utc) - timedelta(hours=24)

        log_count_q = select(func.count(LogEntry.id)).where(LogEntry.org_id == org.id, LogEntry.timestamp >= since)
        log_count = (await db.execute(log_count_q)).scalar() or 0

        alert_count_q = select(func.count(Alert.id)).where(Alert.org_id == org.id, Alert.last_seen >= since)
        alert_count = (await db.execute(alert_count_q)).scalar() or 0

        open_alerts_q = select(func.count(Alert.id)).where(
            Alert.org_id == org.id, Alert.status == AlertStatus.open, Alert.last_seen >= since
        )
        open_count = (await db.execute(open_alerts_q)).scalar() or 0

        critical_q = select(func.count(Alert.id)).where(
            Alert.org_id == org.id, Alert.severity == "critical",
            Alert.status == AlertStatus.open, Alert.last_seen >= since
        )
        critical_count = (await db.execute(critical_q)).scalar() or 0

        sev_q = select(LogEntry.severity, func.count(LogEntry.id).label("cnt")).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since
        ).group_by(LogEntry.severity)
        sev_rows = (await db.execute(sev_q)).all()
        severity_breakdown = {r.severity: r.cnt for r in sev_rows}

        hourly_q = select(
            func.substr(cast(LogEntry.timestamp, Text), 1, 13).label('hour'),
            LogEntry.severity,
            func.count(LogEntry.id).label('cnt'),
        ).where(LogEntry.org_id == org.id, LogEntry.timestamp >= since
        ).group_by(text('hour'), LogEntry.severity).order_by(text('hour'))
        hourly_rows = (await db.execute(hourly_q)).all()
        timeline = {}
        for r in hourly_rows:
            h = r.hour.isoformat()
            if h not in timeline:
                timeline[h] = {"info": 0, "warning": 0, "critical": 0}
            timeline[h][r.severity] = r.cnt

        top_ips_q = select(LogEntry.source_ip, func.count(LogEntry.id).label("cnt")).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since,
            LogEntry.source_ip.is_not(None), LogEntry.source_ip != "",
        ).group_by(LogEntry.source_ip).order_by(text("cnt desc")).limit(10)
        top_ips = [{"ip": r.source_ip, "count": r.cnt} for r in (await db.execute(top_ips_q)).all()]

        top_events_q = select(LogEntry.event_type, func.count(LogEntry.id).label("cnt")).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since,
            LogEntry.event_type.is_not(None), LogEntry.event_type != "",
        ).group_by(LogEntry.event_type).order_by(text("cnt desc")).limit(5)
        top_events = [{"event_type": r.event_type, "count": r.cnt} for r in (await db.execute(top_events_q)).all()]

        return {
            "log_count": log_count, "alert_count": alert_count, "open_alerts": open_count, "critical_alerts": critical_count,
            "severity_breakdown": severity_breakdown,
            "timeline": [{"hour": h, **v} for h, v in sorted(timeline.items())],
            "top_source_ips": top_ips, "top_event_types": top_events,
        }
    except Exception:
        return {
            "log_count": 0, "alert_count": 0, "open_alerts": 0, "critical_alerts": 0,
            "severity_breakdown": {}, "timeline": [], "top_source_ips": [], "top_event_types": [],
        }

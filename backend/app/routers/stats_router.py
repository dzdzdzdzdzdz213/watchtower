from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from app.database import get_db
from app.models import LogEntry, Alert, Organization, AlertStatus, Severity
from app.routers.auth_router import get_current_org

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("")
async def get_stats(
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
):
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

        sev_q = select(Alert.severity, func.count(Alert.id).label("cnt")).where(
            Alert.org_id == org.id, Alert.status == AlertStatus.open, Alert.last_seen >= since
        ).group_by(Alert.severity)
        sev_rows = (await db.execute(sev_q)).all()
        severity_breakdown = {s.value: 0 for s in Severity}
        for r in sev_rows:
            severity_breakdown[r.severity.value] = r.cnt

        logs_q = select(LogEntry.timestamp, LogEntry.severity).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since,
        ).order_by(LogEntry.timestamp)
        log_rows = (await db.execute(logs_q)).all()
        hourly = defaultdict(lambda: {"critical": 0, "warning": 0, "info": 0})
        for r in log_rows:
            if r.timestamp:
                hour_key = r.timestamp.strftime("%Y-%m-%dT%H:00:00")
                hourly[hour_key][r.severity.value] += 1
        timeline = [{"hour": h, **counts} for h, counts in sorted(hourly.items())]

        top_ips_q = select(LogEntry.source_ip, func.count(LogEntry.id).label("cnt")).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since,
        ).group_by(LogEntry.source_ip).order_by(func.count(LogEntry.id).desc()).limit(10)
        top_ips = [{"ip": r.source_ip, "count": r.cnt} for r in (await db.execute(top_ips_q)).all()]

        top_events_q = select(LogEntry.event_type, func.count(LogEntry.id).label("cnt")).where(
            LogEntry.org_id == org.id, LogEntry.timestamp >= since,
        ).group_by(LogEntry.event_type).order_by(func.count(LogEntry.id).desc()).limit(5)
        top_events = [{"event_type": r.event_type, "count": r.cnt} for r in (await db.execute(top_events_q)).all()]

        return {
            "log_count": log_count, "alert_count": alert_count, "open_alerts": open_count, "critical_alerts": critical_count,
            "severity_breakdown": severity_breakdown,
            "timeline": timeline,
            "top_source_ips": top_ips, "top_event_types": top_events,
        }
    except Exception as e:
        return {
            "log_count": 0, "alert_count": 0, "open_alerts": 0, "critical_alerts": 0,
            "severity_breakdown": {}, "timeline": [], "top_source_ips": [], "top_event_types": [],
            "error": str(e),
        }

import uuid
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.database import get_db
from app.models import Alert, Organization, AlertStatus
from app.routers.auth_router import get_current_org, DEV_EMAIL

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("")
async def get_alerts(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
):
    if org.id == DEV_EMAIL:
        return {"total": 0, "page": page, "per_page": per_page, "alerts": []}
    try:
        conditions = [Alert.org_id == org.id]
        if status and status != "all":
            conditions.append(Alert.status == AlertStatus(status))
        if severity:
            conditions.append(Alert.severity == severity)

        count_q = select(func.count(Alert.id)).where(and_(*conditions))
        total = (await db.execute(count_q)).scalar() or 0

        offset = (page - 1) * per_page
        q = select(Alert).where(and_(*conditions)).order_by(Alert.last_seen.desc()).offset(offset).limit(per_page)
        rows = (await db.execute(q)).scalars().all()

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "alerts": [
                {
                    "id": str(r.id),
                    "rule_name": r.rule_name,
                    "severity": r.severity.value,
                    "description": r.description,
                    "source_ip": r.source_ip,
                    "affected_user": r.affected_user,
                    "log_count": r.log_count,
                    "status": r.status.value,
                    "first_seen": r.first_seen.isoformat(),
                    "last_seen": r.last_seen.isoformat(),
                }
                for r in rows
            ],
        }
    except Exception:
        return {"total": 0, "page": page, "per_page": per_page, "alerts": []}

@router.patch("/{alert_id}")
async def update_alert(
    alert_id: str,
    body: dict,
    org: Organization = Depends(get_current_org),
    db: AsyncSession = Depends(get_db),
):
    if org.id == DEV_EMAIL:
        raise HTTPException(status_code=404, detail="Alert not found")
    try:
        result = await db.execute(
            select(Alert).where(Alert.id == uuid.UUID(alert_id), Alert.org_id == org.id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        new_status = body.get("status")
        if new_status not in ("acknowledged", "resolved"):
            raise HTTPException(status_code=400, detail="Status must be acknowledged or resolved")
        alert.status = AlertStatus(new_status)
        await db.commit()
        return {"status": "ok"}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=404, detail="Alert not found")

"""Alerts API - list, detail, update status, assign, investigate"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog
from app.auth import get_current_user
from app.sse import alert_broadcaster

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


class AlertUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assignee_id: Optional[int] = None
    analyst_notes: Optional[str] = None


@router.get("")
def list_alerts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    per_page: int = Query(None, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|risk_score|severity|status)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    sort_dir: str = Query(None, pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    effective_limit = per_page or limit
    effective_sort = sort_dir or sort_order
    org_id = current_user.organization_id
    query = db.query(Alert).filter(Alert.organization_id == org_id)

    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if search:
        query = query.filter(
            (Alert.title.ilike(f"%{search}%")) |
            (Alert.source_ip.ilike(f"%{search}%")) |
            (Alert.username.ilike(f"%{search}%"))
        )

    total = query.count()

    sort_col = getattr(Alert, sort_by)
    if effective_sort == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    alerts = query.offset((page - 1) * effective_limit).limit(effective_limit).all()

    return {
        "alerts": [a.to_dict() for a in alerts],
        "total": total,
        "page": page,
        "limit": effective_limit,
        "total_pages": (total + effective_limit - 1) // effective_limit,
    }


@router.get("/{alert_id}")
def get_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == current_user.organization_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Get related events
    related_events = []
    if alert.source_ip:
        related_events = db.query(SecurityEvent).filter(
            SecurityEvent.organization_id == current_user.organization_id,
            SecurityEvent.source_ip == alert.source_ip,
        ).order_by(SecurityEvent.created_at.desc()).limit(10).all()

    result = alert.to_dict()
    result["related_events"] = [e.to_dict() for e in related_events]
    return result


@router.patch("/{alert_id}/status")
def update_alert_status(alert_id: int, body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == current_user.organization_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    valid_statuses = {s.value for s in AlertStatus}
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    alert.status = new_status
    if new_status == "acknowledged":
        alert.acknowledged_at = datetime.now(timezone.utc)
    elif new_status == "resolved":
        alert.resolved_at = datetime.now(timezone.utc)
    alert.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)

    # Broadcast status update
    alert_broadcaster.broadcast(current_user.organization_id, "alert_updated", alert.to_dict())

    return alert.to_dict()


@router.post("/{alert_id}/create-incident")
def create_incident_from_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.incident import Incident, IncidentStatus
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == current_user.organization_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    incident = Incident(
        title=f"Incident: {alert.title}",
        description=f"Created from alert #{alert.id}. {alert.description or ''}",
        severity=alert.severity,
        status=IncidentStatus.NEW,
        organization_id=current_user.organization_id,
        assignee_id=current_user.id,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident.to_dict() if hasattr(incident, 'to_dict') else {"id": incident.id, "title": incident.title, "severity": incident.severity.value if incident.severity else "low", "status": incident.status.value if incident.status else "new"}


@router.put("/{alert_id}")
def update_alert(alert_id: int, data: AlertUpdate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == current_user.organization_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    if data.status:
        valid_statuses = {s.value for s in AlertStatus}
        if data.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
        alert.status = data.status
        if data.status == AlertStatus.ACKNOWLEDGED.value:
            alert.acknowledged_at = datetime.now(timezone.utc)
        elif data.status == AlertStatus.RESOLVED.value:
            alert.resolved_at = datetime.now(timezone.utc)

    if data.severity:
        valid_severities = {s.value for s in AlertSeverity}
        if data.severity not in valid_severities:
            raise HTTPException(status_code=400, detail=f"Invalid severity. Must be one of: {valid_severities}")
        alert.severity = data.severity

    if data.assignee_id is not None:
        alert.assignee_id = data.assignee_id

    if data.analyst_notes is not None:
        alert.analyst_notes = data.analyst_notes

    alert.updated_at = datetime.now(timezone.utc)

    audit = AuditLog(
        action="alert_updated",
        resource_type="alert",
        resource_id=alert.id,
        details=f"Updated alert #{alert.id}",
        ip_address=request.client.host if request.client else None,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)

    return alert.to_dict()

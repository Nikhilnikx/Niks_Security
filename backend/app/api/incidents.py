"""Incidents API"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import json
from app.database import get_db
from app.models.user import User
from app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentAlert
from app.models.audit_log import AuditLog
from app.auth import get_current_user

router = APIRouter(prefix="/api/incidents", tags=["incidents"])


class IncidentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    alert_id: Optional[int] = None


class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assignee_id: Optional[int] = None
    notes: Optional[str] = None
    resolution: Optional[str] = None


@router.get("")
def list_incidents(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    per_page: int = Query(None, ge=1, le=100),
    status: Optional[str] = None,
    severity: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    effective_limit = per_page or limit
    org_id = current_user.organization_id
    query = db.query(Incident).filter(Incident.organization_id == org_id)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    if search:
        query = query.filter(Incident.title.ilike(f"%{search}%"))

    total = query.count()
    incidents = query.order_by(Incident.created_at.desc()).offset((page - 1) * effective_limit).limit(effective_limit).all()

    return {
        "incidents": [_incident_to_dict(i) for i in incidents],
        "total": total,
        "page": page,
        "total_pages": (total + effective_limit - 1) // effective_limit,
    }


@router.post("")
def create_incident(data: IncidentCreate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = Incident(
        title=data.title,
        description=data.description,
        severity=data.severity,
        status=IncidentStatus.NEW,
        organization_id=current_user.organization_id,
        timeline=json.dumps([{"event": "Incident created", "timestamp": datetime.now(timezone.utc).isoformat(), "user": current_user.username}]),
    )
    db.add(incident)
    db.flush()

    if data.alert_id:
        link = IncidentAlert(incident_id=incident.id, alert_id=data.alert_id)
        db.add(link)

    audit = AuditLog(
        action="incident_created",
        resource_type="incident",
        resource_id=incident.id,
        details=f"Created incident: {data.title}",
        ip_address=request.client.host if request.client else None,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()
    db.refresh(incident)
    return _incident_to_dict(incident)


@router.get("/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.organization_id == current_user.organization_id,
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _incident_to_dict(incident)


@router.patch("/{incident_id}/status")
def update_incident_status(incident_id: int, body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id, Incident.organization_id == current_user.organization_id,
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    new_status = body.get("status")
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")
    incident.status = new_status
    if new_status == "resolved":
        incident.resolved_at = datetime.now(timezone.utc)
    incident.updated_at = datetime.now(timezone.utc)
    timeline = json.loads(incident.timeline or "[]")
    timeline.append({"event": f"Status changed to {new_status}", "timestamp": datetime.now(timezone.utc).isoformat(), "user": current_user.username})
    incident.timeline = json.dumps(timeline)
    db.commit()
    return _incident_to_dict(incident)


@router.post("/{incident_id}/notes")
def add_incident_note(incident_id: int, body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id, Incident.organization_id == current_user.organization_id,
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    content = body.get("content", "")
    if not content:
        raise HTTPException(status_code=400, detail="Note content is required")
    notes = json.loads(incident.notes or "[]") if isinstance(incident.notes, str) else (incident.notes or [])
    notes.append({"content": content, "author": current_user.username, "created_at": datetime.now(timezone.utc).isoformat()})
    incident.notes = json.dumps(notes)
    incident.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Note added"}


@router.put("/{incident_id}")
def update_incident(incident_id: int, data: IncidentUpdate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    incident = db.query(Incident).filter(
        Incident.id == incident_id,
        Incident.organization_id == current_user.organization_id,
    ).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if data.status:
        incident.status = data.status
        if data.status == IncidentStatus.RESOLVED.value:
            incident.resolved_at = datetime.now(timezone.utc)
    if data.severity:
        incident.severity = data.severity
    if data.assignee_id is not None:
        incident.assignee_id = data.assignee_id
    if data.notes:
        incident.notes = data.notes
    if data.resolution:
        incident.resolution = data.resolution

    # Update timeline
    timeline = json.loads(incident.timeline or "[]")
    timeline.append({
        "event": f"Updated: {', '.join(filter(None, [f'status={data.status}', f'severity={data.severity}']))}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user": current_user.username,
    })
    incident.timeline = json.dumps(timeline)

    audit = AuditLog(
        action="incident_updated",
        resource_type="incident",
        resource_id=incident.id,
        details=f"Updated incident #{incident.id}",
        ip_address=request.client.host if request.client else None,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()
    db.refresh(incident)
    return _incident_to_dict(incident)


def _incident_to_dict(i):
    return {
        "id": i.id,
        "title": i.title,
        "description": i.description,
        "severity": i.severity.value if hasattr(i.severity, 'value') else i.severity,
        "status": i.status.value if hasattr(i.status, 'value') else i.status,
        "assignee_id": i.assignee_id,
        "resolution": i.resolution,
        "timeline": json.loads(i.timeline) if i.timeline else [],
        "notes": i.notes,
        "evidence": i.evidence,
        "created_at": i.created_at.isoformat() if i.created_at else None,
        "updated_at": i.updated_at.isoformat() if i.updated_at else None,
        "resolved_at": i.resolved_at.isoformat() if i.resolved_at else None,
    }

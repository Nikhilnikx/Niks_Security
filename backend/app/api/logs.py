"""Logs API - upload, search, list"""
import os
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.config import get_settings
from app.models.user import User
from app.models.security_event import SecurityEvent
from app.models.asset import Asset
from app.detector.parser import parse_file
from app.detector.risk import calculate_risk_score
from app.detector.rules import run_detection
from app.auth import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])
settings = get_settings()


@router.post("/upload")
async def upload_log(
    file: UploadFile = File(...),
    asset_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    allowed_ext = {"log", "txt", "csv", "json"}
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in allowed_ext:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {', '.join(allowed_ext)}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")

    parsed_entries = parse_file(file.filename, content)
    if not parsed_entries:
        raise HTTPException(status_code=400, detail="No events found in file")

    events = []
    for entry in parsed_entries:
        score, severity = calculate_risk_score(entry.get("event_type", "unknown_event"), entry.get("severity", "low"))
        event = SecurityEvent(
            timestamp=entry.get("timestamp"),
            event_type=entry.get("event_type", "unknown_event"),
            category=entry.get("category", "unknown"),
            description=entry.get("action"),
            source_ip=entry.get("source_ip"),
            destination_ip=entry.get("destination_ip"),
            username=entry.get("username"),
            action=entry.get("action"),
            status=entry.get("status"),
            severity=severity,
            risk_score=score,
            raw_log=entry.get("raw_line"),
            is_flagged=entry.get("parsed", False),
            source_file=file.filename,
            organization_id=org_id,
            user_id=current_user.id,
            asset_id=asset_id,
        )
        db.add(event)
        events.append(event)

    db.flush()

    # Run detection
    alerts = run_detection(org_id, events, db)

    db.commit()

    return {
        "message": f"Uploaded '{file.filename}': {len(events)} events processed",
        "events_count": len(events),
        "alerts_generated": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "title": a.title,
                "severity": a.severity.value if hasattr(a.severity, 'value') else a.severity,
            }
            for a in alerts
        ],
    }


@router.get("")
def list_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    source_ip: Optional[str] = None,
    search: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    query = db.query(SecurityEvent).filter(SecurityEvent.organization_id == org_id)

    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if source_ip:
        query = query.filter(SecurityEvent.source_ip == source_ip)
    if search:
        query = query.filter(
            (SecurityEvent.event_type.ilike(f"%{search}%")) |
            (SecurityEvent.source_ip.ilike(f"%{search}%")) |
            (SecurityEvent.raw_log.ilike(f"%{search}%"))
        )
    if start_date:
        query = query.filter(SecurityEvent.created_at >= start_date)
    if end_date:
        query = query.filter(SecurityEvent.created_at <= end_date)

    total = query.count()
    events = query.order_by(SecurityEvent.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "events": [e.to_dict() for e in events],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }


@router.get("/{event_id}")
def get_log(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(SecurityEvent).filter(
        SecurityEvent.id == event_id,
        SecurityEvent.organization_id == current_user.organization_id,
    ).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event.to_dict()

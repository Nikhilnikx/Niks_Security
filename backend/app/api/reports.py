"""Reports API"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
import json
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.incident import Incident, IncidentStatus
from app.models.security_event import SecurityEvent
from app.models.report import Report
from app.auth import get_current_user

router = APIRouter(prefix="/api/reports", tags=["reports"])


class ReportCreate(BaseModel):
    title: str
    report_type: str  # security_summary, incident, threat, executive, detection


@router.get("")
def list_reports(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reports = db.query(Report).filter(Report.organization_id == current_user.organization_id).order_by(Report.created_at.desc()).all()
    return {"reports": [
        {"id": r.id, "title": r.title, "report_type": r.report_type, "format": r.format, "created_at": r.created_at.isoformat() if r.created_at else None}
        for r in reports
    ]}


@router.post("/generate")
def generate_report_endpoint(data: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _generate_report(data, db, current_user)


@router.post("")
def generate_report(data: ReportCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _generate_report(data, db, current_user)


def _generate_report(data, db, current_user):
    org_id = current_user.organization_id
    now = datetime.now(timezone.utc)

    if data.report_type == "security_summary":
        total_alerts = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id).scalar() or 0
        critical = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.severity == AlertSeverity.CRITICAL).scalar() or 0
        high = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.severity == AlertSeverity.HIGH).scalar() or 0
        total_incidents = db.query(func.count(Incident.id)).filter(Incident.organization_id == org_id).scalar() or 0
        total_events = db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.organization_id == org_id).scalar() or 0
        resolved = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.status == AlertStatus.RESOLVED).scalar() or 0

        content = json.dumps({
            "period": f"Report generated on {now.isoformat()}",
            "summary": {
                "total_alerts": total_alerts,
                "critical_alerts": critical,
                "high_alerts": high,
                "total_incidents": total_incidents,
                "total_events_analyzed": total_events,
                "alerts_resolved": resolved,
                "resolution_rate": round((resolved / max(total_alerts, 1)) * 100, 1),
            },
            "top_alert_types": dict(
                db.query(Alert.mitre_technique, func.count(Alert.id))
                .filter(Alert.organization_id == org_id, Alert.mitre_technique.isnot(None))
                .group_by(Alert.mitre_technique)
                .order_by(func.count(Alert.id).desc()).limit(5).all()
            ),
        })

    elif data.report_type == "incident":
        incidents = db.query(Incident).filter(Incident.organization_id == org_id).order_by(Incident.created_at.desc()).limit(50).all()
        content = json.dumps({
            "report_type": "Incident Report",
            "generated_at": now.isoformat(),
            "incidents": [
                {"id": i.id, "title": i.title, "severity": str(i.severity.value if hasattr(i.severity, 'value') else i.severity), "status": str(i.status.value if hasattr(i.status, 'value') else i.status), "created_at": i.created_at.isoformat() if i.created_at else None}
                for i in incidents
            ],
        })
    else:
        content = json.dumps({"report_type": data.report_type, "generated_at": now.isoformat(), "message": "Report generated"})

    report = Report(title=data.title, report_type=data.report_type, content=content, organization_id=org_id, created_by_id=current_user.id)
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "content": json.loads(report.content),
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id, Report.organization_id == current_user.organization_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"message": "Report deleted"}


@router.get("/{report_id}")
def get_report(report_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    report = db.query(Report).filter(Report.id == report_id, Report.organization_id == current_user.organization_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {
        "id": report.id,
        "title": report.title,
        "report_type": report.report_type,
        "content": json.loads(report.content) if report.content else {},
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }

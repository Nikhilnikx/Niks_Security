"""Dashboard API - summary stats and charts"""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.incident import Incident, IncidentStatus
from app.models.security_event import SecurityEvent
from app.models.asset import Asset
from app.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    org_id = current_user.organization_id
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    prev_week = week_ago - timedelta(days=7)

    # Alert counts by severity
    alert_counts = dict(
        db.query(Alert.severity, func.count(Alert.id))
        .filter(Alert.organization_id == org_id)
        .group_by(Alert.severity)
        .all()
    )

    # This week vs last week alert counts
    this_week_alerts = db.query(func.count(Alert.id)).filter(
        Alert.organization_id == org_id, Alert.created_at >= week_ago
    ).scalar() or 0
    prev_week_alerts = db.query(func.count(Alert.id)).filter(
        Alert.organization_id == org_id, Alert.created_at >= prev_week, Alert.created_at < week_ago
    ).scalar() or 0

    # Active incidents
    active_incidents = db.query(func.count(Incident.id)).filter(
        Incident.organization_id == org_id,
        Incident.status.in_([IncidentStatus.NEW, IncidentStatus.TRIAGED, IncidentStatus.INVESTIGATING])
    ).scalar() or 0

    # Total assets
    total_assets = db.query(func.count(Asset.id)).filter(Asset.organization_id == org_id).scalar() or 0

    # Security events today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    events_today = db.query(func.count(SecurityEvent.id)).filter(
        SecurityEvent.organization_id == org_id,
        SecurityEvent.created_at >= today_start
    ).scalar() or 0

    # Recent alerts
    recent_alerts = db.query(Alert).filter(Alert.organization_id == org_id).order_by(Alert.created_at.desc()).limit(10).all()

    # Alerts over time (last 7 days)
    alerts_over_time = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day, datetime.min.time()).replace(tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)
        count = db.query(func.count(Alert.id)).filter(
            Alert.organization_id == org_id,
            Alert.created_at >= day_start,
            Alert.created_at < day_end,
        ).scalar() or 0
        alerts_over_time.append({"date": day.isoformat(), "count": count})

    # Top threat types
    threat_types = dict(
        db.query(SecurityEvent.event_type, func.count(SecurityEvent.id))
        .filter(SecurityEvent.organization_id == org_id)
        .group_by(SecurityEvent.event_type)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(5)
        .all()
    )

    # Top attacking IPs
    top_ips = dict(
        db.query(SecurityEvent.source_ip, func.count(SecurityEvent.id))
        .filter(SecurityEvent.organization_id == org_id, SecurityEvent.source_ip.isnot(None))
        .group_by(SecurityEvent.source_ip)
        .order_by(func.count(SecurityEvent.id).desc())
        .limit(5)
        .all()
    )

    # Severity distribution
    severity_dist = dict(
        db.query(SecurityEvent.severity, func.count(SecurityEvent.id))
        .filter(SecurityEvent.organization_id == org_id)
        .group_by(SecurityEvent.severity)
        .all()
    )

    total_alerts = sum(alert_counts.values())
    critical = alert_counts.get("critical", 0)
    high = alert_counts.get("high", 0)

    # Security score calculation
    score = 100
    score -= min(30, critical * 5)
    score -= min(20, high * 3)
    score -= min(10, active_incidents * 2)
    score = max(0, min(100, score))

    return {
        "security_score": score,
        "critical_alerts": critical,
        "high_alerts": high,
        "medium_alerts": alert_counts.get("medium", 0),
        "low_alerts": alert_counts.get("low", 0),
        "total_alerts": total_alerts,
        "active_incidents": active_incidents,
        "total_assets": total_assets,
        "events_today": events_today,
        "alerts_trend": {
            "this_week": this_week_alerts,
            "last_week": prev_week_alerts,
            "change_pct": round(((this_week_alerts - prev_week_alerts) / max(prev_week_alerts, 1)) * 100),
        },
        "recent_alerts": [a.to_dict() for a in recent_alerts],
        "alerts_over_time": alerts_over_time,
        "top_threats": [{"name": k, "count": v} for k, v in threat_types.items()],
        "top_ips": [{"ip": k, "count": v} for k, v in top_ips.items()],
        "severity_distribution": severity_dist,
    }

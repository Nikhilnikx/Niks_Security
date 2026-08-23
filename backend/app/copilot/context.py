"""Context builder - assembles security data for the AI copilot."""
import json
from typing import Optional
from app.copilot.sanitizer import sanitize_dict


def build_alert_context(db, org_id: int, alert_id: int) -> dict:
    """Build full investigation context for an alert."""
    from app.models.alert import Alert
    from app.models.security_event import SecurityEvent
    from app.models.detection_rule import DetectionRule
    from app.models.threat_indicator import ThreatIndicator

    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == org_id).first()
    if not alert:
        return {"error": f"Alert #{alert_id} not found"}

    context = {"alert": sanitize_dict(alert.to_dict())}

    # Related events
    if alert.source_ip:
        events = db.query(SecurityEvent).filter(
            SecurityEvent.organization_id == org_id,
            SecurityEvent.source_ip == alert.source_ip,
        ).order_by(SecurityEvent.created_at.desc()).limit(20).all()
        context["related_events"] = [sanitize_dict(e.to_dict()) for e in events]

        # Related alerts
        related_alerts = db.query(Alert).filter(
            Alert.organization_id == org_id,
            Alert.source_ip == alert.source_ip,
            Alert.id != alert.id,
        ).order_by(Alert.created_at.desc()).limit(10).all()
        context["related_alerts"] = [sanitize_dict(a.to_dict()) for a in related_alerts]

        # Threat intelligence
        ioc = db.query(ThreatIndicator).filter(
            ThreatIndicator.organization_id == org_id,
            ThreatIndicator.indicator_type == "ip",
            ThreatIndicator.value == alert.source_ip,
        ).first()
        if ioc:
            context["threat_intelligence"] = sanitize_dict(ioc.to_dict())

    # Detection rule
    if alert.detection_rule_id:
        rule = db.query(DetectionRule).filter(DetectionRule.id == alert.detection_rule_id).first()
        if rule:
            context["detection_rule"] = sanitize_dict(rule.to_dict())

    return context


def build_incident_context(db, org_id: int, incident_id: int) -> dict:
    """Build full investigation context for an incident."""
    from app.models.incident import Incident, IncidentAlert
    from app.models.alert import Alert
    from app.models.security_event import SecurityEvent
    from app.models.threat_indicator import ThreatIndicator

    incident = db.query(Incident).filter(
        Incident.id == incident_id, Incident.organization_id == org_id
    ).first()
    if not incident:
        return {"error": f"Incident #{incident_id} not found"}

    iocs = json.loads(incident.iocs) if incident.iocs else []
    timeline = json.loads(incident.timeline) if incident.timeline else []

    context = {
        "incident": {
            "id": incident.id,
            "title": incident.title,
            "description": incident.description,
            "severity": incident.severity.value if incident.severity else "low",
            "status": incident.status.value if incident.status else "new",
            "evidence": incident.evidence,
            "notes": incident.notes,
            "iocs": iocs,
            "timeline": timeline,
            "resolution": incident.resolution,
            "created_at": incident.created_at.isoformat() if incident.created_at else None,
        }
    }

    # Linked alerts
    linked = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
    linked_alerts = []
    source_ips = set()
    for la in linked:
        alert = db.query(Alert).filter(Alert.id == la.alert_id).first()
        if alert:
            linked_alerts.append(sanitize_dict(alert.to_dict()))
            if alert.source_ip:
                source_ips.add(alert.source_ip)
    context["linked_alerts"] = linked_alerts

    # Related events from source IPs
    if source_ips:
        events = db.query(SecurityEvent).filter(
            SecurityEvent.organization_id == org_id,
            SecurityEvent.source_ip.in_(list(source_ips)),
        ).order_by(SecurityEvent.created_at.desc()).limit(30).all()
        context["related_events"] = [sanitize_dict(e.to_dict()) for e in events]

    return context


def build_dashboard_context(db, org_id: int) -> dict:
    """Build dashboard summary context for copilot questions."""
    from sqlalchemy import func
    from app.models.alert import Alert, AlertSeverity
    from app.models.incident import Incident
    from app.models.security_event import SecurityEvent
    from app.models.asset import Asset

    return {
        "total_alerts": db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id).scalar() or 0,
        "critical_alerts": db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.severity == AlertSeverity.CRITICAL).scalar() or 0,
        "high_alerts": db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.severity == AlertSeverity.HIGH).scalar() or 0,
        "total_incidents": db.query(func.count(Incident.id)).filter(Incident.organization_id == org_id).scalar() or 0,
        "total_events": db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.organization_id == org_id).scalar() or 0,
        "total_assets": db.query(func.count(Asset.id)).filter(Asset.organization_id == org_id).scalar() or 0,
    }


def build_ip_context(db, org_id: int, ip_address: str) -> dict:
    """Build investigation context for an IP address."""
    from app.models.security_event import SecurityEvent
    from app.models.alert import Alert
    from app.models.threat_indicator import ThreatIndicator

    context = {"ip_address": ip_address}

    # Threat intel
    ioc = db.query(ThreatIndicator).filter(
        ThreatIndicator.organization_id == org_id,
        ThreatIndicator.indicator_type == "ip",
        ThreatIndicator.value == ip_address,
    ).first()
    if ioc:
        context["threat_intelligence"] = sanitize_dict(ioc.to_dict())

    # Alerts
    alerts = db.query(Alert).filter(
        Alert.organization_id == org_id,
        Alert.source_ip == ip_address,
    ).order_by(Alert.created_at.desc()).limit(20).all()
    context["alerts"] = [sanitize_dict(a.to_dict()) for a in alerts]

    # Events
    events = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == org_id,
        SecurityEvent.source_ip == ip_address,
    ).order_by(SecurityEvent.created_at.desc()).limit(20).all()
    context["events"] = [sanitize_dict(e.to_dict()) for e in events]

    return context

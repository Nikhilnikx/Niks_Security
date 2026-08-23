"""Incident investigation tools for the AI Copilot."""
from app.copilot.tools.registry import register_tool
from app.copilot.sanitizer import sanitize_dict


@register_tool(
    name="get_incident",
    description="Retrieve incident details including timeline, IOCs, evidence, and linked alerts.",
    parameters={"incident_id": {"type": "integer", "description": "Incident ID"}},
)
def get_incident(db, org_id: int, incident_id: int = 0, **kwargs):
    from app.models.incident import Incident, IncidentAlert
    incident = db.query(Incident).filter(
        Incident.id == incident_id, Incident.organization_id == org_id
    ).first()
    if not incident:
        return {"error": "Incident not found"}

    # Get linked alerts
    linked = db.query(IncidentAlert).filter(IncidentAlert.incident_id == incident_id).all()
    from app.models.alert import Alert
    linked_alerts = []
    for la in linked:
        alert = db.query(Alert).filter(Alert.id == la.alert_id).first()
        if alert:
            linked_alerts.append(sanitize_dict(alert.to_dict()))

    import json
    return {
        "id": incident.id,
        "title": incident.title,
        "description": incident.description,
        "severity": incident.severity.value if incident.severity else "low",
        "status": incident.status.value if incident.status else "new",
        "evidence": incident.evidence,
        "notes": incident.notes,
        "iocs": json.loads(incident.iocs) if incident.iocs else [],
        "timeline": json.loads(incident.timeline) if incident.timeline else [],
        "resolution": incident.resolution,
        "linked_alerts": linked_alerts,
        "created_at": incident.created_at.isoformat() if incident.created_at else None,
    }


@register_tool(
    name="search_incidents",
    description="Search incidents by severity, status, or keyword.",
    parameters={
        "severity": {"type": "string", "description": "Filter: critical, high, medium, low"},
        "status": {"type": "string", "description": "Filter: new, triaged, investigating, contained, resolved"},
        "search": {"type": "string", "description": "Search in title/description"},
        "limit": {"type": "integer", "description": "Max results (default 10)"},
    },
)
def search_incidents(db, org_id: int, severity: str = None, status: str = None,
                     search: str = None, limit: int = 10, **kwargs):
    from app.models.incident import Incident
    query = db.query(Incident).filter(Incident.organization_id == org_id)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if search:
        query = query.filter(
            (Incident.title.ilike(f"%{search}%")) | (Incident.description.ilike(f"%{search}%"))
        )
    incidents = query.order_by(Incident.created_at.desc()).limit(limit).all()
    return {
        "incidents": [{
            "id": i.id, "title": i.title,
            "severity": i.severity.value if i.severity else "low",
            "status": i.status.value if i.status else "new",
            "created_at": i.created_at.isoformat() if i.created_at else None,
        } for i in incidents],
        "total": query.count(),
    }

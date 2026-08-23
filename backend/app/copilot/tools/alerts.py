"""Alert investigation tools for the AI Copilot."""
from typing import Optional
from app.copilot.tools.registry import register_tool
from app.copilot.sanitizer import sanitize_dict


@register_tool(
    name="get_alert",
    description="Retrieve details of a specific alert by ID. Returns alert metadata, severity, IPs, MITRE technique, and evidence.",
    parameters={"alert_id": {"type": "integer", "description": "Alert ID"}},
)
def get_alert(db, org_id: int, alert_id: int = 0, **kwargs):
    from app.models.alert import Alert
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.organization_id == org_id).first()
    if not alert:
        return {"error": "Alert not found"}
    return sanitize_dict(alert.to_dict())


@register_tool(
    name="search_alerts",
    description="Search alerts by severity, status, source_ip, or keyword. Returns matching alerts with pagination.",
    parameters={
        "severity": {"type": "string", "description": "Filter: critical, high, medium, low"},
        "status": {"type": "string", "description": "Filter: new, acknowledged, investigating, resolved"},
        "source_ip": {"type": "string", "description": "Filter by source IP address"},
        "search": {"type": "string", "description": "Search keyword in title/description"},
        "limit": {"type": "integer", "description": "Max results (default 10)"},
    },
)
def search_alerts(db, org_id: int, severity: str = None, status: str = None,
                  source_ip: str = None, search: str = None, limit: int = 10, **kwargs):
    from app.models.alert import Alert
    query = db.query(Alert).filter(Alert.organization_id == org_id)
    if severity:
        query = query.filter(Alert.severity == severity)
    if status:
        query = query.filter(Alert.status == status)
    if source_ip:
        query = query.filter(Alert.source_ip == source_ip)
    if search:
        query = query.filter(
            (Alert.title.ilike(f"%{search}%")) | (Alert.description.ilike(f"%{search}%"))
        )
    alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
    return {"alerts": [sanitize_dict(a.to_dict()) for a in alerts], "total": query.count()}

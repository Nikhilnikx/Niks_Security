"""Log and security event tools for the AI Copilot."""
from app.copilot.tools.registry import register_tool
from app.copilot.sanitizer import sanitize_dict


@register_tool(
    name="search_logs",
    description="Search security events/logs by event_type, source_ip, severity, username, or keyword. Returns matching events.",
    parameters={
        "event_type": {"type": "string", "description": "Filter by event type (e.g. failed_login, port_scan)"},
        "source_ip": {"type": "string", "description": "Filter by source IP"},
        "severity": {"type": "string", "description": "Filter by severity"},
        "username": {"type": "string", "description": "Filter by username"},
        "search": {"type": "string", "description": "Free-text search in event descriptions"},
        "limit": {"type": "integer", "description": "Max results (default 10)"},
    },
)
def search_logs(db, org_id: int, event_type: str = None, source_ip: str = None,
                severity: str = None, username: str = None, search: str = None,
                limit: int = 10, **kwargs):
    from app.models.security_event import SecurityEvent
    query = db.query(SecurityEvent).filter(SecurityEvent.organization_id == org_id)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if source_ip:
        query = query.filter(SecurityEvent.source_ip == source_ip)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if username:
        query = query.filter(SecurityEvent.username == username)
    if search:
        query = query.filter(
            (SecurityEvent.event_type.ilike(f"%{search}%")) |
            (SecurityEvent.description.ilike(f"%{search}%")) |
            (SecurityEvent.source_ip.ilike(f"%{search}%"))
        )
    events = query.order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    return {"events": [sanitize_dict(e.to_dict()) for e in events], "total": query.count()}


@register_tool(
    name="get_related_events",
    description="Find security events related to a specific source IP address. Useful for investigating attacker activity.",
    parameters={
        "source_ip": {"type": "string", "description": "Source IP to investigate"},
        "limit": {"type": "integer", "description": "Max results (default 20)"},
    },
)
def get_related_events(db, org_id: int, source_ip: str = "", limit: int = 20, **kwargs):
    from app.models.security_event import SecurityEvent
    if not source_ip:
        return {"error": "source_ip is required"}
    events = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == org_id,
        SecurityEvent.source_ip == source_ip,
    ).order_by(SecurityEvent.created_at.desc()).limit(limit).all()
    return {"events": [sanitize_dict(e.to_dict()) for e in events], "count": len(events)}

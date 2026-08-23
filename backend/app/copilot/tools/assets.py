"""Asset, threat intel, and MITRE tools for the AI Copilot."""
from app.copilot.tools.registry import register_tool
from app.copilot.sanitizer import sanitize_dict


@register_tool(
    name="get_asset",
    description="Retrieve asset details including type, IP, hostname, OS, risk level, and recent alerts.",
    parameters={"asset_id": {"type": "integer", "description": "Asset ID"}},
)
def get_asset(db, org_id: int, asset_id: int = 0, **kwargs):
    from app.models.asset import Asset
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == org_id).first()
    if not asset:
        return {"error": "Asset not found"}
    return {
        "id": asset.id, "name": asset.name,
        "type": asset.asset_type.value if asset.asset_type else "unknown",
        "ip_address": asset.ip_address, "hostname": asset.hostname,
        "status": asset.status.value if asset.status else "active",
        "risk_level": asset.risk_level, "os_info": asset.os_info,
    }


@register_tool(
    name="search_iocs",
    description="Search threat indicators (IOCs) by type, value, severity, or reputation.",
    parameters={
        "indicator_type": {"type": "string", "description": "Filter: ip, domain, url, hash"},
        "value": {"type": "string", "description": "Search IOC value"},
        "severity": {"type": "string", "description": "Filter by severity"},
        "limit": {"type": "integer", "description": "Max results (default 10)"},
    },
)
def search_iocs(db, org_id: int, indicator_type: str = None, value: str = None,
                severity: str = None, limit: int = 10, **kwargs):
    from app.models.threat_indicator import ThreatIndicator
    query = db.query(ThreatIndicator).filter(ThreatIndicator.organization_id == org_id, ThreatIndicator.is_active == True)
    if indicator_type:
        query = query.filter(ThreatIndicator.indicator_type == indicator_type)
    if value:
        query = query.filter(ThreatIndicator.value.ilike(f"%{value}%"))
    if severity:
        query = query.filter(ThreatIndicator.severity == severity)
    iocs = query.order_by(ThreatIndicator.created_at.desc()).limit(limit).all()
    return {"iocs": [sanitize_dict(i.to_dict()) for i in iocs], "total": query.count()}


@register_tool(
    name="get_ip_reputation",
    description="Look up threat intelligence for an IP address. Returns reputation, geolocation, ASN, and detection history.",
    parameters={"ip_address": {"type": "string", "description": "IP address to look up"}},
)
def get_ip_reputation(db, org_id: int, ip_address: str = "", **kwargs):
    from app.models.threat_indicator import ThreatIndicator
    if not ip_address:
        return {"error": "ip_address is required"}
    indicator = db.query(ThreatIndicator).filter(
        ThreatIndicator.organization_id == org_id,
        ThreatIndicator.indicator_type == "ip",
        ThreatIndicator.value == ip_address,
    ).first()
    if not indicator:
        return {"value": ip_address, "reputation": "unknown", "message": "No threat intelligence available for this IP"}
    return sanitize_dict(indicator.to_dict())


@register_tool(
    name="get_mitre_technique",
    description="Get details of a MITRE ATT&CK technique including name, tactic, and description.",
    parameters={"technique_id": {"type": "string", "description": "MITRE technique ID (e.g. T1110)"}},
)
def get_mitre_technique(db, org_id: int, technique_id: str = "", **kwargs):
    from app.api.mitre import MITRE_TECHNIQUES
    if not technique_id:
        return {"error": "technique_id is required"}
    # Normalize: try exact match, then parent technique
    tech = MITRE_TECHNIQUES.get(technique_id)
    if not tech and "." in technique_id:
        parent = technique_id.split(".")[0]
        tech = MITRE_TECHNIQUES.get(parent)
    if not tech:
        return {"technique_id": technique_id, "message": "Technique not found in platform database"}
    # Count detections for this technique
    from app.models.alert import Alert
    count = db.query(Alert).filter(
        Alert.organization_id == org_id, Alert.mitre_technique == technique_id
    ).count()
    return {"technique_id": technique_id, **tech, "detection_count": count}


@register_tool(
    name="get_detection_rule",
    description="Get details of a detection rule including conditions, severity, and MITRE mapping.",
    parameters={"rule_id": {"type": "integer", "description": "Detection rule ID"}},
)
def get_detection_rule(db, org_id: int, rule_id: int = 0, **kwargs):
    from app.models.detection_rule import DetectionRule
    rule = db.query(DetectionRule).filter(
        DetectionRule.id == rule_id, DetectionRule.organization_id == org_id
    ).first()
    if not rule:
        return {"error": "Detection rule not found"}
    return sanitize_dict(rule.to_dict())


@register_tool(
    name="get_user_activity",
    description="Find all security events and alerts for a specific username.",
    parameters={
        "username": {"type": "string", "description": "Username to investigate"},
        "limit": {"type": "integer", "description": "Max results (default 10)"},
    },
)
def get_user_activity(db, org_id: int, username: str = "", limit: int = 10, **kwargs):
    from app.models.security_event import SecurityEvent
    from app.models.alert import Alert
    if not username:
        return {"error": "username is required"}

    events = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == org_id,
        SecurityEvent.username == username,
    ).order_by(SecurityEvent.created_at.desc()).limit(limit).all()

    alerts = db.query(Alert).filter(
        Alert.organization_id == org_id,
        Alert.username == username,
    ).order_by(Alert.created_at.desc()).limit(limit).all()

    return {
        "username": username,
        "events": [sanitize_dict(e.to_dict()) for e in events],
        "alerts": [sanitize_dict(a.to_dict()) for a in alerts],
    }


@register_tool(
    name="get_attack_timeline",
    description="Build an attack timeline for a source IP by combining alerts and security events chronologically.",
    parameters={
        "source_ip": {"type": "string", "description": "Source IP to build timeline for"},
        "limit": {"type": "integer", "description": "Max events (default 30)"},
    },
)
def get_attack_timeline(db, org_id: int, source_ip: str = "", limit: int = 30, **kwargs):
    from app.models.security_event import SecurityEvent
    from app.models.alert import Alert
    if not source_ip:
        return {"error": "source_ip is required"}

    events = db.query(SecurityEvent).filter(
        SecurityEvent.organization_id == org_id,
        SecurityEvent.source_ip == source_ip,
    ).order_by(SecurityEvent.created_at.asc()).limit(limit).all()

    alerts = db.query(Alert).filter(
        Alert.organization_id == org_id,
        Alert.source_ip == source_ip,
    ).order_by(Alert.created_at.asc()).limit(limit).all()

    timeline = []
    for e in events:
        timeline.append({
            "type": "event",
            "timestamp": e.created_at.isoformat() if e.created_at else None,
            "event_type": e.event_type,
            "severity": e.severity,
            "description": e.description or e.event_type,
            "action": e.action,
        })
    for a in alerts:
        timeline.append({
            "type": "alert",
            "timestamp": a.created_at.isoformat() if a.created_at else None,
            "title": a.title,
            "severity": a.severity.value if a.severity else "low",
            "mitre_technique": a.mitre_technique,
        })

    timeline.sort(key=lambda x: x.get("timestamp") or "", reverse=False)
    return {"source_ip": source_ip, "timeline": timeline[:limit]}

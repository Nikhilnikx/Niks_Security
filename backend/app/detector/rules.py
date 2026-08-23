"""
Detection rules engine - threshold-based and pattern-based detection.
"""
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.security_event import SecurityEvent
from app.models.detection_rule import DetectionRule
from app.models.alert import Alert, AlertSeverity, AlertStatus


# Default detection rules shipped with the platform
DEFAULT_RULES = [
    {
        "name": "SSH Brute Force",
        "description": "Detects multiple failed SSH login attempts from the same IP within a time window",
        "rule_type": "threshold",
        "severity": "high",
        "mitre_technique": "T1110",
        "mitre_tactic": "Credential Access",
        "conditions": '{"event_type": "failed_login", "threshold": 5, "window_minutes": 10, "group_by": "source_ip"}',
    },
    {
        "name": "Port Scanning",
        "description": "Detects port scanning activity from a single source",
        "rule_type": "threshold",
        "severity": "medium",
        "mitre_technique": "T1046",
        "mitre_tactic": "Discovery",
        "conditions": '{"event_type": "port_scan", "threshold": 15, "window_minutes": 5, "group_by": "source_ip"}',
    },
    {
        "name": "SQL Injection Attempt",
        "description": "Detects SQL injection patterns in web requests",
        "rule_type": "pattern",
        "severity": "critical",
        "mitre_technique": "T1190",
        "mitre_tactic": "Initial Access",
        "conditions": '{"event_type": "sql_injection", "patterns": ["union select", "insert into", "drop table", "or 1=1"]}',
    },
    {
        "name": "XSS Attack",
        "description": "Detects cross-site scripting patterns",
        "rule_type": "pattern",
        "severity": "high",
        "mitre_technique": "T1189",
        "mitre_tactic": "Initial Access",
        "conditions": '{"event_type": "xss_attack", "patterns": ["<script", "javascript:", "onerror=", "onload="]}',
    },
    {
        "name": "Command Injection",
        "description": "Detects command injection attempts",
        "rule_type": "pattern",
        "severity": "critical",
        "mitre_technique": "T1059",
        "mitre_tactic": "Execution",
        "conditions": '{"event_type": "command_injection", "patterns": ["; ls", "| cat", "&& rm", "$("]}',
    },
    {
        "name": "Suspicious Authentication",
        "description": "Detects authentication from unusual locations or at unusual times",
        "rule_type": "anomaly",
        "severity": "medium",
        "mitre_technique": "T1078",
        "mitre_tactic": "Initial Access",
        "conditions": '{"event_type": "successful_login", "unusual_hours": true}',
    },
    {
        "name": "Malware Indicator",
        "description": "Detects known malware indicators in system events",
        "rule_type": "pattern",
        "severity": "critical",
        "mitre_technique": "T1059",
        "mitre_tactic": "Execution",
        "conditions": '{"event_type": "malware", "patterns": ["trojan", "ransomware", "backdoor", "keylogger"]}',
    },
    {
        "name": "Privilege Escalation",
        "description": "Detects privilege escalation attempts",
        "rule_type": "pattern",
        "severity": "high",
        "mitre_technique": "T1068",
        "mitre_tactic": "Privilege Escalation",
        "conditions": '{"event_type": "privilege_escalation", "patterns": ["sudo", "setuid", "runas"]}',
    },
    {
        "name": "DDoS Attack",
        "description": "Detects potential DDoS activity from high request volumes",
        "rule_type": "threshold",
        "severity": "critical",
        "mitre_technique": "T1498",
        "mitre_tactic": "Impact",
        "conditions": '{"event_type": "high_volume_requests", "threshold": 100, "window_seconds": 60, "group_by": "source_ip"}',
    },
    {
        "name": "Failed Login Lockout",
        "description": "Detects account lockout after multiple failed attempts",
        "rule_type": "threshold",
        "severity": "high",
        "mitre_technique": "T1110.003",
        "mitre_tactic": "Credential Access",
        "conditions": '{"event_type": "failed_login", "threshold": 10, "window_minutes": 5, "group_by": "username"}',
    },
]


def run_threshold_rule(rule, events, db):
    """Run a threshold-based detection rule against events."""
    import json
    conditions = json.loads(rule.conditions) if rule.conditions else {}
    event_type = conditions.get("event_type", "failed_login")
    threshold = conditions.get("threshold", 5)
    window_minutes = conditions.get("window_minutes", 10)
    group_by = conditions.get("group_by", "source_ip")

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(minutes=window_minutes)

    # Query recent events matching the type
    query = db.query(SecurityEvent).filter(
        SecurityEvent.event_type == event_type,
        SecurityEvent.created_at >= window_start,
        SecurityEvent.organization_id == rule.organization_id,
    )

    recent_events = query.all()

    # Group and count
    groups = defaultdict(list)
    for event in recent_events:
        key = getattr(event, group_by, None) or "unknown"
        groups[key].append(event)

    alerts_created = []
    for key, event_list in groups.items():
        if len(event_list) >= threshold:
            severity_map = {"critical": AlertSeverity.CRITICAL, "high": AlertSeverity.HIGH, "medium": AlertSeverity.MEDIUM, "low": AlertSeverity.LOW}
            alert = Alert(
                title=f"{rule.name} detected",
                description=f"{rule.name}: {len(event_list)} events from {group_by}={key} within {window_minutes} minutes",
                severity=severity_map.get(rule.severity, AlertSeverity.MEDIUM),
                status=AlertStatus.NEW,
                risk_score=min(100, len(event_list) * 10 + 50),
                confidence=min(100, len(event_list) * 8 + 30),
                source_ip=key if group_by == "source_ip" else None,
                username=key if group_by == "username" else None,
                mitre_technique=rule.mitre_technique,
                mitre_tactic=rule.mitre_tactic,
                evidence=f"Matched rule '{rule.name}': {len(event_list)} events",
                recommended_actions=f"Investigate {group_by}={key}. Review related logs and consider blocking if malicious.",
                organization_id=rule.organization_id,
                event_id=event_list[0].id,
                detection_rule_id=rule.id,
            )
            db.add(alert)
            alerts_created.append(alert)

    return alerts_created


def run_pattern_rule(rule, events, db):
    """Run pattern-based detection against events."""
    import json
    conditions = json.loads(rule.conditions) if rule.conditions else {}
    patterns = conditions.get("patterns", [])
    
    alerts_created = []
    for event in events:
        if not event.raw_log:
            continue
        raw_lower = event.raw_log.lower()
        matched_patterns = [p for p in patterns if p.lower() in raw_lower]
        if matched_patterns:
            severity_map = {"critical": AlertSeverity.CRITICAL, "high": AlertSeverity.HIGH, "medium": AlertSeverity.MEDIUM, "low": AlertSeverity.LOW}
            alert = Alert(
                title=f"{rule.name} detected",
                description=f"Pattern match: {', '.join(matched_patterns)}",
                severity=severity_map.get(rule.severity, AlertSeverity.MEDIUM),
                status=AlertStatus.NEW,
                risk_score=85 if rule.severity == "critical" else 65,
                confidence=90,
                source_ip=event.source_ip,
                mitre_technique=rule.mitre_technique,
                mitre_tactic=rule.mitre_tactic,
                evidence=f"Matched patterns: {', '.join(matched_patterns)}",
                recommended_actions=f"Investigate source IP {event.source_ip}. Review full request logs.",
                organization_id=rule.organization_id,
                event_id=event.id,
                detection_rule_id=rule.id,
            )
            db.add(alert)
            alerts_created.append(alert)
            event.is_flagged = True
            event.risk_score = max(event.risk_score, 85)
            event.severity = "critical" if rule.severity == "critical" else "high"

    return alerts_created


def run_detection(org_id, events, db):
    """Run all enabled detection rules for an organization."""
    rules = db.query(DetectionRule).filter(
        DetectionRule.organization_id == org_id,
        DetectionRule.enabled == True,
    ).all()

    all_alerts = []
    for rule in rules:
        if rule.rule_type == "threshold":
            alerts = run_threshold_rule(rule, events, db)
        elif rule.rule_type == "pattern":
            alerts = run_pattern_rule(rule, events, db)
        else:
            continue
        all_alerts.extend(alerts)
        if alerts:
            rule.last_triggered_at = datetime.now(timezone.utc)

    return all_alerts

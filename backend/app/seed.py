"""Seed database with realistic demo data for first-time setup."""
import random
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.organization import Organization, PlanType
from app.models.asset import Asset
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.incident import Incident, IncidentStatus
from app.models.security_event import SecurityEvent
from app.models.detection_rule import DetectionRule
from app.models.notification import Notification
from app.auth import hash_password


def seed_database(db: Session):
    """Seed the database with demo data if empty."""
    if db.query(User).count() > 0:
        return False

    now = datetime.now(timezone.utc)

    # Create demo organization
    org = Organization(
        name="Demo Security Operations",
        slug="demo-soc",
        description="Demo organization for Niks Security platform",
        plan=PlanType.PRO,
        max_users=50,
        max_assets=500,
        max_events_per_day=1000000,
    )
    db.add(org)
    db.flush()

    # Create demo user
    user = User(
        username="admin",
        email="admin@niks.security",
        password_hash=hash_password("Admin123!"),
        full_name="SOC Administrator",
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
        organization_id=org.id,
    )
    db.add(user)
    db.flush()

    # Create demo assets
    assets_data = [
        {"name": "Web Server 01", "asset_type": "server", "ip_address": "10.0.1.10", "hostname": "web01.prod"},
        {"name": "Web Server 02", "asset_type": "server", "ip_address": "10.0.1.11", "hostname": "web02.prod"},
        {"name": "API Gateway", "asset_type": "server", "ip_address": "10.0.1.20", "hostname": "api.prod"},
        {"name": "Database Primary", "asset_type": "database", "ip_address": "10.0.2.10", "hostname": "db01.prod"},
        {"name": "Database Replica", "asset_type": "database", "ip_address": "10.0.2.11", "hostname": "db02.prod"},
        {"name": "Auth Service", "asset_type": "application", "ip_address": "10.0.3.10", "hostname": "auth.prod"},
        {"name": "SOC Analyst Workstation", "asset_type": "endpoint", "ip_address": "10.0.5.100", "hostname": "soc-ws01"},
        {"name": "Firewall", "asset_type": "network_device", "ip_address": "10.0.0.1", "hostname": "fw01"},
        {"name": "Load Balancer", "asset_type": "network_device", "ip_address": "10.0.0.5", "hostname": "lb01"},
        {"name": "Monitoring Server", "asset_type": "server", "ip_address": "10.0.4.10", "hostname": "monitor.prod"},
    ]
    assets = []
    for a in assets_data:
        asset = Asset(**a, organization_id=org.id, owner_id=user.id, status="active")
        db.add(asset)
        assets.append(asset)
    db.flush()

    # Create demo detection rules
    rules_data = [
        {"name": "SSH Brute Force", "description": "Detects brute-force SSH login attempts", "severity": "high", "rule_type": "threshold", "conditions": "failed_logins > 5 FROM same_ip WITHIN 10m", "mitre_technique": "T1110", "mitre_tactic": "Credential Access", "enabled": True, "threat_type": "brute_force"},
        {"name": "Port Scanning", "description": "Detects port scanning activity", "severity": "medium", "rule_type": "threshold", "conditions": "port_connections > 15 FROM same_ip WITHIN 5m", "mitre_technique": "T1046", "mitre_tactic": "Discovery", "enabled": True, "threat_type": "port_scan"},
        {"name": "SQL Injection", "description": "Detects SQL injection patterns in web requests", "severity": "critical", "rule_type": "pattern", "conditions": "payload MATCHES 'sql_injection_patterns'", "mitre_technique": "T1190", "mitre_tactic": "Initial Access", "enabled": True, "threat_type": "sql_injection"},
        {"name": "XSS Attack", "description": "Detects cross-site scripting payloads", "severity": "medium", "rule_type": "pattern", "conditions": "payload MATCHES 'xss_patterns'", "mitre_technique": "T1189", "mitre_tactic": "Initial Access", "enabled": True, "threat_type": "xss"},
        {"name": "Command Injection", "description": "Detects OS command injection attempts", "severity": "critical", "rule_type": "pattern", "conditions": "payload MATCHES 'command_injection_patterns'", "mitre_technique": "T1059", "mitre_tactic": "Execution", "enabled": True, "threat_type": "command_injection"},
        {"name": "Suspicious Authentication", "description": "Detects unusual login patterns", "severity": "high", "rule_type": "anomaly", "conditions": "login FROM unusual_location OR unusual_time", "mitre_technique": "T1078", "mitre_tactic": "Initial Access", "enabled": True, "threat_type": "suspicious_auth"},
        {"name": "Malware Indicators", "description": "Detects known malware signatures", "severity": "critical", "rule_type": "signature", "conditions": "file_hash IN malware_database", "mitre_technique": "T1059", "mitre_tactic": "Execution", "enabled": True, "threat_type": "malware"},
        {"name": "Privilege Escalation", "description": "Detects privilege escalation attempts", "severity": "critical", "rule_type": "behavior", "conditions": "privilege_change FROM non_admin TO admin", "mitre_technique": "T1068", "mitre_tactic": "Privilege Escalation", "enabled": True, "threat_type": "priv_esc"},
        {"name": "Abnormal Network Traffic", "description": "Detects unusual network patterns", "severity": "medium", "rule_type": "anomaly", "conditions": "traffic_volume > baseline * 3", "mitre_technique": "T1071", "mitre_tactic": "Command and Control", "enabled": True, "threat_type": "network_anomaly"},
        {"name": "DDoS Detection", "description": "Detects distributed denial of service attacks", "severity": "high", "rule_type": "threshold", "conditions": "requests > 1000 FROM multiple_ips WITHIN 60s", "mitre_technique": "T1498", "mitre_tactic": "Impact", "enabled": True, "threat_type": "ddos"},
    ]
    for r in rules_data:
        rule = DetectionRule(**r, organization_id=org.id)
        db.add(rule)
    db.flush()

    # Create demo security events
    attacker_ips = [
        "203.45.167.89", "185.237.145.12", "45.89.201.56", "91.134.206.78",
        "172.67.198.34", "104.26.11.23", "162.159.36.2", "198.51.100.42",
    ]
    event_types = [
        ("failed_login", "authentication", "high"),
        ("port_scan", "network", "medium"),
        ("sql_injection", "web", "critical"),
        ("xss_attack", "web", "medium"),
        ("command_injection", "web", "critical"),
        ("suspicious_login", "authentication", "high"),
        ("malware", "endpoint", "critical"),
        ("privilege_escalation", "system", "critical"),
        ("abnormal_network", "network", "medium"),
    ]

    events = []
    for day_offset in range(7, -1, -1):
        day = now - timedelta(days=day_offset)
        num_events = random.randint(3, 8)
        for _ in range(num_events):
            etype, ecategory, eseverity = random.choice(event_types)
            ts = day.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))
            src_ip = random.choice(attacker_ips)
            event = SecurityEvent(
                timestamp=ts, event_type=etype, category=ecategory,
                description=f"{etype.replace('_', ' ').title()} from {src_ip}",
                source_ip=src_ip, username=random.choice(["admin", "root", "ubuntu", "deploy", "appuser"]),
                action=etype, status=random.choice(["detected", "blocked", "failure"]),
                severity=eseverity, risk_score=random.randint(40, 95),
                raw_log=f"timestamp={ts.isoformat()},source_ip={src_ip},action={etype}",
                is_flagged=True, source_file="demo_data",
                organization_id=org.id, user_id=user.id,
                asset_id=random.choice(assets).id if assets else None,
                created_at=ts,
            )
            db.add(event)
            events.append(event)
    db.flush()

    # Create demo alerts
    alert_templates = [
        {"title": "Brute Force Attack Detected", "severity": AlertSeverity.HIGH, "mitre_technique": "T1110", "mitre_tactic": "Credential Access", "risk_score": 90, "confidence": 85, "description": "Multiple failed login attempts detected from suspicious IP"},
        {"title": "Port Scanning Activity", "severity": AlertSeverity.MEDIUM, "mitre_technique": "T1046", "mitre_tactic": "Discovery", "risk_score": 50, "confidence": 70, "description": "Port scan detected from external IP"},
        {"title": "SQL Injection Attempt", "severity": AlertSeverity.CRITICAL, "mitre_technique": "T1190", "mitre_tactic": "Initial Access", "risk_score": 95, "confidence": 90, "description": "SQL injection payload detected in web request"},
        {"title": "Malware Detected on Endpoint", "severity": AlertSeverity.CRITICAL, "mitre_technique": "T1059", "mitre_tactic": "Execution", "risk_score": 95, "confidence": 85, "description": "Malware signature matched on endpoint"},
        {"title": "Suspicious Login Location", "severity": AlertSeverity.HIGH, "mitre_technique": "T1078", "mitre_tactic": "Initial Access", "risk_score": 65, "confidence": 60, "description": "Login from unusual geographic location"},
        {"title": "XSS Payload Detected", "severity": AlertSeverity.MEDIUM, "mitre_technique": "T1189", "mitre_tactic": "Initial Access", "risk_score": 55, "confidence": 75, "description": "Cross-site scripting payload detected"},
        {"title": "Command Injection Attempt", "severity": AlertSeverity.CRITICAL, "mitre_technique": "T1059", "mitre_tactic": "Execution", "risk_score": 92, "confidence": 88, "description": "OS command injection attempt blocked"},
    ]

    statuses = [AlertStatus.NEW, AlertStatus.ACKNOWLEDGED, AlertStatus.INVESTIGATING, AlertStatus.RESOLVED, AlertStatus.FALSE_POSITIVE]

    alerts = []
    for day_offset in range(7, -1, -1):
        day = now - timedelta(days=day_offset)
        num_alerts = random.randint(2, 5)
        for _ in range(num_alerts):
            tmpl = random.choice(alert_templates)
            ts = day.replace(hour=random.randint(0, 23), minute=random.randint(0, 59))
            src_ip = random.choice(attacker_ips)
            alert = Alert(
                title=tmpl["title"],
                description=tmpl["description"],
                severity=tmpl["severity"],
                status=random.choice(statuses),
                risk_score=tmpl["risk_score"] + random.randint(-10, 10),
                confidence=tmpl["confidence"] + random.randint(-10, 10),
                source_ip=src_ip,
                destination_ip=f"10.0.{random.randint(1,5)}.{random.randint(10,100)}",
                mitre_technique=tmpl["mitre_technique"],
                mitre_tactic=tmpl["mitre_tactic"],
                evidence=f"Alert generated from {tmpl['title'].lower()} detection.",
                organization_id=org.id,
                created_at=ts,
            )
            db.add(alert)
            alerts.append(alert)
    db.flush()

    # Create demo incidents
    incident_templates = [
        {"title": "Brute Force Campaign Against SSH", "severity": "high", "status": IncidentStatus.INVESTIGATING},
        {"title": "SQL Injection Attack on Web App", "severity": "critical", "status": IncidentStatus.INVESTIGATING},
        {"title": "Malware Outbreak on Endpoints", "severity": "critical", "status": IncidentStatus.CONTAINED},
        {"title": "Unauthorized Access Attempt", "severity": "high", "status": IncidentStatus.TRIAGED},
        {"title": "DDoS Attack in Progress", "severity": "high", "status": IncidentStatus.NEW},
    ]

    for i, tmpl in enumerate(incident_templates):
        ts = now - timedelta(days=i, hours=random.randint(0, 12))
        incident = Incident(
            title=tmpl["title"],
            description=f"Incident related to {tmpl['title'].lower()}. Requires investigation and containment.",
            severity=tmpl["severity"],
            status=tmpl["status"],
            organization_id=org.id,
            assignee_id=user.id,
            created_at=ts,
        )
        db.add(incident)
    db.flush()

    # Create demo notifications
    notif_templates = [
        ("Critical Alert: Brute Force Attack", "High-severity brute force attack detected from 203.45.167.89", "alert"),
        ("Incident Updated", "SQL Injection incident moved to Investigating", "incident"),
        ("New Asset Added", "Firewall added to asset inventory", "system"),
        ("Detection Rule Triggered", "SSH Brute Force rule generated 3 alerts today", "detection"),
    ]

    for title, message, ntype in notif_templates:
        notif = Notification(
            title=title, message=message, type=ntype,
            user_id=user.id,
            is_read=random.choice([True, False]),
        )
        db.add(notif)

    db.commit()
    return True

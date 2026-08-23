"""Settings API"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.audit_log import AuditLog
from app.auth import get_current_user, hash_password, verify_password

router = APIRouter(prefix="/api/settings", tags=["settings"])


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class OrgUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@router.get("/organization")
def get_organization(current_user: User = Depends(get_current_user)):
    org = current_user.organization
    if not org:
        raise HTTPException(status_code=404, detail="No organization")
    return {
        "id": org.id, "name": org.name, "slug": org.slug,
        "description": org.description, "plan": org.plan.value if hasattr(org.plan, 'value') else org.plan,
        "max_users": org.max_users, "max_assets": org.max_assets,
        "created_at": org.created_at.isoformat() if org.created_at else None,
    }


@router.put("/organization")
def update_organization(data: OrgUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    org = current_user.organization
    if data.name:
        org.name = data.name
    if data.description is not None:
        org.description = data.description
    db.commit()
    return {"message": "Organization updated"}


@router.put("/profile")
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    db.commit()
    return {"message": "Profile updated"}


@router.get("/api-keys")
def list_api_keys(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.api_key import ApiKey
    keys = db.query(ApiKey).filter(ApiKey.user_id == current_user.id).all()
    return {"keys": [{"id": k.id, "name": k.name, "key_prefix": k.key_prefix or "••••••••", "created_at": k.created_at.isoformat() if k.created_at else None} for k in keys]}


@router.post("/api-keys")
def create_api_key(body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    import secrets
    import hashlib
    from app.models.api_key import ApiKey
    key_name = body.get("name", "API Key")
    raw_key = f"nsk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    api_key = ApiKey(name=key_name, key_hash=key_hash, key_prefix=raw_key[:11], user_id=current_user.id)
    db.add(api_key)
    db.commit()
    return {"id": api_key.id, "name": key_name, "key": raw_key, "message": "Save this key securely. It will not be shown again."}


@router.delete("/api-keys/{key_id}")
def delete_api_key(key_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from app.models.api_key import ApiKey
    key = db.query(ApiKey).filter(ApiKey.id == key_id, ApiKey.user_id == current_user.id).first()
    if not key:
        raise HTTPException(status_code=404, detail="API key not found")
    db.delete(key)
    db.commit()
    return {"message": "API key deleted"}


@router.get("/team")
def list_team(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    members = db.query(User).filter(User.organization_id == current_user.organization_id).all()
    return {"members": [
        {"id": m.id, "username": m.username, "email": m.email, "full_name": m.full_name,
         "role": m.role.value if hasattr(m.role, 'value') else m.role,
         "is_active": m.is_active, "last_login": m.last_login.isoformat() if m.last_login else None}
        for m in members
    ]}


@router.get("/audit-logs")
def get_audit_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    logs = db.query(AuditLog).filter(AuditLog.organization_id == current_user.organization_id).order_by(AuditLog.created_at.desc()).limit(50).all()
    return {"audit_logs": [
        {"id": l.id, "action": l.action, "resource_type": l.resource_type, "details": l.details,
         "ip_address": l.ip_address, "user_id": l.user_id, "created_at": l.created_at.isoformat() if l.created_at else None}
        for l in logs
    ]}


# ── Notification Config ─────────────────────────────────────────────────

class EmailConfig(BaseModel):
    enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    to_email: Optional[str] = None
    use_tls: bool = True

class SlackConfig(BaseModel):
    enabled: bool = False
    webhook_url: Optional[str] = None

class WebhookEntry(BaseModel):
    name: str = ""
    url: str
    enabled: bool = True
    headers: Optional[Dict[str, str]] = None

class NotificationSettings(BaseModel):
    email: Optional[EmailConfig] = None
    slack: Optional[SlackConfig] = None
    custom_webhooks: Optional[List[WebhookEntry]] = None
    severity_filter: Optional[Dict[str, bool]] = None


def get_or_create_config(db: Session, org_id: int):
    from app.models.notification_config import NotificationConfig
    config = db.query(NotificationConfig).filter(NotificationConfig.organization_id == org_id).first()
    if not config:
        config = NotificationConfig(organization_id=org_id)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("/notifications")
def get_notification_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = get_or_create_config(db, current_user.organization_id)
    return config.to_dict()


@router.put("/notifications")
def update_notification_settings(data: NotificationSettings, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    config = get_or_create_config(db, current_user.organization_id)

    if data.email:
        config.email_enabled = data.email.enabled
        config.smtp_host = data.email.smtp_host
        config.smtp_port = data.email.smtp_port
        config.smtp_user = data.email.smtp_user
        if data.email.smtp_password:  # Only update if provided
            config.smtp_password = data.email.smtp_password
        config.from_email = data.email.from_email
        config.to_email = data.email.to_email
        config.use_tls = data.email.use_tls

    if data.slack:
        config.slack_enabled = data.slack.enabled
        config.slack_webhook_url = data.slack.webhook_url

    if data.custom_webhooks is not None:
        config.custom_webhooks = json.dumps([wh.dict() for wh in data.custom_webhooks])

    if data.severity_filter:
        config.notify_critical = data.severity_filter.get("critical", True)
        config.notify_high = data.severity_filter.get("high", True)
        config.notify_medium = data.severity_filter.get("medium", False)
        config.notify_low = data.severity_filter.get("low", False)

    from datetime import datetime, timezone
    config.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Notification settings updated", "config": config.to_dict()}


@router.post("/notifications/test")
def test_notification(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Send a test notification to verify channel configuration."""
    from app.services.notification_service import (
        send_email, send_slack_webhook, send_generic_webhook,
        format_alert_email, format_alert_slack, format_alert_webhook_payload,
    )

    channel = data.get("channel", "email")
    config = get_or_create_config(db, current_user.organization_id)

    # Fake alert for testing
    test_alert = {
        "title": "Test Alert: Notification Channel Verification",
        "description": "This is a test notification from Niks Security to verify your alert channel is configured correctly.",
        "severity": "high",
        "risk_score": 75,
        "source_ip": "192.168.1.100",
        "mitre_technique": "T1078",
        "mitre_tactic": "Initial Access",
        "created_at": "2026-08-23T12:00:00Z",
        "recommended_actions": "No action needed — this is a test notification.",
    }

    org = current_user.organization
    org_name = org.name if org else "Niks Security"

    if channel == "email":
        if not config.email_enabled or not config.smtp_host or not config.to_email:
            raise HTTPException(status_code=400, detail="Email not configured. Save settings first.")
        html = format_alert_email(test_alert, org_name)
        result = send_email(
            smtp_host=config.smtp_host, smtp_port=config.smtp_port or 587,
            smtp_user=config.smtp_user, smtp_password=config.smtp_password,
            to_email=config.to_email, subject="[TEST] Niks Security Alert",
            html_body=html, from_email=config.from_email, use_tls=config.use_tls,
        )
    elif channel == "slack":
        if not config.slack_enabled or not config.slack_webhook_url:
            raise HTTPException(status_code=400, detail="Slack not configured. Save settings first.")
        msg = format_alert_slack(test_alert, org_name)
        result = send_slack_webhook(config.slack_webhook_url, msg)
    elif channel == "webhook":
        url = data.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="Webhook URL required.")
        payload = format_alert_webhook_payload(test_alert, org_name)
        result = send_generic_webhook(url, payload, headers=data.get("headers"))
    else:
        raise HTTPException(status_code=400, detail=f"Unknown channel: {channel}")

    return result

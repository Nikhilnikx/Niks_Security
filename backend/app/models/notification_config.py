"""Notification Config model - stores org-level notification settings"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, unique=True, index=True)

    # Email settings
    email_enabled = Column(Boolean, default=False, nullable=False)
    smtp_host = Column(String(255), nullable=True)
    smtp_port = Column(Integer, default=587, nullable=True)
    smtp_user = Column(String(255), nullable=True)
    smtp_password = Column(String(500), nullable=True)  # In production, encrypt this
    from_email = Column(String(255), nullable=True)
    to_email = Column(String(255), nullable=True)
    use_tls = Column(Boolean, default=True, nullable=False)

    # Slack webhook
    slack_enabled = Column(Boolean, default=False, nullable=False)
    slack_webhook_url = Column(String(500), nullable=True)

    # Custom webhooks (JSON string: [{"name": "...", "url": "...", "enabled": true, "headers": {}}])
    custom_webhooks = Column(Text, nullable=True)

    # Alert filtering
    notify_critical = Column(Boolean, default=True, nullable=False)
    notify_high = Column(Boolean, default=True, nullable=False)
    notify_medium = Column(Boolean, default=False, nullable=False)
    notify_low = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self):
        import json
        return {
            "id": self.id,
            "organization_id": self.organization_id,
            "email": {
                "enabled": self.email_enabled,
                "smtp_host": self.smtp_host,
                "smtp_port": self.smtp_port,
                "smtp_user": self.smtp_user,
                "from_email": self.from_email,
                "to_email": self.to_email,
                "use_tls": self.use_tls,
            },
            "slack": {
                "enabled": self.slack_enabled,
                "webhook_url": self.slack_webhook_url,
            },
            "custom_webhooks": json.loads(self.custom_webhooks) if self.custom_webhooks else [],
            "severity_filter": {
                "critical": self.notify_critical,
                "high": self.notify_high,
                "medium": self.notify_medium,
                "low": self.notify_low,
            },
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

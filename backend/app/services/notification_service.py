"""Notification Service - sends alerts via Email (SMTP) and Webhooks (Slack, custom)"""
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import urllib.request
import urllib.error


def send_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    to_email: str,
    subject: str,
    html_body: str,
    from_email: Optional[str] = None,
    use_tls: bool = True,
) -> Dict[str, Any]:
    """Send an email via SMTP. Returns success/failure dict."""
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_email or smtp_user
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_body, "html"))

        context = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if use_tls:
                server.starttls(context=context)
            server.login(smtp_user, smtp_password)
            server.sendmail(msg["From"], [to_email], msg.as_string())

        return {"success": True, "channel": "email", "recipient": to_email}
    except Exception as e:
        return {"success": False, "channel": "email", "error": str(e)}


def send_slack_webhook(webhook_url: str, message: Dict[str, Any]) -> Dict[str, Any]:
    """Send a notification to a Slack-compatible webhook."""
    try:
        payload = json.dumps(message).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"success": True, "channel": "slack", "status": resp.status}
    except Exception as e:
        return {"success": False, "channel": "slack", "error": str(e)}


def send_generic_webhook(webhook_url: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Send a POST to a generic webhook URL with custom payload."""
    try:
        data = json.dumps(payload).encode("utf-8")
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        req = urllib.request.Request(webhook_url, data=data, headers=req_headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            return {"success": True, "channel": "webhook", "status": resp.status}
    except Exception as e:
        return {"success": False, "channel": "webhook", "error": str(e)}


# ── Alert Formatting ────────────────────────────────────────────────────

SEVERITY_COLORS = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#eab308",
    "low": "#22c55e",
}


def format_alert_email(alert_data: Dict[str, Any], org_name: str = "Niks Security") -> str:
    """Format an alert as a professional HTML email."""
    severity = alert_data.get("severity", "unknown")
    color = SEVERITY_COLORS.get(severity, "#7c3aed")

    return f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; background: #0f172a; color: #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: linear-gradient(135deg, #7c3aed, #a855f7); padding: 24px; text-align: center;">
        <h1 style="color: white; margin: 0; font-size: 20px;">🛡️ {org_name}</h1>
        <p style="color: rgba(255,255,255,0.8); margin: 8px 0 0; font-size: 14px;">Security Alert Notification</p>
      </div>
      <div style="padding: 24px;">
        <div style="background: {color}15; border: 1px solid {color}40; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span style="background: {color}; color: white; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 700; text-transform: uppercase;">{severity}</span>
            <span style="font-size: 13px; color: #94a3b8;">Risk Score: {alert_data.get('risk_score', 'N/A')}/100</span>
          </div>
          <h2 style="color: white; margin: 0 0 8px; font-size: 18px;">{alert_data.get('title', 'Security Alert')}</h2>
          <p style="color: #94a3b8; margin: 0; font-size: 14px;">{alert_data.get('description', '')}</p>
        </div>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px;">
          <tr><td style="padding: 8px 0; color: #64748b; font-size: 13px; border-bottom: 1px solid #1e293b;">Source IP</td><td style="padding: 8px 0; color: #e2e8f0; font-size: 13px; border-bottom: 1px solid #1e293b; text-align: right;">{alert_data.get('source_ip', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #64748b; font-size: 13px; border-bottom: 1px solid #1e293b;">MITRE Technique</td><td style="padding: 8px 0; color: #e2e8f0; font-size: 13px; border-bottom: 1px solid #1e293b; text-align: right;">{alert_data.get('mitre_technique', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #64748b; font-size: 13px; border-bottom: 1px solid #1e293b;">Tactic</td><td style="padding: 8px 0; color: #e2e8f0; font-size: 13px; border-bottom: 1px solid #1e293b; text-align: right;">{alert_data.get('mitre_tactic', 'N/A')}</td></tr>
          <tr><td style="padding: 8px 0; color: #64748b; font-size: 13px;">Created</td><td style="padding: 8px 0; color: #e2e8f0; font-size: 13px; text-align: right;">{alert_data.get('created_at', 'N/A')}</td></tr>
        </table>
        {f'''<div style="background: #1e293b; border-radius: 8px; padding: 12px; margin-bottom: 16px;">
          <div style="color: #a855f7; font-size: 11px; font-weight: 600; text-transform: uppercase; margin-bottom: 6px;">Recommended Actions</div>
          <p style="color: #94a3b8; margin: 0; font-size: 13px;">{alert_data.get('recommended_actions', '')}</p>
        </div>''' if alert_data.get('recommended_actions') else ''}
      </div>
      <div style="background: #1e293b; padding: 16px; text-align: center;">
        <p style="color: #64748b; margin: 0; font-size: 12px;">View this alert in your <a href="http://localhost:3000/dashboard/alerts" style="color: #a855f7;">Security Dashboard</a></p>
      </div>
    </div>
    """


def format_alert_slack(alert_data: Dict[str, Any], org_name: str = "Niks Security") -> Dict[str, Any]:
    """Format an alert as a Slack message payload."""
    severity = alert_data.get("severity", "unknown")
    color = SEVERITY_COLORS.get(severity, "#7c3aed")

    return {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {"type": "plain_text", "text": f"🛡️ {alert_data.get('title', 'Security Alert')}", "emoji": True},
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Severity:*\n:{severity}: `{severity.upper()}`"},
                            {"type": "mrkdwn", "text": f"*Risk Score:*\n{alert_data.get('risk_score', 'N/A')}/100"},
                            {"type": "mrkdwn", "text": f"*Source IP:*\n`{alert_data.get('source_ip', 'N/A')}`"},
                            {"type": "mrkdwn", "text": f"*MITRE:*\n`{alert_data.get('mitre_technique', 'N/A')}`"},
                        ],
                    },
                    {
                        "type": "section",
                        "text": {"type": "mrkdwn", "text": f"*Description:*\n{alert_data.get('description', '')}"},
                    },
                ],
            }
        ],
        "text": f"🚨 {org_name}: {alert_data.get('title', 'New Alert')} ({severity.upper()})",
    }


def format_alert_webhook_payload(alert_data: Dict[str, Any], org_name: str = "Niks Security") -> Dict[str, Any]:
    """Format an alert as a generic JSON webhook payload."""
    return {
        "event": "alert.created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organization": org_name,
        "alert": {
            "id": alert_data.get("id"),
            "title": alert_data.get("title"),
            "severity": alert_data.get("severity"),
            "risk_score": alert_data.get("risk_score"),
            "source_ip": alert_data.get("source_ip"),
            "mitre_technique": alert_data.get("mitre_technique"),
            "mitre_tactic": alert_data.get("mitre_tactic"),
            "description": alert_data.get("description"),
            "recommended_actions": alert_data.get("recommended_actions"),
            "created_at": alert_data.get("created_at"),
        },
    }


# ── Main Dispatcher ────────────────────────────────────────────────────

def dispatch_alert_notifications(
    alert_data: Dict[str, Any],
    org_name: str = "Niks Security",
    email_config: Optional[Dict[str, Any]] = None,
    slack_webhook_url: Optional[str] = None,
    custom_webhooks: Optional[list] = None,
) -> list:
    """
    Send alert notifications to all configured channels.
    Returns a list of delivery results.
    """
    results = []

    # Email notification
    if email_config and email_config.get("enabled"):
        html = format_alert_email(alert_data, org_name)
        subject = f"[{alert_data.get('severity', 'alert').upper()}] {alert_data.get('title', 'Security Alert')}"
        result = send_email(
            smtp_host=email_config["smtp_host"],
            smtp_port=email_config.get("smtp_port", 587),
            smtp_user=email_config["smtp_user"],
            smtp_password=email_config["smtp_password"],
            to_email=email_config["to_email"],
            subject=subject,
            html_body=html,
            from_email=email_config.get("from_email"),
            use_tls=email_config.get("use_tls", True),
        )
        results.append(result)

    # Slack webhook
    if slack_webhook_url:
        slack_msg = format_alert_slack(alert_data, org_name)
        result = send_slack_webhook(slack_webhook_url, slack_msg)
        results.append(result)

    # Custom webhooks
    if custom_webhooks:
        for wh in custom_webhooks:
            if wh.get("url") and wh.get("enabled", True):
                payload = format_alert_webhook_payload(alert_data, org_name)
                result = send_generic_webhook(
                    wh["url"], payload, headers=wh.get("headers")
                )
                results.append(result)

    return results

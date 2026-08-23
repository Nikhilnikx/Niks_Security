"""Onboarding API - status check, team invite, quick-setup rules"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.detection_rule import DetectionRule
from app.models.audit_log import AuditLog
from app.auth import get_current_user

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class TeamInvite(BaseModel):
    email: str
    role: str = "analyst"


class QuickRule(BaseModel):
    name: str
    rule_type: str = "threshold"
    severity: str = "medium"
    mitre_technique: Optional[str] = None
    mitre_tactic: Optional[str] = None
    enabled: bool = True


@router.get("/status")
def get_onboarding_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Check if user needs onboarding and return progress."""
    org_id = current_user.organization_id

    # Check what's been set up
    member_count = db.query(User).filter(User.organization_id == org_id).count()
    rule_count = db.query(DetectionRule).filter(DetectionRule.organization_id == org_id).count()
    has_org_name = bool(current_user.organization and current_user.organization.name != f"{current_user.username}'s Organization")

    steps = {
        "org_setup": has_org_name,
        "team_invite": member_count > 1,
        "detection_rules": rule_count > 0,
    }

    completed = sum(1 for v in steps.values() if v)
    total = len(steps)

    return {
        "onboarding_needed": completed < total,
        "steps": steps,
        "completed": completed,
        "total": total,
        "progress_pct": int((completed / total) * 100),
        "member_count": member_count,
        "rule_count": rule_count,
    }


class OrgSetup(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


@router.put("/org-setup")
def update_org_setup(data: OrgSetup, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Step 1: Update organization details."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    org = current_user.organization
    if not org:
        raise HTTPException(status_code=404, detail="No organization found")

    if data.name:
        org.name = data.name
    if data.description is not None:
        org.description = data.description
    db.commit()
    return {"message": "Organization updated", "name": org.name}


@router.post("/invite")
def invite_team_member(data: TeamInvite, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Step 2: Invite a team member (creates a placeholder user)."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    org_id = current_user.organization_id

    # Check if user already exists
    existing = db.query(User).filter(User.email == data.email.lower()).first()
    if existing:
        if existing.organization_id == org_id:
            return {"message": "User already in your organization", "user_id": existing.id}
        raise HTTPException(status_code=409, detail="Email already registered to another organization")

    # Check org member limit
    org = current_user.organization
    member_count = db.query(User).filter(User.organization_id == org_id).count()
    if org and member_count >= org.max_users:
        raise HTTPException(status_code=400, detail=f"Organization has reached the maximum of {org.max_users} members")

    # Create user with pending status
    username = data.email.split("@")[0].replace(".", "_")
    # Make username unique
    base_username = username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}_{counter}"
        counter += 1

    role_map = {"admin": UserRole.ADMIN, "analyst": UserRole.ANALYST, "viewer": UserRole.VIEWER}
    user_role = role_map.get(data.role, UserRole.ANALYST)

    new_user = User(
        username=username,
        email=data.email.lower(),
        full_name="",
        password_hash="pending",  # Will be set when they accept invite
        role=user_role,
        is_active=True,
        is_verified=False,
        organization_id=org_id,
    )
    db.add(new_user)

    audit = AuditLog(
        action="team_invite_sent",
        resource_type="user",
        details=f"Invited {data.email} as {data.role}",
        user_id=current_user.id,
        organization_id=org_id,
    )
    db.add(audit)
    db.commit()
    db.refresh(new_user)

    return {
        "message": f"Invitation sent to {data.email}",
        "user": {"id": new_user.id, "email": new_user.email, "role": data.role, "username": username},
    }


# Pre-built detection rules for quick setup
QUICK_RULES = [
    {
        "name": "SSH Brute Force Detection",
        "description": "Detects multiple failed SSH login attempts from a single source",
        "rule_type": "threshold",
        "severity": "high",
        "mitre_technique": "T1110",
        "mitre_tactic": "Credential Access",
        "conditions": '{"event_type": "failed_login", "threshold": 5, "window_seconds": 600}',
    },
    {
        "name": "Port Scanning Detection",
        "description": "Detects port scanning activity from reconnaissance sources",
        "rule_type": "threshold",
        "severity": "medium",
        "mitre_technique": "T1046",
        "mitre_tactic": "Discovery",
        "conditions": '{"event_type": "port_scan", "threshold": 15, "window_seconds": 300}',
    },
    {
        "name": "SQL Injection Detection",
        "description": "Detects SQL injection attempts in web application inputs",
        "rule_type": "pattern",
        "severity": "critical",
        "mitre_technique": "T1190",
        "mitre_tactic": "Initial Access",
        "conditions": '{"patterns": ["UNION SELECT", "OR 1=1", "DROP TABLE", "INSERT INTO"]}',
    },
    {
        "name": "Suspicious Login Location",
        "description": "Detects authentication from unusual geographic locations",
        "rule_type": "anomaly",
        "severity": "medium",
        "mitre_technique": "T1078",
        "mitre_tactic": "Initial Access",
        "conditions": '{"check_geolocation": true, "baseline_days": 7}',
    },
    {
        "name": "Malware Indicator Detection",
        "description": "Detects known malware signatures and file hashes",
        "rule_type": "pattern",
        "severity": "critical",
        "mitre_technique": "T1059",
        "mitre_tactic": "Execution",
        "conditions": '{"hash_match": true, "signature_match": true}',
    },
    {
        "name": "XSS Attack Detection",
        "description": "Detects cross-site scripting payloads in web requests",
        "rule_type": "pattern",
        "severity": "high",
        "mitre_technique": "T1189",
        "mitre_tactic": "Initial Access",
        "conditions": '{"patterns": ["<script>", "onerror=", "onload=", "javascript:"]}',
    },
]


@router.get("/quick-rules")
def list_quick_rules():
    """List pre-built detection rules for quick setup."""
    return {"rules": QUICK_RULES}


@router.post("/quick-rules")
def setup_quick_rules(data: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Step 3: Create selected detection rules."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")

    org_id = current_user.organization_id
    selected = data.get("rules", [])  # list of rule names or indices

    if not selected:
        # Create all rules
        selected_rules = QUICK_RULES
    else:
        selected_rules = []
        for s in selected:
            if isinstance(s, int) and 0 <= s < len(QUICK_RULES):
                selected_rules.append(QUICK_RULES[s])
            elif isinstance(s, str):
                for r in QUICK_RULES:
                    if r["name"] == s:
                        selected_rules.append(r)
                        break

    created = []
    for rule_data in selected_rules:
        rule = DetectionRule(
            name=rule_data["name"],
            description=rule_data["description"],
            rule_type=rule_data["rule_type"],
            severity=rule_data["severity"],
            mitre_technique=rule_data.get("mitre_technique"),
            mitre_tactic=rule_data.get("mitre_tactic"),
            conditions=rule_data.get("conditions"),
            enabled=True,
            organization_id=org_id,
        )
        db.add(rule)
        created.append(rule_data["name"])

    db.commit()

    return {"message": f"Created {len(created)} detection rules", "rules_created": created}


@router.post("/complete")
def complete_onboarding(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Mark onboarding as complete."""
    # Record in audit log
    audit = AuditLog(
        action="onboarding_completed",
        resource_type="user",
        details="Onboarding wizard completed",
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()
    return {"message": "Onboarding completed"}

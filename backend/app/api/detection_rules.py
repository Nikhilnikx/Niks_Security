"""Detection Rules API"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.detection_rule import DetectionRule
from app.models.audit_log import AuditLog
from app.auth import get_current_user
from app.detector.rules import DEFAULT_RULES

router = APIRouter(prefix="/api/rules", tags=["detection-rules"])


class RuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    rule_type: str = "threshold"
    severity: str = "medium"
    mitre_technique: Optional[str] = None
    mitre_tactic: Optional[str] = None
    conditions: Optional[str] = None


class RuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[str] = None
    enabled: Optional[bool] = None
    conditions: Optional[str] = None
    mitre_technique: Optional[str] = None
    mitre_tactic: Optional[str] = None


@router.get("")
def list_rules(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    query = db.query(DetectionRule).filter(DetectionRule.organization_id == org_id)
    if enabled is not None:
        query = query.filter(DetectionRule.enabled == enabled)

    total = query.count()
    rules = query.order_by(DetectionRule.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "rules": [r.to_dict() for r in rules],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }


@router.post("")
def create_rule(data: RuleCreate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = DetectionRule(
        name=data.name,
        description=data.description,
        rule_type=data.rule_type,
        severity=data.severity,
        mitre_technique=data.mitre_technique,
        mitre_tactic=data.mitre_tactic,
        conditions=data.conditions,
        organization_id=current_user.organization_id,
    )
    db.add(rule)
    audit = AuditLog(action="rule_created", resource_type="detection_rule", details=data.name, user_id=current_user.id, organization_id=current_user.organization_id)
    db.add(audit)
    db.commit()
    db.refresh(rule)
    return rule.to_dict()


@router.patch("/{rule_id}/toggle")
def toggle_rule(rule_id: int, body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id, DetectionRule.organization_id == current_user.organization_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.enabled = body.get("enabled", not rule.enabled)
    db.commit()
    return rule.to_dict()


@router.put("/{rule_id}")
def update_rule(rule_id: int, data: RuleUpdate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id, DetectionRule.organization_id == current_user.organization_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rule, field, value)
    audit = AuditLog(action="rule_updated", resource_type="detection_rule", resource_id=rule.id, details=f"Updated rule: {rule.name}", user_id=current_user.id, organization_id=current_user.organization_id)
    db.add(audit)
    db.commit()
    db.refresh(rule)
    return rule.to_dict()


@router.delete("/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rule = db.query(DetectionRule).filter(DetectionRule.id == rule_id, DetectionRule.organization_id == current_user.organization_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted"}


@router.post("/seed-defaults")
def seed_default_rules(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Initialize the organization with default detection rules."""
    org_id = current_user.organization_id
    existing = db.query(DetectionRule).filter(DetectionRule.organization_id == org_id).count()
    if existing > 0:
        return {"message": f"Organization already has {existing} rules", "seeded": 0}

    seeded = 0
    for rule_data in DEFAULT_RULES:
        rule = DetectionRule(organization_id=org_id, **rule_data)
        db.add(rule)
        seeded += 1
    db.commit()
    return {"message": f"Seeded {seeded} default detection rules", "seeded": seeded}

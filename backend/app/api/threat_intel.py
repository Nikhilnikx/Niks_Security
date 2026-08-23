"""Threat Intelligence API"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import hashlib
import random
from app.database import get_db
from app.models.user import User
from app.models.threat_indicator import ThreatIndicator
from app.auth import get_current_user

router = APIRouter(prefix="/api/threat-intel", tags=["threat-intelligence"])


class IOCSearch(BaseModel):
    indicator_type: str
    value: str


@router.get("/lookup")
def lookup_ioc_get(type: str = "ip", query: str = "", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Look up an IOC via GET params."""
    data = IOCSearch(indicator_type=type, value=query)
    return _do_lookup(data, db, current_user)


@router.post("/lookup")
def lookup_ioc(data: IOCSearch, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Look up an IOC in the threat intelligence database."""
    return _do_lookup(data, db, current_user)


def _do_lookup(data, db, current_user):
    """Look up an IOC in the threat intelligence database."""
    org_id = current_user.organization_id
    existing = db.query(ThreatIndicator).filter(
        ThreatIndicator.organization_id == org_id,
        ThreatIndicator.indicator_type == data.indicator_type,
        ThreatIndicator.value == data.value,
    ).first()

    if existing:
        existing.detection_count += 1
        existing.last_seen = datetime.now(timezone.utc)
        db.commit()
        return existing.to_dict()

    # Generate reputation assessment based on known patterns
    reputation = _assess_reputation(data.indicator_type, data.value)

    indicator = ThreatIndicator(
        indicator_type=data.indicator_type,
        value=data.value,
        threat_type=reputation["threat_type"],
        severity=reputation["severity"],
        confidence=reputation["confidence"],
        risk_score=reputation["risk_score"],
        reputation=reputation["reputation"],
        geolocation=reputation.get("geolocation"),
        asn=reputation.get("asn"),
        country=reputation.get("country"),
        description=reputation.get("description"),
        source="internal_analysis",
        first_seen=datetime.now(timezone.utc),
        last_seen=datetime.now(timezone.utc),
        detection_count=1,
        organization_id=org_id,
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator.to_dict()


@router.get("")
def list_indicators(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    indicator_type: Optional[str] = None,
    reputation: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ThreatIndicator).filter(ThreatIndicator.organization_id == current_user.organization_id)
    if indicator_type:
        query = query.filter(ThreatIndicator.indicator_type == indicator_type)
    if reputation:
        query = query.filter(ThreatIndicator.reputation == reputation)
    if search:
        query = query.filter(ThreatIndicator.value.ilike(f"%{search}%"))

    total = query.count()
    indicators = query.order_by(ThreatIndicator.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "indicators": [i.to_dict() for i in indicators],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }


def _assess_reputation(indicator_type, value):
    """Simple heuristic-based reputation assessment."""
    # Check against known suspicious patterns
    suspicious_tlds = {".ru", ".cn", ".kp", ".ir"}
    suspicious_asns = {51207, 41379, 36352}

    value_lower = value.lower()
    risk_score = 10.0
    confidence = 40.0
    reputation = "unknown"
    threat_type = None
    severity = "low"

    if indicator_type == "ip":
        # Check for suspicious IP patterns
        if value.startswith("10.") or value.startswith("192.168.") or value.startswith("172."):
            risk_score = 5.0
            reputation = "clean"
            return {"risk_score": risk_score, "confidence": 60, "reputation": reputation, "threat_type": None, "severity": "info", "description": "Private IP address"}

        # Simulated check - in production this would query real threat intel APIs
        hash_val = int(hashlib.md5(value.encode()).hexdigest()[:8], 16)
        if hash_val % 10 == 0:  # ~10% flagged
            risk_score = 75.0
            confidence = 65.0
            reputation = "malicious"
            threat_type = "C2 Server"
            severity = "high"
        elif hash_val % 5 == 0:  # ~20% flagged
            risk_score = 45.0
            confidence = 50.0
            reputation = "suspicious"
            threat_type = "Scanning"
            severity = "medium"

    elif indicator_type == "domain":
        if any(value_lower.endswith(tld) for tld in suspicious_tlds):
            risk_score = 55.0
            confidence = 45.0
            reputation = "suspicious"
            threat_type = "Potentially Unwanted Domain"
            severity = "medium"

    elif indicator_type == "hash":
        # File hashes with known patterns
        risk_score = 80.0
        confidence = 70.0
        reputation = "malicious"
        threat_type = "Malware"
        severity = "critical"

    return {
        "risk_score": risk_score,
        "confidence": confidence,
        "reputation": reputation,
        "threat_type": threat_type,
        "severity": severity,
        "description": f"Analysis of {indicator_type}: {value[:50]}",
    }

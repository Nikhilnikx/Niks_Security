"""MITRE ATT&CK mapping API"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.alert import Alert
from app.models.incident import Incident
from app.auth import get_current_user

router = APIRouter(prefix="/api/mitre", tags=["mitre-attack"])

# MITRE ATT&CK techniques used in the platform
MITRE_TECHNIQUES = {
    "T1110": {"name": "Brute Force", "tactic": "Credential Access", "description": "Adversaries may use brute force techniques to gain access to accounts."},
    "T1110.001": {"name": "Password Guessing", "tactic": "Credential Access", "description": "Adversaries may guess passwords to access victim accounts."},
    "T1110.003": {"name": "Password Spraying", "tactic": "Credential Access", "description": "Adversaries may use a single password against many accounts."},
    "T1046": {"name": "Network Service Scanning", "tactic": "Discovery", "description": "Adversaries may attempt to get a listing of services running on remote hosts."},
    "T1190": {"name": "Exploit Public-Facing Application", "tactic": "Initial Access", "description": "Adversaries may attempt to take advantage of a weakness in an Internet-facing computer or program."},
    "T1189": {"name": "Drive-by Compromise", "tactic": "Initial Access", "description": "Adversaries may gain access to a system through a user visiting a website."},
    "T1059": {"name": "Command and Scripting Interpreter", "tactic": "Execution", "description": "Adversaries may abuse command and script interpreters to execute commands and scripts."},
    "T1078": {"name": "Valid Accounts", "tactic": "Initial Access", "description": "Adversaries may obtain and abuse credentials of existing accounts."},
    "T1068": {"name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation", "description": "Adversaries may exploit software vulnerabilities to elevate privileges."},
    "T1498": {"name": "Network Denial of Service", "tactic": "Impact", "description": "Adversaries may perform Network Denial of Service attacks."},
    "T1027": {"name": "Obfuscated Files or Information", "tactic": "Defense Evasion", "description": "Adversaries may attempt to make an executable or file difficult to discover or analyze."},
    "T1053": {"name": "Scheduled Task/Job", "tactic": "Execution", "description": "Adversaries may abuse task scheduling functionality to facilitate execution."},
}


@router.get("/techniques")
def list_techniques():
    """List all MITRE ATT&CK techniques tracked by the platform."""
    return {"techniques": MITRE_TECHNIQUES}


@router.get("/mapping")
def get_mapping(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _build_matrix(db, current_user)


@router.get("/matrix")
def get_matrix(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return _build_matrix(db, current_user)


def _build_matrix(db, current_user):
    """Get the MITRE ATT&CK matrix with detection counts for the organization."""
    org_id = current_user.organization_id

    # Count alerts by MITRE technique
    technique_counts = dict(
        db.query(Alert.mitre_technique, func.count(Alert.id))
        .filter(Alert.organization_id == org_id, Alert.mitre_technique.isnot(None))
        .group_by(Alert.mitre_technique)
        .all()
    )

    matrix = []
    for tech_id, tech_info in MITRE_TECHNIQUES.items():
        count = technique_counts.get(tech_id, 0)
        matrix.append({
            "technique_id": tech_id,
            "name": tech_info["name"],
            "tactic": tech_info["tactic"],
            "description": tech_info["description"],
            "detection_count": count,
            "has_detections": count > 0,
        })

    total_alerts = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id).scalar() or 0
    total_incidents = db.query(func.count(Incident.id)).filter(Incident.organization_id == org_id).scalar() or 0
    total_detections = sum(technique_counts.values())

    return {
        "techniques": matrix,
        "matrix": matrix,
        "stats": {
            "total_techniques": len(matrix),
            "total_alerts": total_alerts,
            "total_incidents": total_incidents,
            "total_detections": total_detections,
        },
    }

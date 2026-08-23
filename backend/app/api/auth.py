"""Auth API - signup, login, logout, profile, forgot/reset password, admin user mgmt"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization, PlanType
from app.models.audit_log import AuditLog
from app.auth import hash_password, verify_password, create_access_token, get_current_user, get_current_admin
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/api/auth", tags=["auth"])


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    organization_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class AdminUserUpdate(BaseModel):
    role: Optional[str] = None
    is_active: Optional[bool] = None
    full_name: Optional[str] = None


def validate_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters"
    if not any(c.islower() for c in password):
        return "Password must include a lowercase letter"
    if not any(c.isupper() for c in password):
        return "Password must include an uppercase letter"
    if not any(c.isdigit() for c in password):
        return "Password must include a number"
    return None


@router.post("/signup")
def signup(data: SignupRequest, request: Request, db: Session = Depends(get_db)):
    if not data.username or not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Username, email, and password are required")

    password_error = validate_password(data.password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)

    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    if db.query(User).filter(User.email == data.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(
        username=data.username,
        email=data.email.lower(),
        full_name=data.full_name,
        password_hash=hash_password(data.password),
        role=UserRole.ADMIN,  # First user of org is admin
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.flush()

    # Create organization
    org_name = data.organization_name or f"{data.username}'s Organization"
    slug = data.username.lower().replace(" ", "-").replace("'", "") + "-org"
    org = Organization(
        name=org_name,
        slug=slug,
        plan=PlanType.FREE,
    )
    db.add(org)
    db.flush()

    user.organization_id = org.id
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "org_id": org.id, "role": user.role.value})

    # Audit log
    audit = AuditLog(
        action="user_signup",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_id=user.id,
        organization_id=org.id,
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Account created successfully",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "organization_id": org.id,
            "organization_name": org.name,
        },
    }


@router.post("/login")
def login(data: LoginRequest, request: Request, db: Session = Depends(get_db)):
    if not data.email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = db.query(User).filter(User.email == data.email.lower()).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    user.last_login = datetime.now(timezone.utc)
    token = create_access_token({
        "sub": str(user.id),
        "org_id": user.organization_id,
        "role": user.role.value,
    })

    audit = AuditLog(
        action="user_login",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_id=user.id,
        organization_id=user.organization_id,
    )
    db.add(audit)
    db.commit()

    return {
        "message": "Login successful",
        "access_token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "organization_id": user.organization_id,
            "organization_name": user.organization.name if user.organization else None,
        },
    }


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "organization_id": current_user.organization_id,
        "organization_name": current_user.organization.name if current_user.organization else None,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
    }


@router.put("/profile")
def update_profile(data: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.full_name is not None:
        current_user.full_name = data.full_name
    if data.username and data.username != current_user.username:
        if db.query(User).filter(User.username == data.username, User.id != current_user.id).first():
            raise HTTPException(status_code=409, detail="Username already taken")
        current_user.username = data.username
    db.commit()
    return {"message": "Profile updated"}


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    password_error = validate_password(data.new_password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)
    current_user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# ── Forgot / Reset Password ────────────────────────────────────────────

@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    """Request a password reset token. Always returns success to prevent email enumeration."""
    user = db.query(User).filter(User.email == data.email.lower()).first()

    # Always return success to prevent email enumeration
    if user and user.is_active:
        from app.models.password_reset import PasswordResetToken
        token = PasswordResetToken.create_for_user(user.id, db)

        # In production, send email here. For dev, include token in response.
        reset_url = f"{settings.APP_URL}/reset-password?token={token}"

        audit = AuditLog(
            action="password_reset_requested",
            resource_type="user",
            resource_id=user.id,
            details=f"Password reset requested for {user.email}",
            ip_address=request.client.host if request.client else None,
            user_id=user.id,
            organization_id=user.organization_id,
        )
        db.add(audit)
        db.commit()

        # Dev mode: return token in response. In prod, send via email only.
        if settings.ENVIRONMENT == "development":
            return {
                "message": "If an account with that email exists, a reset link has been sent.",
                "debug_token": token,
                "debug_url": reset_url,
            }

    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid token."""
    from app.models.password_reset import PasswordResetToken

    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token
    ).first()

    if not reset_token or not reset_token.is_valid():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    password_error = validate_password(data.new_password)
    if password_error:
        raise HTTPException(status_code=400, detail=password_error)

    user = db.query(User).filter(User.id == reset_token.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(data.new_password)
    reset_token.used = True
    db.commit()

    return {"message": "Password has been reset successfully. You can now sign in."}


@router.get("/reset-password/verify")
def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """Check if a reset token is still valid."""
    from app.models.password_reset import PasswordResetToken

    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()

    if not reset_token or not reset_token.is_valid():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    return {"valid": True, "email": "***"}


# ── Admin User Management ──────────────────────────────────────────────

@router.get("/admin/users")
def admin_list_users(
    page: int = 1, limit: int = 20,
    search: Optional[str] = None,
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin: List all users across the organization."""
    query = db.query(User).filter(User.organization_id == current_user.organization_id)

    if search:
        query = query.filter(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )
    if role:
        query = query.filter(User.role == role)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "users": [
            {
                "id": u.id,
                "username": u.username,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value,
                "is_active": u.is_active,
                "is_verified": u.is_verified,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }


@router.put("/admin/users/{user_id}")
def admin_update_user(
    user_id: int,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin: Update a user's role, status, or name."""
    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user.organization_id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent self-demotion
    if user.id == current_user.id and data.role and data.role != "admin":
        raise HTTPException(status_code=400, detail="Cannot change your own admin role")

    if data.role is not None:
        valid_roles = {"admin", "analyst", "viewer"}
        if data.role not in valid_roles:
            raise HTTPException(status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}")
        user.role = data.role

    if data.is_active is not None:
        # Prevent self-deactivation
        if user.id == current_user.id and not data.is_active:
            raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
        user.is_active = data.is_active

    if data.full_name is not None:
        user.full_name = data.full_name

    db.commit()

    audit = AuditLog(
        action="admin_user_updated",
        resource_type="user",
        resource_id=user.id,
        details=f"Admin updated user #{user.id}: role={user.role.value}, active={user.is_active}",
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()

    return {
        "message": "User updated",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active,
        },
    }


@router.delete("/admin/users/{user_id}")
def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin: Deactivate a user (soft delete)."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user = db.query(User).filter(
        User.id == user_id,
        User.organization_id == current_user.organization_id,
    ).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    audit = AuditLog(
        action="admin_user_deactivated",
        resource_type="user",
        resource_id=user.id,
        details=f"Admin deactivated user #{user.id} ({user.email})",
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )
    db.add(audit)
    db.commit()

    return {"message": f"User {user.username} has been deactivated"}


@router.get("/admin/stats")
def admin_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin: System-wide stats for the organization."""
    from sqlalchemy import func
    from app.models.alert import Alert, AlertSeverity
    from app.models.incident import Incident
    from app.models.security_event import SecurityEvent
    from app.models.asset import Asset
    from app.models.audit_log import AuditLog

    org_id = current_user.organization_id

    total_users = db.query(func.count(User.id)).filter(User.organization_id == org_id).scalar() or 0
    active_users = db.query(func.count(User.id)).filter(User.organization_id == org_id, User.is_active == True).scalar() or 0
    total_alerts = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id).scalar() or 0
    critical_alerts = db.query(func.count(Alert.id)).filter(Alert.organization_id == org_id, Alert.severity == AlertSeverity.CRITICAL).scalar() or 0
    total_incidents = db.query(func.count(Incident.id)).filter(Incident.organization_id == org_id).scalar() or 0
    total_events = db.query(func.count(SecurityEvent.id)).filter(SecurityEvent.organization_id == org_id).scalar() or 0
    total_assets = db.query(func.count(Asset.id)).filter(Asset.organization_id == org_id).scalar() or 0

    # Recent activity (last 20 audit events)
    recent_activity = db.query(AuditLog).filter(
        AuditLog.organization_id == org_id
    ).order_by(AuditLog.created_at.desc()).limit(20).all()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_alerts": total_alerts,
        "critical_alerts": critical_alerts,
        "total_incidents": total_incidents,
        "total_events": total_events,
        "total_assets": total_assets,
        "recent_activity": [
            {
                "id": a.id,
                "action": a.action,
                "resource_type": a.resource_type,
                "details": a.details,
                "ip_address": a.ip_address,
                "user_id": a.user_id,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in recent_activity
        ],
    }


@router.get("/admin/activity")
def admin_activity_log(
    page: int = 1, limit: int = 30,
    action: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Admin: Paginated activity log."""
    query = db.query(AuditLog).filter(AuditLog.organization_id == current_user.organization_id)
    if action:
        query = query.filter(AuditLog.action == action)

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "logs": [
            {
                "id": l.id,
                "action": l.action,
                "resource_type": l.resource_type,
                "details": l.details,
                "ip_address": l.ip_address,
                "user_id": l.user_id,
                "created_at": l.created_at.isoformat() if l.created_at else None,
            }
            for l in logs
        ],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }

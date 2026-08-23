"""Auth API - signup, login, logout, profile"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.organization import Organization, PlanType
from app.models.audit_log import AuditLog
from app.auth import hash_password, verify_password, create_access_token, get_current_user

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

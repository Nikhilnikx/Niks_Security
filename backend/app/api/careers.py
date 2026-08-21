from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.career import CareerPath, CareerCertification, UserCareerGoal
from app.models.certification import Certification
from app.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/careers", tags=["careers"])


class CareerGoalRequest(BaseModel):
    career_path_id: Optional[int] = None
    goal_type: Optional[str] = None
    current_level: Optional[str] = None
    preferred_technology: Optional[str] = None
    target_role: Optional[str] = None
    daily_hours: Optional[int] = None
    target_date: Optional[str] = None


# --- List Career Paths ---

@router.get("/")
async def list_career_paths(db: Session = Depends(get_db)):
    paths = db.query(CareerPath).filter(CareerPath.active == True).all()
    result = []
    for p in paths:
        certs = db.query(CareerCertification).filter(
            CareerCertification.career_path_id == p.id
        ).order_by(CareerCertification.order_index).all()
        result.append({
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
            "difficulty": p.difficulty,
            "estimated_months": p.estimated_months,
            "skills_covered": p.skills_covered,
            "certifications_count": len(certs),
            "certifications": [
                {
                    "id": c.id,
                    "stage": c.stage,
                    "order_index": c.order_index,
                    "required": c.required,
                    "certification": {
                        "id": c.certification.id,
                        "name": c.certification.name,
                        "code": c.certification.code,
                        "level": c.certification.level.value if c.certification.level else None,
                    } if c.certification else None,
                }
                for c in certs
            ],
        })
    return {"career_paths": result}


# --- Get Single Career Path ---

@router.get("/{slug}")
async def get_career_path(slug: str, db: Session = Depends(get_db)):
    path = db.query(CareerPath).filter(CareerPath.slug == slug).first()
    if not path:
        raise HTTPException(status_code=404, detail="Career path not found")

    certs = db.query(CareerCertification).filter(
        CareerCertification.career_path_id == path.id
    ).order_by(CareerCertification.order_index).all()

    return {
        "id": path.id,
        "name": path.name,
        "slug": path.slug,
        "description": path.description,
        "difficulty": path.difficulty,
        "estimated_months": path.estimated_months,
        "skills_covered": path.skills_covered,
        "roadmap": [
            {
                "stage": c.stage,
                "order_index": c.order_index,
                "required": c.required,
                "description": c.description,
                "certification": {
                    "id": c.certification.id,
                    "name": c.certification.name,
                    "code": c.certification.code,
                    "level": c.certification.level.value if c.certification.level else None,
                    "slug": c.certification.slug,
                } if c.certification else None,
            }
            for c in certs
        ],
    }


# --- Set Career Goal ---

@router.post("/goal")
async def set_career_goal(
    request: CareerGoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Upsert career goal
    goal = db.query(UserCareerGoal).filter(
        UserCareerGoal.user_id == current_user.id
    ).first()

    if not goal:
        goal = UserCareerGoal(user_id=current_user.id)
        db.add(goal)

    if request.career_path_id:
        goal.career_path_id = request.career_path_id
    if request.goal_type:
        goal.goal_type = request.goal_type
    if request.current_level:
        goal.current_level = request.current_level
    if request.preferred_technology:
        goal.preferred_technology = request.preferred_technology
    if request.target_role:
        goal.target_role = request.target_role
    if request.daily_hours:
        goal.daily_hours = request.daily_hours
    if request.target_date:
        try:
            goal.target_date = datetime.strptime(request.target_date, "%Y-%m-%d")
        except ValueError:
            pass

    goal.updated_at = datetime.utcnow()
    db.commit()

    return {"status": "saved", "goal_id": goal.id}


# --- Get Career Goal ---

@router.get("/goal/me")
async def get_my_career_goal(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    goal = db.query(UserCareerGoal).filter(
        UserCareerGoal.user_id == current_user.id
    ).first()

    if not goal:
        return {"goal": None}

    career_path = None
    if goal.career_path_id:
        path = db.query(CareerPath).filter(CareerPath.id == goal.career_path_id).first()
        if path:
            certs = db.query(CareerCertification).filter(
                CareerCertification.career_path_id == path.id
            ).order_by(CareerCertification.order_index).all()
            career_path = {
                "id": path.id,
                "name": path.name,
                "slug": path.slug,
                "roadmap": [
                    {
                        "stage": c.stage,
                        "order_index": c.order_index,
                        "certification": {
                            "id": c.certification.id,
                            "name": c.certification.name,
                            "code": c.certification.code,
                        } if c.certification else None,
                    }
                    for c in certs
                ],
            }

    return {
        "goal": {
            "id": goal.id,
            "goal_type": goal.goal_type,
            "current_level": goal.current_level,
            "preferred_technology": goal.preferred_technology,
            "target_role": goal.target_role,
            "daily_hours": goal.daily_hours,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "career_path": career_path,
        }
    }


# --- Admin: Create Career Path ---

@router.post("/admin/career-paths")
async def create_career_path(
    name: str,
    slug: str,
    description: Optional[str] = None,
    difficulty: Optional[str] = None,
    estimated_months: Optional[int] = None,
    skills_covered: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    path = CareerPath(
        name=name, slug=slug, description=description,
        difficulty=difficulty, estimated_months=estimated_months,
        skills_covered=skills_covered,
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return {"id": path.id, "name": path.name}


# --- Admin: Add Certification to Career Path ---

@router.post("/admin/career-paths/{path_id}/certifications")
async def add_cert_to_career_path(
    path_id: int,
    certification_id: int,
    stage: str,
    order_index: int = 0,
    required: bool = False,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    cc = CareerCertification(
        career_path_id=path_id,
        certification_id=certification_id,
        stage=stage,
        order_index=order_index,
        required=required,
    )
    db.add(cc)
    db.commit()
    return {"status": "added"}

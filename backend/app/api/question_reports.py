from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.question_report import QuestionReport
from app.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/questions", tags=["question-reports"])


class ReportRequest(BaseModel):
    question_id: int
    reason: str
    description: Optional[str] = None


@router.post("/report")
async def report_question(
    request: ReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    report = QuestionReport(
        user_id=current_user.id,
        question_id=request.question_id,
        reason=request.reason,
        description=request.description,
    )
    db.add(report)
    db.commit()
    return {"status": "reported", "report_id": report.id}


@router.get("/reports")
async def list_reports(
    status: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    query = db.query(QuestionReport)
    if status:
        query = query.filter(QuestionReport.status == status)
    reports = query.order_by(QuestionReport.created_at.desc()).all()

    return {
        "reports": [
            {
                "id": r.id,
                "question_id": r.question_id,
                "reason": r.reason,
                "description": r.description,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
            }
            for r in reports
        ]
    }


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    report = db.query(QuestionReport).filter(QuestionReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = "resolved"
    report.resolved_at = datetime.utcnow()
    db.commit()
    return {"status": "resolved"}

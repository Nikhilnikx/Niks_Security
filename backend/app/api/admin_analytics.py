from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User, UserRole
from app.models.certification import Certification
from app.models.user_answer import UserAnswer
from app.models.quiz import Quiz, QuizStatus
from app.models.mock_exam import MockExam, MockExamStatus
from app.models.product import Product, Purchase, PurchaseStatus
from app.models.question import Question
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/admin/analytics", tags=["admin-analytics"])


@router.get("/overview")
async def get_overview(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_users = db.query(func.count(User.id)).filter(User.role == UserRole.USER).scalar() or 0
    new_users_week = db.query(func.count(User.id)).filter(
        User.role == UserRole.USER,
        User.created_at >= datetime.combine(week_ago, datetime.min.time()),
    ).scalar() or 0

    total_quizzes = db.query(func.count(Quiz.id)).filter(Quiz.status == QuizStatus.COMPLETED).scalar() or 0
    total_mocks = db.query(func.count(MockExam.id)).filter(MockExam.status == MockExamStatus.COMPLETED).scalar() or 0

    total_purchases = db.query(func.count(Purchase.id)).filter(Purchase.status == PurchaseStatus.PAID).scalar() or 0
    total_revenue = db.query(func.sum(Purchase.amount)).filter(Purchase.status == PurchaseStatus.PAID).scalar() or 0

    return {
        "total_users": total_users,
        "new_users_this_week": new_users_week,
        "total_quizzes": total_quizzes,
        "total_mock_exams": total_mocks,
        "total_premium_purchases": total_purchases,
        "total_revenue": round(total_revenue, 2),
    }


@router.get("/certifications")
async def get_certification_analytics(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    certs = db.query(Certification).filter(Certification.active == True).all()
    result = []
    for c in certs:
        enrolled = db.query(func.count(Quiz.id)).filter(Quiz.certification_id == c.id).scalar() or 0
        avg_score = db.query(func.avg(Quiz.score)).filter(
            Quiz.certification_id == c.id,
            Quiz.status == QuizStatus.COMPLETED,
        ).scalar() or 0

        result.append({
            "id": c.id,
            "name": c.name,
            "code": c.code,
            "quiz_attempts": enrolled,
            "average_score": round(float(avg_score), 1) if avg_score else 0,
        })

    result.sort(key=lambda x: x["quiz_attempts"], reverse=True)
    return {"certifications": result}


@router.get("/revenue")
async def get_revenue_analytics(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    paid = db.query(Purchase).filter(Purchase.status == PurchaseStatus.PAID)

    today_revenue = db.query(func.sum(Purchase.amount)).filter(
        Purchase.status == PurchaseStatus.PAID,
        Purchase.created_at >= datetime.combine(today, datetime.min.time()),
    ).scalar() or 0

    week_revenue = db.query(func.sum(Purchase.amount)).filter(
        Purchase.status == PurchaseStatus.PAID,
        Purchase.created_at >= datetime.combine(week_start, datetime.min.time()),
    ).scalar() or 0

    month_revenue = db.query(func.sum(Purchase.amount)).filter(
        Purchase.status == PurchaseStatus.PAID,
        Purchase.created_at >= datetime.combine(month_start, datetime.min.time()),
    ).scalar() or 0

    return {
        "today": round(float(today_revenue), 2),
        "this_week": round(float(week_revenue), 2),
        "this_month": round(float(month_revenue), 2),
    }


@router.get("/questions/health")
async def get_question_health(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    total = db.query(func.count(Question.id)).scalar() or 0

    # Questions with high error rate
    problematic = db.query(Question).filter(
        Question.attempt_count > 10,
        Question.success_rate < 0.2,
    ).all()

    # Most difficult
    most_difficult = db.query(Question).filter(
        Question.attempt_count > 5,
    ).order_by(Question.success_rate.asc()).limit(10).all()

    return {
        "total_questions": total,
        "problematic_count": len(problematic),
        "most_difficult": [
            {
                "id": q.id,
                "question_text": q.question_text[:100],
                "success_rate": round(q.success_rate * 100, 1),
                "attempt_count": q.attempt_count,
            }
            for q in most_difficult
        ],
    }

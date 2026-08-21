from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.database import get_db
from app.models.user import User
from app.models.activity_log import ActivityLog
from app.models.user_answer import UserAnswer
from app.models.quiz import Quiz, QuizStatus
from app.models.mock_exam import MockExam, MockExamStatus
from app.auth import get_current_user

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.post("/log")
async def log_activity(
    activity_type: str,
    duration_minutes: float = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    existing = db.query(ActivityLog).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.activity_type == activity_type,
        ActivityLog.activity_date == today,
    ).first()

    if existing:
        existing.duration_minutes += duration_minutes
    else:
        log = ActivityLog(
            user_id=current_user.id,
            activity_type=activity_type,
            duration_minutes=duration_minutes,
            activity_date=today,
        )
        db.add(log)

    db.commit()
    return {"status": "logged"}


@router.get("/streak")
async def get_streak(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    logs = db.query(ActivityLog.activity_date).filter(
        ActivityLog.user_id == current_user.id,
    ).distinct().order_by(ActivityLog.activity_date.desc()).all()

    active_dates = {log[0] for log in logs}

    # Calculate current streak
    current_streak = 0
    check_date = today
    while check_date in active_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    # Calculate longest streak
    sorted_dates = sorted(active_dates)
    longest_streak = 0
    streak = 0
    for i, d in enumerate(sorted_dates):
        if i == 0:
            streak = 1
        elif (d - sorted_dates[i - 1]).days == 1:
            streak += 1
        else:
            streak = 1
        longest_streak = max(longest_streak, streak)

    # Weekly activity (last 7 days)
    weekly = {}
    for i in range(7):
        d = today - timedelta(days=i)
        weekly[d.isoformat()] = d in active_dates

    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "weekly_activity": weekly,
    }


@router.get("/statistics")
async def get_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # This week's activity
    week_logs = db.query(func.sum(ActivityLog.duration_minutes)).filter(
        ActivityLog.user_id == current_user.id,
        ActivityLog.activity_date >= week_start,
    ).scalar() or 0

    # This week's questions
    week_questions = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.attempted_at >= datetime.combine(week_start, datetime.min.time()),
    ).scalar() or 0

    week_correct = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.attempted_at >= datetime.combine(week_start, datetime.min.time()),
        UserAnswer.is_correct == True,
    ).scalar() or 0

    # This week's quizzes
    week_quizzes = db.query(func.count(Quiz.id)).filter(
        Quiz.user_id == current_user.id,
        Quiz.status == QuizStatus.COMPLETED,
        Quiz.completed_at >= datetime.combine(week_start, datetime.min.time()),
    ).scalar() or 0

    # This week's mock exams
    week_mocks = db.query(func.count(MockExam.id)).filter(
        MockExam.user_id == current_user.id,
        MockExam.status == MockExamStatus.COMPLETED,
        MockExam.completed_at >= datetime.combine(week_start, datetime.min.time()),
    ).scalar() or 0

    # Total stats
    total_questions = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == current_user.id,
    ).scalar() or 0

    total_correct = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == current_user.id,
        UserAnswer.is_correct == True,
    ).scalar() or 0

    return {
        "this_week": {
            "study_minutes": round(week_logs, 1),
            "questions_attempted": week_questions,
            "accuracy": int((week_correct / week_questions) * 100) if week_questions > 0 else 0,
            "quizzes_completed": week_quizzes,
            "mock_exams_completed": week_mocks,
        },
        "all_time": {
            "total_questions": total_questions,
            "total_correct": total_correct,
            "overall_accuracy": int((total_correct / total_questions) * 100) if total_questions > 0 else 0,
        },
    }


@router.get("/trends")
async def get_performance_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Quiz score trends (last 10 quizzes)
    quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.status == QuizStatus.COMPLETED,
    ).order_by(Quiz.completed_at.desc()).limit(10).all()

    quiz_trends = [
        {
            "id": q.id,
            "score": q.score,
            "date": q.completed_at.isoformat() if q.completed_at else None,
        }
        for q in reversed(quizzes)
    ]

    # Mock exam score trends
    mocks = db.query(MockExam).filter(
        MockExam.user_id == current_user.id,
        MockExam.status == MockExamStatus.COMPLETED,
    ).order_by(MockExam.completed_at.desc()).limit(10).all()

    mock_trends = [
        {
            "id": m.id,
            "score": m.score,
            "date": m.completed_at.isoformat() if m.completed_at else None,
        }
        for m in reversed(mocks)
    ]

    # Daily questions trend (last 14 days)
    today = date.today()
    daily_trends = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        count = db.query(func.count(UserAnswer.id)).filter(
            UserAnswer.user_id == current_user.id,
            UserAnswer.attempted_at >= datetime.combine(d, datetime.min.time()),
            UserAnswer.attempted_at < datetime.combine(d + timedelta(days=1), datetime.min.time()),
        ).scalar() or 0
        daily_trends.append({"date": d.isoformat(), "questions": count})

    return {
        "quiz_trends": quiz_trends,
        "mock_trends": mock_trends,
        "daily_trends": daily_trends,
    }

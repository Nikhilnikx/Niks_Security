from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.user_progress import UserProgress, MasteryScore, ConceptProgress
from app.models.quiz import Quiz, QuizStatus
from app.models.mock_exam import MockExam, MockExamStatus
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.concept import Concept
from app.models.user_answer import UserAnswer
from app.models.study_plan import StudyPlan, StudyPlanItem
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["progress"])


# --- Get Dashboard ---

@router.get("/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get all progress entries
    progress_entries = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()

    total_questions = sum(p.total_questions_attempted for p in progress_entries)
    total_correct = sum(p.correct_answers for p in progress_entries)
    accuracy = int((total_correct / total_questions) * 100) if total_questions > 0 else 0

    # Recent quizzes
    recent_quizzes = db.query(Quiz).filter(
        Quiz.user_id == current_user.id,
        Quiz.status == QuizStatus.COMPLETED,
    ).order_by(Quiz.completed_at.desc()).limit(5).all()

    # Mock exams
    mock_exams = db.query(MockExam).filter(
        MockExam.user_id == current_user.id,
        MockExam.status == MockExamStatus.COMPLETED,
    ).order_by(MockExam.completed_at.desc()).limit(5).all()

    return {
        "total_questions_attempted": total_questions,
        "total_correct": total_correct,
        "accuracy": accuracy,
        "certifications_count": len(progress_entries),
        "recent_quizzes": [
            {
                "id": q.id,
                "quiz_type": q.quiz_type,
                "score": q.score,
                "total_questions": q.total_questions,
                "correct_answers": q.correct_answers,
                "completed_at": q.completed_at.isoformat() if q.completed_at else None,
            }
            for q in recent_quizzes
        ],
        "recent_mock_exams": [
            {
                "id": m.id,
                "score": m.score,
                "total_questions": m.total_questions,
                "correct_answers": m.correct_answers,
                "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            }
            for m in mock_exams
        ],
    }


# --- Get Certification Progress ---

@router.get("/certifications/{certification_id}/progress")
async def get_certification_progress(
    certification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.certification_id == certification_id,
    ).first()

    # Get domain mastery scores
    mastery = db.query(MasteryScore).filter(
        MasteryScore.user_id == current_user.id,
    ).join(Domain).filter(Domain.exam_version_id.in_(
        db.query(func.min(Domain.exam_version_id)).filter(
            Domain.exam_version_id == Domain.exam_version_id
        )
    )).all() if False else []

    # Get mastery by domain
    from app.models.certification import ExamVersion
    exam_version = db.query(ExamVersion).filter(
        ExamVersion.certification_id == certification_id,
    ).first()

    domain_mastery = []
    if exam_version:
        domains = db.query(Domain).filter(Domain.exam_version_id == exam_version.id).all()
        for domain in domains:
            # Calculate mastery from answers
            total_in_domain = db.query(func.count(UserAnswer.id)).join(
                # We need to join through question
            ).filter(
                UserAnswer.user_id == current_user.id,
            ).scalar() if False else 0

            # Simplified: get questions answered in domain
            answered_correct = db.query(func.count(UserAnswer.id)).filter(
                UserAnswer.user_id == current_user.id,
                UserAnswer.is_correct == True,
            ).scalar() or 0

            total_answered = db.query(func.count(UserAnswer.id)).filter(
                UserAnswer.user_id == current_user.id,
            ).scalar() or 0

            domain_mastery.append({
                "domain_id": domain.id,
                "domain_name": domain.name,
                "weight_percentage": domain.weight_percentage,
                "mastery": 0,  # Will be calculated properly
            })

    # Get weak areas (topics with low accuracy)
    weak_topics = []
    from app.models.question import Question
    topics = db.query(Topic).join(Domain).filter(
        Domain.exam_version_id == exam_version.id if exam_version else True
    ).all()

    for topic in topics:
        total = db.query(func.count(Question.id)).filter(
            Question.topic_id == topic.id,
        ).scalar() or 0
        if total > 0:
            # Count correct answers for this topic
            topic_question_ids = [q.id for q in db.query(Question.id).filter(Question.topic_id == topic.id).all()]
            correct = db.query(func.count(UserAnswer.id)).filter(
                UserAnswer.user_id == current_user.id,
                UserAnswer.question_id.in_(topic_question_ids),
                UserAnswer.is_correct == True,
            ).scalar() or 0

            accuracy = int((correct / total) * 100) if total > 0 else 0
            if accuracy < 70:
                weak_topics.append({
                    "topic_id": topic.id,
                    "topic_name": topic.name,
                    "accuracy": accuracy,
                })

    overall_accuracy = int((total_correct / total_questions) * 100) if total_questions > 0 else 0

    return {
        "certification_id": certification_id,
        "total_questions_attempted": progress.total_questions_attempted if progress else 0,
        "correct_answers": progress.correct_answers if progress else 0,
        "accuracy": overall_accuracy,
        "concepts_completed": progress.concepts_completed if progress else 0,
        "total_concepts": progress.total_concepts if progress else 0,
        "weak_areas": weak_topics[:5],
        "domain_mastery": domain_mastery,
    }


# --- Readiness Score ---

@router.get("/readiness/{certification_id}")
async def get_readiness_score(
    certification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.certification_id == certification_id,
    ).first()

    total_questions = progress.total_questions_attempted if progress else 0
    total_correct = progress.correct_answers if progress else 0

    # Knowledge mastery (accuracy)
    knowledge_mastery = int((total_correct / total_questions) * 100) if total_questions > 0 else 0

    # Practice accuracy (last 50 questions)
    recent_answers = db.query(UserAnswer).filter(
        UserAnswer.user_id == current_user.id,
    ).order_by(UserAnswer.attempted_at.desc()).limit(50).all()

    recent_correct = sum(1 for a in recent_answers if a.is_correct)
    practice_accuracy = int((recent_correct / len(recent_answers)) * 100) if recent_answers else 0

    # Mock exam performance
    mock_exams = db.query(MockExam).filter(
        MockExam.user_id == current_user.id,
        MockExam.certification_id == certification_id,
        MockExam.status == MockExamStatus.COMPLETED,
    ).all()

    mock_performance = int(sum(m.score for m in mock_exams) / len(mock_exams)) if mock_exams else 0

    # Retention (consistency of performance)
    retention = min(knowledge_mastery, practice_accuracy) if total_questions > 0 else 0

    # Overall readiness
    if total_questions == 0:
        overall = 0
        status = "Not Started"
    else:
        overall = int(
            knowledge_mastery * 0.3 +
            practice_accuracy * 0.3 +
            mock_performance * 0.25 +
            retention * 0.15
        )
        if overall >= 85:
            status = "Ready"
        elif overall >= 70:
            status = "Almost Ready"
        elif overall >= 50:
            status = "Learning"
        elif overall >= 20:
            status = "Beginner"
        else:
            status = "Not Started"

    return {
        "knowledge_mastery": knowledge_mastery,
        "practice_accuracy": practice_accuracy,
        "mock_performance": mock_performance,
        "retention": retention,
        "overall_readiness": overall,
        "status": status,
        "disclaimer": "Niksmind's readiness score is an internal preparation indicator and does not guarantee passing the actual certification exam.",
    }


# --- Weak Areas ---

@router.get("/weak-areas/{certification_id}")
async def get_weak_areas(
    certification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.certification import ExamVersion
    from app.models.question import Question

    exam_version = db.query(ExamVersion).filter(
        ExamVersion.certification_id == certification_id,
    ).first()
    if not exam_version:
        return {"weak_areas": []}

    domains = db.query(Domain).filter(Domain.exam_version_id == exam_version.id).all()
    weak_areas = []

    for domain in domains:
        topics = db.query(Topic).filter(Topic.domain_id == domain.id).all()
        for topic in topics:
            topic_questions = db.query(Question).filter(Question.topic_id == topic.id).all()
            if not topic_questions:
                continue

            topic_q_ids = [q.id for q in topic_questions]
            total = db.query(func.count(UserAnswer.id)).filter(
                UserAnswer.user_id == current_user.id,
                UserAnswer.question_id.in_(topic_q_ids),
            ).scalar() or 0

            if total == 0:
                continue

            correct = db.query(func.count(UserAnswer.id)).filter(
                UserAnswer.user_id == current_user.id,
                UserAnswer.question_id.in_(topic_q_ids),
                UserAnswer.is_correct == True,
            ).scalar() or 0

            accuracy = int((correct / total) * 100) if total > 0 else 0

            weak_areas.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "domain_name": domain.name,
                "accuracy": accuracy,
                "questions_attempted": total,
            })

    weak_areas.sort(key=lambda x: x["accuracy"])

    return {"weak_areas": weak_areas[:10]}


# --- Study Plan ---

@router.post("/study-plan")
async def create_study_plan(
    certification_id: int,
    exam_date: str,
    daily_hours: int = 2,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get topics for certification
    from app.models.certification import ExamVersion
    exam_version = db.query(ExamVersion).filter(
        ExamVersion.certification_id == certification_id,
    ).first()
    if not exam_version:
        raise HTTPException(status_code=404, detail="No exam version found")

    domains = db.query(Domain).filter(Domain.exam_version_id == exam_version.id).all()

    # Build study plan
    all_topics = []
    for domain in domains:
        topics = db.query(Topic).filter(Topic.domain_id == domain.id).all()
        for topic in topics:
            all_topics.append({
                "topic_id": topic.id,
                "topic_name": topic.name,
                "domain_name": domain.name,
                "weight": domain.weight_percentage,
            })

    # Sort by weight (study higher-weight topics first)
    all_topics.sort(key=lambda x: x["weight"], reverse=True)

    # Calculate days available
    try:
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    today = date.today()
    days_available = max(1, (exam_dt - today).days)

    # Create plan
    plan = StudyPlan(
        user_id=current_user.id,
        certification_id=certification_id,
        exam_date=exam_dt,
        daily_hours=daily_hours,
    )
    db.add(plan)
    db.flush()

    # Distribute topics across days
    for i, topic in enumerate(all_topics):
        day_number = (i % days_available) + 1
        item = StudyPlanItem(
            study_plan_id=plan.id,
            day_number=day_number,
            topic_name=topic["topic_name"],
            topic_id=topic["topic_id"],
            description=f"Study {topic['topic_name']} from {topic['domain_name']}",
        )
        db.add(item)

    db.commit()
    db.refresh(plan)

    # Group by day
    items = db.query(StudyPlanItem).filter(StudyPlanItem.study_plan_id == plan.id).order_by(StudyPlanItem.day_number).all()
    daily_plan = {}
    for item in items:
        if item.day_number not in daily_plan:
            daily_plan[item.day_number] = []
        daily_plan[item.day_number].append({
            "topic_name": item.topic_name,
            "description": item.description,
            "completed": item.completed,
        })

    return {
        "id": plan.id,
        "exam_date": exam_date,
        "daily_hours": daily_hours,
        "total_days": days_available,
        "plan": {f"Day {k}": v for k, v in daily_plan.items()},
    }


@router.get("/study-plan")
async def get_study_plan(
    certification_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id)
    if certification_id:
        query = query.filter(StudyPlan.certification_id == certification_id)

    plan = query.order_by(StudyPlan.created_at.desc()).first()
    if not plan:
        return {"plan": None}

    items = db.query(StudyPlanItem).filter(
        StudyPlanItem.study_plan_id == plan.id
    ).order_by(StudyPlanItem.day_number).all()

    daily_plan = {}
    for item in items:
        if item.day_number not in daily_plan:
            daily_plan[item.day_number] = []
        daily_plan[item.day_number].append({
            "topic_name": item.topic_name,
            "description": item.description,
            "completed": item.completed,
        })

    return {
        "id": plan.id,
        "exam_date": plan.exam_date.isoformat() if plan.exam_date else None,
        "daily_hours": plan.daily_hours,
        "plan": {f"Day {k}": v for k, v in daily_plan.items()},
    }

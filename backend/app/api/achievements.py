from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement, UserGamification
from app.models.user_answer import UserAnswer
from app.models.quiz import Quiz, QuizStatus
from app.models.mock_exam import MockExam, MockExamStatus
from app.auth import get_current_user

router = APIRouter(prefix="/api/achievements", tags=["achievements"])

# Level thresholds
LEVELS = {
    1: 0, 2: 100, 3: 250, 4: 500, 5: 800,
    6: 1200, 7: 1700, 8: 2300, 9: 3000, 10: 4000,
    11: 5200, 12: 6500, 13: 8000, 14: 10000, 15: 12500,
}

LEVEL_TITLES = {
    1: "Newcomer", 2: "Learner", 3: "Student", 4: "Scholar", 5: "Practitioner",
    6: "Specialist", 7: "Expert", 8: "Master", 9: "Grandmaster", 10: "Legend",
    11: "Cloud Apprentice", 12: "Cloud Engineer", 13: "Cloud Architect",
    14: "Cloud Guru", 15: "Certification Champion",
}


def calculate_level(xp: int) -> tuple[int, str]:
    level = 1
    for lvl, threshold in sorted(LEVELS.items()):
        if xp >= threshold:
            level = lvl
    title = LEVEL_TITLES.get(level, "Newcomer")
    return level, title


def check_and_award_achievements(user_id: int, db: Session):
    """Check if user qualifies for any new achievements."""
    gamification = db.query(UserGamification).filter(UserGamification.user_id == user_id).first()
    if not gamification:
        gamification = UserGamification(user_id=user_id)
        db.add(gamification)
        db.flush()

    # Count user stats
    total_answers = db.query(func.count(UserAnswer.id)).filter(UserAnswer.user_id == user_id).scalar() or 0
    correct_answers = db.query(func.count(UserAnswer.id)).filter(
        UserAnswer.user_id == user_id, UserAnswer.is_correct == True
    ).scalar() or 0
    total_quizzes = db.query(func.count(Quiz.id)).filter(
        Quiz.user_id == user_id, Quiz.status == QuizStatus.COMPLETED
    ).scalar() or 0
    perfect_quizzes = db.query(func.count(Quiz.id)).filter(
        Quiz.user_id == user_id, Quiz.status == QuizStatus.COMPLETED, Quiz.score == 100
    ).scalar() or 0
    total_mocks = db.query(func.count(MockExam.id)).filter(
        MockExam.user_id == user_id, MockExam.status == MockExamStatus.COMPLETED
    ).scalar() or 0

    # Get all achievements
    achievements = db.query(Achievement).all()
    existing = {ua.achievement_id for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()}
    newly_unlocked = []

    for ach in achievements:
        if ach.id in existing:
            continue

        value = 0
        if ach.requirement_type == "questions_answered":
            value = total_answers
        elif ach.requirement_type == "correct_answers":
            value = correct_answers
        elif ach.requirement_type == "quizzes_completed":
            value = total_quizzes
        elif ach.requirement_type == "perfect_quizzes":
            value = perfect_quizzes
        elif ach.requirement_type == "mock_exams":
            value = total_mocks

        if value >= ach.requirement_value:
            ua = UserAchievement(user_id=user_id, achievement_id=ach.id)
            db.add(ua)
            gamification.total_xp += ach.xp_reward
            newly_unlocked.append({"name": ach.name, "xp": ach.xp_reward})

    # Update level
    level, title = calculate_level(gamification.total_xp)
    gamification.level = level
    gamification.title = title

    db.commit()
    return newly_unlocked


@router.get("/")
async def list_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    achievements = db.query(Achievement).all()
    unlocked = {ua.achievement_id: ua.unlocked_at for ua in
                db.query(UserAchievement).filter(UserAchievement.user_id == current_user.id).all()}
    gamification = db.query(UserGamification).filter(UserGamification.user_id == current_user.id).first()

    return {
        "achievements": [
            {
                "id": a.id,
                "name": a.name,
                "description": a.description,
                "icon": a.icon,
                "category": a.category,
                "xp_reward": a.xp_reward,
                "unlocked": a.id in unlocked,
                "unlocked_at": unlocked[a.id].isoformat() if a.id in unlocked else None,
            }
            for a in achievements
        ],
        "gamification": {
            "total_xp": gamification.total_xp if gamification else 0,
            "level": gamification.level if gamification else 1,
            "title": gamification.title if gamification else "Newcomer",
        } if gamification else None,
    }


@router.post("/check")
async def check_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    newly_unlocked = check_and_award_achievements(current_user.id, db)
    return {"newly_unlocked": newly_unlocked}

from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.models.flashcard import UserFlashcard
from app.models.study_plan import StudyPlan
from app.models.user_progress import UserProgress
from app.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.get("/")
async def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.read == False)
    notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False,
    ).count()

    return {
        "notifications": [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "link": n.link,
                "read": n.read,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ],
        "unread_count": unread_count,
    }


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    n.read = True
    db.commit()
    return {"status": "read"}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.read == False,
    ).update({"read": True})
    db.commit()
    return {"status": "all_read"}


@router.post("/generate")
async def generate_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate notifications based on user's current state."""
    today = date.today()
    created = 0

    # Flashcard due notifications
    now = datetime.utcnow()
    due_cards = db.query(UserFlashcard).filter(
        UserFlashcard.user_id == current_user.id,
        (UserFlashcard.next_review != None) & (UserFlashcard.next_review <= now),
    ).count()

    if due_cards > 0:
        existing = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.type == "flashcard_due",
            Notification.created_at >= datetime.combine(today, datetime.min.time()),
        ).first()
        if not existing:
            n = Notification(
                user_id=current_user.id,
                type="flashcard_due",
                title=f"You have {due_cards} flashcards due today",
                message="Review your flashcards to maintain your spaced repetition schedule.",
                link="/flashcards",
            )
            db.add(n)
            created += 1

    # Study plan reminders
    plans = db.query(StudyPlan).filter(StudyPlan.user_id == current_user.id).all()
    for plan in plans:
        if plan.exam_date:
            days_left = (plan.exam_date - today).days
            if days_left in [7, 3, 1]:
                existing = db.query(Notification).filter(
                    Notification.user_id == current_user.id,
                    Notification.type == "exam_countdown",
                    Notification.message.contains(f"{days_left} days"),
                ).first()
                if not existing:
                    n = Notification(
                        user_id=current_user.id,
                        type="exam_countdown",
                        title=f"Your exam is in {days_left} days",
                        message=f"You have {days_left} days remaining. Keep up your preparation!",
                        link="/dashboard",
                    )
                    db.add(n)
                    created += 1

    # Inactivity reminder (no activity in 3 days)
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).first()
    if progress and progress.last_activity:
        days_inactive = (datetime.utcnow() - progress.last_activity).days
        if days_inactive >= 3:
            existing = db.query(Notification).filter(
                Notification.user_id == current_user.id,
                Notification.type == "study_reminder",
                Notification.created_at >= datetime.combine(today, datetime.min.time()),
            ).first()
            if not existing:
                n = Notification(
                    user_id=current_user.id,
                    type="study_reminder",
                    title="You haven't studied in a while",
                    message=f"It's been {days_inactive} days. Even 15 minutes a day helps!",
                    link="/dashboard",
                )
                db.add(n)
                created += 1

    db.commit()
    return {"generated": created}

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.flashcard import Flashcard, UserFlashcard
from app.models.concept import Concept
from app.models.user import User
from app.auth import get_current_user

router = APIRouter(prefix="/api/flashcards", tags=["flashcards"])


class CreateFlashcardRequest(BaseModel):
    concept_id: Optional[int] = None
    front: str
    back: str


class ReviewFlashcardRequest(BaseModel):
    flashcard_id: int
    confidence: float  # 0.0 to 1.0


# --- Get Flashcards for a Concept ---

@router.get("/concept/{concept_id}")
async def get_concept_flashcards(
    concept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get system flashcards
    system_flashcards = db.query(Flashcard).filter(
        Flashcard.concept_id == concept_id,
    ).all()

    # Get user flashcards
    user_flashcards = db.query(UserFlashcard).filter(
        UserFlashcard.user_id == current_user.id,
        UserFlashcard.concept_id == concept_id if hasattr(UserFlashcard, 'concept_id') else True,
    ).all()

    return {
        "flashcards": [
            {
                "id": f.id,
                "front": f.front,
                "back": f.back,
                "type": "system",
            }
            for f in system_flashcards
        ] + [
            {
                "id": f.id,
                "front": f.front,
                "back": f.back,
                "type": "user" if f.is_user_created else "ai_generated",
                "confidence": f.confidence,
                "review_count": f.review_count,
                "next_review": f.next_review.isoformat() if f.next_review else None,
            }
            for f in user_flashcards
        ],
    }


# --- Get Flashcards Due for Review ---

@router.get("/review")
async def get_flashcards_for_review(
    certification_id: Optional[int] = None,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    now = datetime.utcnow()
    flashcards = db.query(UserFlashcard).filter(
        UserFlashcard.user_id == current_user.id,
    ).filter(
        (UserFlashcard.next_review == None) | (UserFlashcard.next_review <= now)
    ).order_by(UserFlashcard.next_review.asc().nullslast()).limit(limit).all()

    return {
        "flashcards": [
            {
                "id": f.id,
                "front": f.front,
                "back": f.back,
                "confidence": f.confidence,
                "review_count": f.review_count,
                "next_review": f.next_review.isoformat() if f.next_review else None,
            }
            for f in flashcards
        ],
        "total": len(flashcards),
    }


# --- Create User Flashcard ---

@router.post("/")
async def create_flashcard(
    request: CreateFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flashcard = UserFlashcard(
        user_id=current_user.id,
        front=request.front,
        back=request.back,
        is_user_created=1,
    )
    db.add(flashcard)
    db.commit()
    db.refresh(flashcard)

    return {
        "id": flashcard.id,
        "front": flashcard.front,
        "back": flashcard.back,
        "type": "user",
    }


# --- Review Flashcard (Spaced Repetition) ---

@router.post("/review")
async def review_flashcard(
    request: ReviewFlashcardRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flashcard = db.query(UserFlashcard).filter(
        UserFlashcard.id == request.flashcard_id,
        UserFlashcard.user_id == current_user.id,
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    # Update confidence
    flashcard.confidence = request.confidence
    flashcard.review_count += 1
    flashcard.last_reviewed = datetime.utcnow()

    # Calculate next review using simple spaced repetition
    if request.confidence >= 0.8:
        # High confidence: review in 7 days
        flashcard.next_review = datetime.utcnow() + timedelta(days=7)
    elif request.confidence >= 0.5:
        # Medium confidence: review in 3 days
        flashcard.next_review = datetime.utcnow() + timedelta(days=3)
    else:
        # Low confidence: review tomorrow
        flashcard.next_review = datetime.utcnow() + timedelta(days=1)

    db.commit()

    return {
        "id": flashcard.id,
        "confidence": flashcard.confidence,
        "review_count": flashcard.review_count,
        "next_review": flashcard.next_review.isoformat(),
    }


# --- Delete Flashcard ---

@router.delete("/{flashcard_id}")
async def delete_flashcard(
    flashcard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    flashcard = db.query(UserFlashcard).filter(
        UserFlashcard.id == flashcard_id,
        UserFlashcard.user_id == current_user.id,
    ).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    db.delete(flashcard)
    db.commit()

    return {"status": "deleted"}

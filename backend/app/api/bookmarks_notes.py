from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.models.user_note import UserNote
from app.models.concept import Concept
from app.auth import get_current_user

router = APIRouter(prefix="/api", tags=["bookmarks-notes"])


class BookmarkRequest(BaseModel):
    entity_type: str  # concept, question, resource, flashcard
    entity_id: int


class NoteRequest(BaseModel):
    concept_id: int
    content: str


# --- Bookmarks ---

@router.post("/bookmarks")
async def toggle_bookmark(
    request: BookmarkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.entity_type == request.entity_type,
        Bookmark.entity_id == request.entity_id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"bookmarked": False}
    else:
        bookmark = Bookmark(
            user_id=current_user.id,
            entity_type=request.entity_type,
            entity_id=request.entity_id,
        )
        db.add(bookmark)
        db.commit()
        return {"bookmarked": True}


@router.get("/bookmarks")
async def list_bookmarks(
    entity_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Bookmark).filter(Bookmark.user_id == current_user.id)
    if entity_type:
        query = query.filter(Bookmark.entity_type == entity_type)

    bookmarks = query.order_by(Bookmark.created_at.desc()).all()

    result = []
    for b in bookmarks:
        entity = None
        if b.entity_type == "concept":
            c = db.query(Concept).filter(Concept.id == b.entity_id).first()
            if c:
                entity = {"id": c.id, "name": c.name, "slug": c.slug, "short_definition": c.short_definition}

        result.append({
            "id": b.id,
            "entity_type": b.entity_type,
            "entity_id": b.entity_id,
            "entity": entity,
            "created_at": b.created_at.isoformat(),
        })

    return {"bookmarks": result}


@router.delete("/bookmarks/{bookmark_id}")
async def delete_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id,
    ).first()
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    db.delete(bookmark)
    db.commit()
    return {"status": "deleted"}


# --- Notes ---

@router.post("/notes")
async def create_or_update_note(
    request: NoteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(UserNote).filter(
        UserNote.user_id == current_user.id,
        UserNote.concept_id == request.concept_id,
    ).first()

    if existing:
        existing.content = request.content
        existing.updated_at = datetime.utcnow()
        db.commit()
        return {"id": existing.id, "content": existing.content, "updated": True}
    else:
        note = UserNote(
            user_id=current_user.id,
            concept_id=request.concept_id,
            content=request.content,
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return {"id": note.id, "content": note.content, "updated": False}


@router.get("/notes")
async def list_notes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = db.query(UserNote).filter(
        UserNote.user_id == current_user.id
    ).order_by(UserNote.updated_at.desc()).all()

    result = []
    for n in notes:
        concept = db.query(Concept).filter(Concept.id == n.concept_id).first()
        result.append({
            "id": n.id,
            "concept_id": n.concept_id,
            "concept_name": concept.name if concept else None,
            "content": n.content,
            "created_at": n.created_at.isoformat(),
            "updated_at": n.updated_at.isoformat(),
        })

    return {"notes": result}


@router.get("/notes/concept/{concept_id}")
async def get_concept_note(
    concept_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(UserNote).filter(
        UserNote.user_id == current_user.id,
        UserNote.concept_id == concept_id,
    ).first()

    if not note:
        return {"note": None}

    return {
        "note": {
            "id": note.id,
            "content": note.content,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat(),
        }
    }


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    note = db.query(UserNote).filter(
        UserNote.id == note_id,
        UserNote.user_id == current_user.id,
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(note)
    db.commit()
    return {"status": "deleted"}

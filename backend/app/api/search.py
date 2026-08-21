from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.provider import Provider
from app.models.certification import Certification
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.concept import Concept
from app.models.question import Question
from app.models.learning_resource import LearningResource
from app.models.document import Document
from app.models.user import User
from app.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/")
async def global_search(
    q: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    if not q or len(q.strip()) < 2:
        return {"results": []}

    search_term = f"%{q.strip()}%"
    results = []

    # Search providers
    providers = db.query(Provider).filter(
        Provider.name.ilike(search_term),
        Provider.active == True,
    ).limit(5).all()
    for p in providers:
        results.append({
            "type": "provider",
            "id": p.id,
            "name": p.name,
            "slug": p.slug,
            "description": p.description,
        })

    # Search certifications
    certs = db.query(Certification).filter(
        or_(
            Certification.name.ilike(search_term),
            Certification.code.ilike(search_term),
        ),
        Certification.active == True,
    ).limit(10).all()
    for c in certs:
        results.append({
            "type": "certification",
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "code": c.code,
            "level": c.level.value if c.level else None,
        })

    # Search concepts
    concepts = db.query(Concept).filter(
        or_(
            Concept.name.ilike(search_term),
            Concept.short_definition.ilike(search_term),
        ),
    ).limit(10).all()
    for c in concepts:
        results.append({
            "type": "concept",
            "id": c.id,
            "name": c.name,
            "slug": c.slug,
            "description": c.short_definition,
        })

    # Search topics
    topics = db.query(Topic).filter(
        Topic.name.ilike(search_term),
    ).limit(10).all()
    for t in topics:
        results.append({
            "type": "topic",
            "id": t.id,
            "name": t.name,
            "slug": t.slug,
        })

    # Search questions
    questions = db.query(Question).filter(
        Question.question_text.ilike(search_term),
    ).limit(5).all()
    for q in questions:
        results.append({
            "type": "question",
            "id": q.id,
            "name": q.question_text[:100],
            "difficulty": q.difficulty.value if q.difficulty else None,
        })

    return {"results": results}

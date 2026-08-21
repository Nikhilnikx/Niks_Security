import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import User, UserRole
from app.models.provider import Provider
from app.models.certification import Certification, ExamVersion, ExamVersionStatus
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.concept import Concept
from app.models.question import Question, QuestionOption, AccessLevel, QuestionType, QuestionDifficulty
from app.models.learning_resource import LearningResource, ResourceType
from app.models.flashcard import Flashcard
from app.models.product import Product, ProductType
from app.auth import get_current_admin_user

router = APIRouter(prefix="/api/admin", tags=["admin"])


# --- Provider CRUD ---

@router.post("/providers")
async def create_provider(
    name: str,
    slug: str,
    description: Optional[str] = None,
    logo: Optional[str] = None,
    website_url: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    provider = Provider(
        name=name, slug=slug, description=description,
        logo=logo, website_url=website_url,
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return {"id": provider.id, "name": provider.name, "slug": provider.slug}


# --- Certification CRUD ---

@router.post("/certifications")
async def create_certification(
    provider_id: int,
    name: str,
    slug: str,
    code: str,
    description: Optional[str] = None,
    level: str = "beginner",
    category: str = "cloud",
    estimated_hours: Optional[int] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    cert = Certification(
        provider_id=provider_id, name=name, slug=slug, code=code,
        description=description, level=level, category=category,
        estimated_hours=estimated_hours,
    )
    db.add(cert)
    db.commit()
    db.refresh(cert)
    return {"id": cert.id, "name": cert.name, "slug": cert.slug}


# --- Exam Version CRUD ---

@router.post("/exam-versions")
async def create_exam_version(
    certification_id: int,
    version: str,
    effective_date: Optional[str] = None,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    ev = ExamVersion(
        certification_id=certification_id, version=version,
        status=ExamVersionStatus.DRAFT,
    )
    if effective_date:
        from datetime import datetime
        ev.effective_date = datetime.strptime(effective_date, "%Y-%m-%d")
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return {"id": ev.id, "version": ev.version, "status": ev.status.value}


@router.post("/exam-versions/{version_id}/publish")
async def publish_exam_version(
    version_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    ev = db.query(ExamVersion).filter(ExamVersion.id == version_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Exam version not found")

    # Archive other active versions
    db.query(ExamVersion).filter(
        ExamVersion.certification_id == ev.certification_id,
        ExamVersion.status == ExamVersionStatus.ACTIVE,
    ).update({"status": ExamVersionStatus.ARCHIVED})

    ev.status = ExamVersionStatus.ACTIVE
    db.commit()
    return {"id": ev.id, "status": ev.status.value}


# --- Domain CRUD ---

@router.post("/domains")
async def create_domain(
    exam_version_id: int,
    name: str,
    description: Optional[str] = None,
    weight_percentage: float = 0,
    order_index: int = 0,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    domain = Domain(
        exam_version_id=exam_version_id, name=name,
        description=description, weight_percentage=weight_percentage,
        order_index=order_index,
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return {"id": domain.id, "name": domain.name}


# --- Topic CRUD ---

@router.post("/topics")
async def create_topic(
    domain_id: int,
    name: str,
    slug: str,
    description: Optional[str] = None,
    order_index: int = 0,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    topic = Topic(
        domain_id=domain_id, name=name, slug=slug,
        description=description, order_index=order_index,
    )
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return {"id": topic.id, "name": topic.name, "slug": topic.slug}


# --- Concept CRUD ---

@router.post("/concepts")
async def create_concept(
    topic_id: int,
    name: str,
    slug: str,
    short_definition: Optional[str] = None,
    simple_explanation: Optional[str] = None,
    detailed_explanation: Optional[str] = None,
    examples: Optional[str] = None,
    key_points: Optional[str] = None,
    exam_tips: Optional[str] = None,
    common_mistakes: Optional[str] = None,
    difficulty: str = "medium",
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    concept = Concept(
        topic_id=topic_id, name=name, slug=slug,
        short_definition=short_definition,
        simple_explanation=simple_explanation,
        detailed_explanation=detailed_explanation,
        examples=examples, key_points=key_points,
        exam_tips=exam_tips, common_mistakes=common_mistakes,
        difficulty=difficulty,
    )
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return {"id": concept.id, "name": concept.name}


# --- Question CRUD ---

@router.post("/questions")
async def create_question(
    exam_version_id: int,
    domain_id: int,
    topic_id: int,
    question_text: str,
    question_type: str = "single_choice",
    difficulty: str = "medium",
    access_level: str = "FREE",
    explanation: Optional[str] = None,
    concept_id: Optional[int] = None,
    options: List[dict] = [],
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    question = Question(
        exam_version_id=exam_version_id, domain_id=domain_id,
        topic_id=topic_id, concept_id=concept_id,
        question_text=question_text, question_type=question_type,
        difficulty=difficulty, access_level=access_level,
        explanation=explanation, source_type="admin",
    )
    db.add(question)
    db.flush()

    for opt in options:
        qo = QuestionOption(
            question_id=question.id,
            option_text=opt["text"],
            is_correct=opt.get("is_correct", False),
        )
        db.add(qo)

    db.commit()
    db.refresh(question)
    return {"id": question.id}


# --- Bulk Import ---

@router.post("/import/json")
async def import_json(
    data: dict,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Import certification data from JSON."""
    errors = []
    created = 0

    try:
        provider_name = data.get("provider", "")
        provider_slug = provider_name.lower().replace(" ", "-")

        # Get or create provider
        provider = db.query(Provider).filter(Provider.slug == provider_slug).first()
        if not provider:
            provider = Provider(name=provider_name, slug=provider_slug)
            db.add(provider)
            db.flush()

        # Create certification
        cert_data = data.get("certification", {})
        cert = Certification(
            provider_id=provider.id,
            name=cert_data.get("name", ""),
            slug=cert_data.get("slug", ""),
            code=cert_data.get("code", ""),
            description=cert_data.get("description", ""),
            level=cert_data.get("level", "beginner"),
            category=cert_data.get("category", "cloud"),
        )
        db.add(cert)
        db.flush()
        created += 1

        # Create exam version
        version = ExamVersion(
            certification_id=cert.id,
            version=data.get("exam_version", "2026"),
            status=ExamVersionStatus.DRAFT,
        )
        db.add(version)
        db.flush()

        # Import domains
        for domain_data in data.get("domains", []):
            domain = Domain(
                exam_version_id=version.id,
                name=domain_data.get("name", ""),
                description=domain_data.get("description", ""),
                weight_percentage=domain_data.get("weight_percentage", 0),
                order_index=domain_data.get("order_index", 0),
            )
            db.add(domain)
            db.flush()

            # Import topics
            for topic_data in domain_data.get("topics", []):
                topic = Topic(
                    domain_id=domain.id,
                    name=topic_data.get("name", ""),
                    slug=topic_data.get("slug", ""),
                    description=topic_data.get("description", ""),
                    order_index=topic_data.get("order_index", 0),
                )
                db.add(topic)

        db.commit()
        return {"status": "success", "created": created, "errors": errors}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")


# --- Content Validation ---

@router.get("/validate/{exam_version_id}")
async def validate_content(
    exam_version_id: int,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    errors = []

    # Check domains
    domains = db.query(Domain).filter(Domain.exam_version_id == exam_version_id).all()
    if not domains:
        errors.append("No domains found")

    total_weight = sum(d.weight_percentage for d in domains)
    if abs(total_weight - 100) > 1:
        errors.append(f"Domain weights sum to {total_weight}%, expected ~100%")

    # Check questions
    questions = db.query(Question).filter(Question.exam_version_id == exam_version_id).all()
    if not questions:
        errors.append("No questions found")

    # Validate each question
    for q in questions:
        options = db.query(QuestionOption).filter(QuestionOption.question_id == q.id).all()
        if len(options) < 2:
            errors.append(f"Question {q.id}: Less than 2 options")
        correct = [o for o in options if o.is_correct]
        if len(correct) != 1:
            errors.append(f"Question {q.id}: Must have exactly 1 correct answer")
        if not q.explanation:
            errors.append(f"Question {q.id}: Missing explanation")

    return {"valid": len(errors) == 0, "errors": errors}

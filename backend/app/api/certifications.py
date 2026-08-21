from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.provider import Provider
from app.models.certification import Certification, ExamVersion
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.concept import Concept
from app.models.learning_resource import LearningResource
from app.models.user import User
from app.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api", tags=["certifications"])


# --- Response Models ---

class ProviderResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    logo: Optional[str]
    website_url: Optional[str]

    class Config:
        from_attributes = True


class CertificationBrief(BaseModel):
    id: int
    name: str
    slug: str
    code: str
    level: str
    category: str
    estimated_hours: Optional[int]

    class Config:
        from_attributes = True


class CertificationDetail(BaseModel):
    id: int
    name: str
    slug: str
    code: str
    description: Optional[str]
    level: str
    category: str
    estimated_hours: Optional[int]
    provider: ProviderResponse
    exam_versions: list

    class Config:
        from_attributes = True


class TopicResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]

    class Config:
        from_attributes = True


class DomainResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    weight_percentage: float
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True


class ConceptResponse(BaseModel):
    id: int
    name: str
    slug: str
    short_definition: Optional[str]
    simple_explanation: Optional[str]
    detailed_explanation: Optional[str]
    examples: Optional[str]
    key_points: Optional[str]
    exam_tips: Optional[str]
    common_mistakes: Optional[str]
    difficulty: Optional[str]

    class Config:
        from_attributes = True


class LearningResourceResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    url: Optional[str]
    source: Optional[str]
    resource_type: str
    is_official: bool

    class Config:
        from_attributes = True


# --- Provider Routes ---

@router.get("/providers", response_model=List[ProviderResponse])
async def get_providers(db: Session = Depends(get_db)):
    providers = db.query(Provider).filter(Provider.active == True).all()
    return providers


@router.get("/providers/{slug}")
async def get_provider(slug: str, db: Session = Depends(get_db)):
    provider = db.query(Provider).filter(Provider.slug == slug).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    certs = db.query(Certification).filter(
        Certification.provider_id == provider.id,
        Certification.active == True
    ).all()
    return {
        "id": provider.id,
        "name": provider.name,
        "slug": provider.slug,
        "description": provider.description,
        "logo": provider.logo,
        "website_url": provider.website_url,
        "certifications": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "code": c.code,
                "level": c.level.value if c.level else None,
                "category": c.category,
                "estimated_hours": c.estimated_hours,
            }
            for c in certs
        ],
    }


# --- Certification Routes ---

@router.get("/certifications", response_model=List[CertificationBrief])
async def get_certifications(
    provider: Optional[str] = None,
    category: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Certification).filter(Certification.active == True)
    if provider:
        prov = db.query(Provider).filter(Provider.slug == provider).first()
        if prov:
            query = query.filter(Certification.provider_id == prov.id)
    if category:
        query = query.filter(Certification.category == category)
    if level:
        query = query.filter(Certification.level == level)
    return query.all()


@router.get("/certifications/{slug}")
async def get_certification(slug: str, db: Session = Depends(get_db)):
    cert = db.query(Certification).options(
        joinedload(Certification.provider),
        joinedload(Certification.exam_versions).joinedload(ExamVersion.domains).joinedload(Domain.topics),
    ).filter(Certification.slug == slug).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certification not found")

    active_version = None
    for ev in cert.exam_versions:
        if ev.status.value == "active":
            active_version = ev
            break
    if not active_version and cert.exam_versions:
        active_version = cert.exam_versions[0]

    return {
        "id": cert.id,
        "name": cert.name,
        "slug": cert.slug,
        "code": cert.code,
        "description": cert.description,
        "level": cert.level.value if cert.level else None,
        "category": cert.category,
        "estimated_hours": cert.estimated_hours,
        "provider": {
            "id": cert.provider.id,
            "name": cert.provider.name,
            "slug": cert.provider.slug,
        },
        "exam_version": {
            "id": active_version.id,
            "version": active_version.version,
            "status": active_version.status.value,
            "domains": [
                {
                    "id": d.id,
                    "name": d.name,
                    "description": d.description,
                    "weight_percentage": d.weight_percentage,
                    "topics": [
                        {"id": t.id, "name": t.name, "slug": t.slug}
                        for t in d.topics
                    ]
                }
                for d in active_version.domains
            ] if active_version else [],
        } if active_version else None,
    }


# --- Domain Routes ---

@router.get("/domains/{domain_id}")
async def get_domain(domain_id: int, db: Session = Depends(get_db)):
    domain = db.query(Domain).options(
        joinedload(Domain.topics)
    ).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return {
        "id": domain.id,
        "name": domain.name,
        "description": domain.description,
        "weight_percentage": domain.weight_percentage,
        "topics": [
            {"id": t.id, "name": t.name, "slug": t.slug, "description": t.description}
            for t in domain.topics
        ],
    }


# --- Topic Routes ---

@router.get("/topics/{topic_id}")
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    topic = db.query(Topic).options(
        joinedload(Topic.concepts)
    ).filter(Topic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {
        "id": topic.id,
        "name": topic.name,
        "slug": topic.slug,
        "description": topic.description,
        "domain": {
            "id": topic.domain.id,
            "name": topic.domain.name,
        } if topic.domain else None,
        "concepts": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "short_definition": c.short_definition,
                "difficulty": c.difficulty.value if c.difficulty else None,
            }
            for c in topic.concepts
        ],
    }


# --- Concept Routes ---

@router.get("/concepts/{concept_id}")
async def get_concept(concept_id: int, db: Session = Depends(get_db)):
    concept = db.query(Concept).options(
        joinedload(Concept.topic),
        joinedload(Concept.learning_resources),
        joinedload(Concept.source_relationships).joinedload("target_concept"),
    ).filter(Concept.id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    related = []
    for rel in concept.source_relationships:
        tc = rel.target_concept
        related.append({
            "id": tc.id,
            "name": tc.name,
            "slug": tc.slug,
            "relationship": rel.relationship_type.value,
        })

    return {
        "id": concept.id,
        "name": concept.name,
        "slug": concept.slug,
        "short_definition": concept.short_definition,
        "simple_explanation": concept.simple_explanation,
        "detailed_explanation": concept.detailed_explanation,
        "examples": concept.examples,
        "key_points": concept.key_points,
        "exam_tips": concept.exam_tips,
        "common_mistakes": concept.common_mistakes,
        "difficulty": concept.difficulty.value if concept.difficulty else None,
        "topic": {
            "id": concept.topic.id,
            "name": concept.topic.name,
            "domain": {
                "id": concept.topic.domain.id,
                "name": concept.topic.domain.name,
            } if concept.topic.domain else None,
        } if concept.topic else None,
        "learning_resources": [
            {
                "id": lr.id,
                "title": lr.title,
                "description": lr.description,
                "url": lr.url,
                "source": lr.source,
                "resource_type": lr.resource_type.value,
                "is_official": lr.is_official,
            }
            for lr in concept.learning_resources
        ],
        "related_concepts": related,
    }

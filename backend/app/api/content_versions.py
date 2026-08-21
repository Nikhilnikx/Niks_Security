from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.certification import Certification
from app.models.content_version import ContentVersion, ContentUpdateLog
from app.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/content", tags=["content-versions"])


@router.get("/versions/{certification_id}")
async def get_content_versions(
    certification_id: int,
    db: Session = Depends(get_db),
):
    versions = db.query(ContentVersion).filter(
        ContentVersion.certification_id == certification_id
    ).order_by(ContentVersion.last_updated.desc()).all()

    return {
        "versions": [
            {
                "id": v.id,
                "version": v.version,
                "content_status": v.content_status,
                "last_reviewed": v.last_reviewed.isoformat() if v.last_reviewed else None,
                "last_updated": v.last_updated.isoformat() if v.last_updated else None,
                "next_review": v.next_review.isoformat() if v.next_review else None,
                "changes_summary": v.changes_summary,
            }
            for v in versions
        ]
    }


@router.get("/updates")
async def get_content_updates(
    limit: int = 20,
    db: Session = Depends(get_db),
):
    updates = db.query(ContentUpdateLog).order_by(
        ContentUpdateLog.created_at.desc()
    ).limit(limit).all()

    return {
        "updates": [
            {
                "id": u.id,
                "certification_id": u.certification_id,
                "update_type": u.update_type,
                "title": u.title,
                "description": u.description,
                "created_at": u.created_at.isoformat(),
            }
            for u in updates
        ]
    }


@router.post("/admin/versions")
async def create_content_version(
    certification_id: int,
    version: str,
    changes_summary: str = "",
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    cv = ContentVersion(
        certification_id=certification_id,
        version=version,
        content_status="current",
        last_updated=datetime.utcnow(),
        next_review=datetime.utcnow() + timedelta(days=90),
        changes_summary=changes_summary,
    )
    db.add(cv)
    db.commit()
    return {"id": cv.id}


@router.post("/admin/updates")
async def log_content_update(
    certification_id: int,
    update_type: str,
    title: str,
    description: str = "",
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    log = ContentUpdateLog(
        certification_id=certification_id,
        update_type=update_type,
        title=title,
        description=description,
    )
    db.add(log)
    db.commit()
    return {"id": log.id}

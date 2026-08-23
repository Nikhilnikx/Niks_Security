"""Assets API"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.asset import Asset, AssetType, AssetStatus
from app.models.audit_log import AuditLog
from app.auth import get_current_user

router = APIRouter(prefix="/api/assets", tags=["assets"])


class AssetCreate(BaseModel):
    name: str
    asset_type: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    description: Optional[str] = None
    os_info: Optional[str] = None


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    description: Optional[str] = None


@router.get("")
def list_assets(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    query = db.query(Asset).filter(Asset.organization_id == org_id)
    if asset_type:
        query = query.filter(Asset.asset_type == asset_type)
    if status:
        query = query.filter(Asset.status == status)
    if search:
        query = query.filter((Asset.name.ilike(f"%{search}%")) | (Asset.ip_address.ilike(f"%{search}%")))

    total = query.count()
    assets = query.order_by(Asset.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {
        "assets": [_asset_to_dict(a) for a in assets],
        "total": total,
        "page": page,
        "total_pages": (total + limit - 1) // limit,
    }


@router.post("")
def create_asset(data: AssetCreate, request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = Asset(
        name=data.name,
        asset_type=data.asset_type,
        ip_address=data.ip_address,
        hostname=data.hostname,
        description=data.description,
        os_info=data.os_info,
        organization_id=current_user.organization_id,
        owner_id=current_user.id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _asset_to_dict(asset)


@router.get("/{asset_id}")
def get_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _asset_to_dict(asset)


@router.put("/{asset_id}")
def update_asset(asset_id: int, data: AssetUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    if data.name:
        asset.name = data.name
    if data.status:
        asset.status = data.status
    if data.risk_level:
        asset.risk_level = data.risk_level
    if data.description is not None:
        asset.description = data.description
    db.commit()
    db.refresh(asset)
    return _asset_to_dict(asset)


@router.delete("/{asset_id}")
def delete_asset(asset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    asset = db.query(Asset).filter(Asset.id == asset_id, Asset.organization_id == current_user.organization_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    db.delete(asset)
    db.commit()
    return {"message": "Asset deleted"}


def _asset_to_dict(a):
    return {
        "id": a.id,
        "name": a.name,
        "asset_type": a.asset_type.value if hasattr(a.asset_type, 'value') else a.asset_type,
        "ip_address": a.ip_address,
        "hostname": a.hostname,
        "status": a.status.value if hasattr(a.status, 'value') else a.status,
        "risk_level": a.risk_level,
        "description": a.description,
        "os_info": a.os_info,
        "last_activity": a.last_activity.isoformat() if a.last_activity else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
        "owner_id": a.owner_id,
    }

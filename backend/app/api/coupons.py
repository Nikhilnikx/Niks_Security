from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.models.coupon import Coupon
from app.models.product import Product
from app.auth import get_current_user, get_current_admin_user

router = APIRouter(prefix="/api/coupons", tags=["coupons"])


class ValidateCouponRequest(BaseModel):
    code: str
    product_id: int


class CreateCouponRequest(BaseModel):
    code: str
    discount_type: str
    discount_value: float
    max_uses: Optional[int] = None
    applicable_product_id: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/validate")
async def validate_coupon(
    request: ValidateCouponRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    coupon = db.query(Coupon).filter(
        Coupon.code == request.code.upper(),
        Coupon.active == True,
    ).first()

    if not coupon:
        raise HTTPException(status_code=404, detail="Invalid coupon code")

    now = datetime.utcnow()
    if coupon.start_date and now < coupon.start_date:
        raise HTTPException(status_code=400, detail="Coupon is not yet active")
    if coupon.end_date and now > coupon.end_date:
        raise HTTPException(status_code=400, detail="Coupon has expired")
    if coupon.max_uses and coupon.used_count >= coupon.max_uses:
        raise HTTPException(status_code=400, detail="Coupon usage limit reached")
    if coupon.applicable_product_id and coupon.applicable_product_id != request.product_id:
        raise HTTPException(status_code=400, detail="Coupon not applicable to this product")

    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if coupon.discount_type == "percentage":
        discount = product.price * (coupon.discount_value / 100)
    else:
        discount = min(coupon.discount_value, product.price)

    final_price = max(0, product.price - discount)

    return {
        "valid": True,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "original_price": product.price,
        "discount_amount": round(discount, 2),
        "final_price": round(final_price, 2),
    }


@router.post("/admin/create")
async def create_coupon(
    request: CreateCouponRequest,
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    existing = db.query(Coupon).filter(Coupon.code == request.code.upper()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Coupon code already exists")

    coupon = Coupon(
        code=request.code.upper(),
        discount_type=request.discount_type,
        discount_value=request.discount_value,
        max_uses=request.max_uses,
        applicable_product_id=request.applicable_product_id,
    )

    if request.start_date:
        try:
            coupon.start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        except ValueError:
            pass
    if request.end_date:
        try:
            coupon.end_date = datetime.strptime(request.end_date, "%Y-%m-%d")
        except ValueError:
            pass

    db.add(coupon)
    db.commit()
    return {"id": coupon.id, "code": coupon.code}


@router.get("/admin/list")
async def list_coupons(
    admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    coupons = db.query(Coupon).order_by(Coupon.created_at.desc()).all()
    return {
        "coupons": [
            {
                "id": c.id,
                "code": c.code,
                "discount_type": c.discount_type,
                "discount_value": c.discount_value,
                "max_uses": c.max_uses,
                "used_count": c.used_count,
                "active": c.active,
                "start_date": c.start_date.isoformat() if c.start_date else None,
                "end_date": c.end_date.isoformat() if c.end_date else None,
            }
            for c in coupons
        ]
    }

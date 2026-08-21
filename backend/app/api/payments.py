import hashlib
import hmac
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import httpx
from app.database import get_db
from app.models.user import User
from app.models.product import Product, UserEntitlement, Purchase, EntitlementStatus, PurchaseStatus
from app.config import get_settings
from app.auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["payments"])
settings = get_settings()


class CreateOrderRequest(BaseModel):
    product_id: int


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    product_id: int


# --- Create Razorpay Order ---

@router.post("/create-order")
async def create_order(
    request: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(
        Product.id == request.product_id,
        Product.active == True,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check if already purchased
    existing_entitlement = db.query(UserEntitlement).filter(
        UserEntitlement.user_id == current_user.id,
        UserEntitlement.status == EntitlementStatus.ACTIVE,
    ).join(Product).filter(Product.id == product.id).first()
    if existing_entitlement:
        raise HTTPException(status_code=400, detail="Already have access to this product")

    # Create Razorpay order via API
    try:
        async with httpx.AsyncClient() as client:
            auth = (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            response = await client.post(
                "https://api.razorpay.com/v1/orders",
                auth=auth,
                json={
                    "amount": int(product.price * 100),  # Razorpay uses paise
                    "currency": product.currency,
                    "receipt": f"niksmind_{current_user.id}_{product.id}_{datetime.utcnow().timestamp()}",
                    "notes": {
                        "user_id": str(current_user.id),
                        "product_id": str(product.id),
                    },
                },
            )
            order_data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create payment order")

    if "error" in order_data:
        raise HTTPException(status_code=500, detail=order_data["error"].get("description", "Payment order creation failed"))

    # Record purchase attempt
    purchase = Purchase(
        user_id=current_user.id,
        product_id=product.id,
        payment_provider="razorpay",
        order_id=order_data.get("id"),
        amount=product.price,
        currency=product.currency,
        status=PurchaseStatus.PENDING,
    )
    db.add(purchase)
    db.commit()

    return {
        "order_id": order_data.get("id"),
        "amount": product.price,
        "currency": product.currency,
        "key_id": settings.RAZORPAY_KEY_ID,
        "product_name": product.name,
    }


# --- Verify Payment ---

@router.post("/verify")
async def verify_payment(
    request: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Verify signature server-side
    payload = f"{request.razorpay_order_id}|{request.razorpay_payment_id}"
    expected_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()

    if expected_signature != request.razorpay_signature:
        raise HTTPException(status_code=400, detail="Payment verification failed - invalid signature")

    # Find the purchase record
    purchase = db.query(Purchase).filter(
        Purchase.order_id == request.razorpay_order_id,
        Purchase.user_id == current_user.id,
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase record not found")

    if purchase.status == PurchaseStatus.PAID:
        return {"status": "already_verified"}

    # Update purchase
    purchase.payment_id = request.razorpay_payment_id
    purchase.status = PurchaseStatus.PAID

    # Activate entitlement
    entitlement = UserEntitlement(
        user_id=current_user.id,
        product_id=purchase.product_id,
        status=EntitlementStatus.ACTIVE,
    )
    db.add(entitlement)
    db.commit()

    return {"status": "verified", "entitlement_active": True}


# --- Razorpay Webhook ---

@router.post("/webhook")
async def razorpay_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.body()
    signature = request.headers.get("x-razorpay-signature", "")

    # Verify webhook signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event = payload.get("event", "")

    if event == "payment.captured":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment.get("order_id")
        payment_id = payment.get("id")

        if not order_id:
            return {"status": "ignored"}

        # Find purchase
        purchase = db.query(Purchase).filter(
            Purchase.order_id == order_id,
        ).first()

        if not purchase:
            return {"status": "purchase_not_found"}

        # Idempotent: skip if already processed
        if purchase.status == PurchaseStatus.PAID:
            return {"status": "already_processed"}

        # Update purchase
        purchase.payment_id = payment_id
        purchase.status = PurchaseStatus.PAID

        # Activate entitlement (idempotent check)
        existing = db.query(UserEntitlement).filter(
            UserEntitlement.user_id == purchase.user_id,
            UserEntitlement.product_id == purchase.product_id,
            UserEntitlement.status == EntitlementStatus.ACTIVE,
        ).first()

        if not existing:
            entitlement = UserEntitlement(
                user_id=purchase.user_id,
                product_id=purchase.product_id,
                status=EntitlementStatus.ACTIVE,
            )
            db.add(entitlement)

        db.commit()

    elif event == "payment.failed":
        payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
        order_id = payment.get("order_id")

        if order_id:
            purchase = db.query(Purchase).filter(Purchase.order_id == order_id).first()
            if purchase:
                purchase.status = PurchaseStatus.FAILED
                db.commit()

    return {"status": "processed"}


# --- Get Entitlements ---

@router.get("/entitlements")
async def get_entitlements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    entitlements = db.query(UserEntitlement).filter(
        UserEntitlement.user_id == current_user.id,
        UserEntitlement.status == EntitlementStatus.ACTIVE,
    ).all()

    return {
        "entitlements": [
            {
                "id": e.id,
                "product_id": e.product_id,
                "status": e.status.value,
                "starts_at": e.starts_at.isoformat(),
                "expires_at": e.expires_at.isoformat() if e.expires_at else None,
            }
            for e in entitlements
        ]
    }


# --- Get Products ---

@router.get("/products")
async def get_products(
    certification_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.active == True)
    if certification_id:
        query = query.filter(Product.certification_id == certification_id)

    products = query.all()
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "slug": p.slug,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "product_type": p.product_type.value,
                "certification_id": p.certification_id,
            }
            for p in products
        ]
    }

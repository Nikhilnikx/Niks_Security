from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
from app.database import Base


class ProductType(str, enum.Enum):
    CERTIFICATION = "certification"
    SUBSCRIPTION = "subscription"
    BUNDLE = "bundle"


class EntitlementStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PurchaseStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=True)
    certification_id = Column(Integer, ForeignKey("certifications.id"), nullable=True)
    price = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    product_type = Column(SAEnum(ProductType), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    certification = relationship("Certification", back_populates="products")
    entitlements = relationship("UserEntitlement", back_populates="product")
    purchases = relationship("Purchase", back_populates="product")


class UserEntitlement(Base):
    __tablename__ = "user_entitlements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    status = Column(SAEnum(EntitlementStatus), default=EntitlementStatus.ACTIVE, nullable=False)
    starts_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="entitlements")
    product = relationship("Product", back_populates="entitlements")


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    payment_provider = Column(String(50), nullable=False)
    payment_id = Column(String(255), nullable=True)
    order_id = Column(String(255), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="INR", nullable=False)
    status = Column(SAEnum(PurchaseStatus), default=PurchaseStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")

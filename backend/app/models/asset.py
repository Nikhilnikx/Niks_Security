import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class AssetType(str, enum.Enum):
    SERVER = "server"
    ENDPOINT = "endpoint"
    APPLICATION = "application"
    DATABASE = "database"
    CLOUD = "cloud"
    NETWORK_DEVICE = "network_device"
    OTHER = "other"


class AssetStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    asset_type = Column(SAEnum(AssetType), nullable=False)
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    status = Column(SAEnum(AssetStatus), default=AssetStatus.ACTIVE, nullable=False)
    risk_level = Column(String(20), default="low", nullable=False)
    description = Column(Text, nullable=True)
    os_info = Column(String(200), nullable=True)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    # Foreign keys
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="assets")
    owner = relationship("User", back_populates="assets")
    security_events = relationship("SecurityEvent", back_populates="asset")
    alerts = relationship("Alert", back_populates="asset")

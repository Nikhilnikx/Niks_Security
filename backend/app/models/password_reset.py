"""Password reset token model"""
import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from app.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    @staticmethod
    def generate_token() -> str:
        return secrets.token_urlsafe(48)

    @staticmethod
    def create_for_user(user_id: int, db, expires_minutes: int = 30):
        """Create a reset token valid for the given number of minutes."""
        from app.models.password_reset import PasswordResetToken as PRT

        # Invalidate any previous unused tokens for this user
        old_tokens = db.query(PRT).filter(
            PRT.user_id == user_id, PRT.used == False
        ).all()
        for t in old_tokens:
            t.used = True

        token_str = PRT.generate_token()
        now = datetime.now(timezone.utc)
        reset_token = PRT(
            token=token_str,
            user_id=user_id,
            expires_at=now + timedelta(minutes=expires_minutes),
        )
        db.add(reset_token)
        db.commit()
        return token_str

    def is_valid(self) -> bool:
        # Handle both naive and aware datetimes from SQLite
        now = datetime.utcnow()
        exp = self.expires_at
        if exp and exp.tzinfo is not None:
            exp = exp.replace(tzinfo=None)
        return not self.used and now < exp

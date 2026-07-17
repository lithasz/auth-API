from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)

    # Hash output
    hashed_password = Column(String, nullable=False)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Brute-force tracking
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # Links this refresh token back to the user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    token_hash = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)

    # If a token is used and rotated, or manually revoked
    revoked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


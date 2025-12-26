from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)
    avatar_url = Column(String(512), nullable=True)
    status = Column(Integer, default=1)  # 1: active, 0: disabled
    oauth_provider = Column(String(32), nullable=True)
    oauth_id = Column(String(128), nullable=True, index=True)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    code = Column(String(10), nullable=False)
    type = Column(String(20), default="register") # register, reset_password
    expires_at = Column(DateTime, nullable=False)
    used = Column(Integer, default=0) # 0: unused, 1: used
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Integer, default=0)

class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(512), nullable=False, index=True)
    user_agent = Column(String(512), nullable=True)
    ip = Column(String(64), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    reset_token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class LLMCallLog(Base):
    __tablename__ = "llm_call_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    model = Column(String(128), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

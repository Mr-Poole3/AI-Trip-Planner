from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=2, max_length=32)

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str = Field(..., min_length=6, max_length=72)
    captcha: str

class CaptchaSendRequest(BaseModel):
    email: EmailStr
    type: str = "register" # register, reset_password

# Properties to receive via API on login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Properties to return to client
class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    created_at: datetime
    phone: Optional[str] = None # Keeping for compatibility if needed, though not in new DB schema explicitly

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenRefresh(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    sub: Optional[str] = None
    type: Optional[str] = None

# Password reset
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

# OAuth
class GoogleLogin(BaseModel):
    id_token: str

# Generic Response
class ResponseBase(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Optional[dict] = None

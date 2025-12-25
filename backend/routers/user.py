from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.session import get_db
from routers.auth import get_current_user
from schemas.auth import UserResponse, ResponseBase
from database.models import User

router = APIRouter(prefix="/api/v1/auth", tags=["user"])

@router.get("/me", response_model=ResponseBase)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return ResponseBase(data=UserResponse.model_validate(current_user).model_dump())

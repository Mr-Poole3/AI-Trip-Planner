from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc, delete

from database.session import get_db
from routers.auth import get_current_user
from database.models import User, LLMCallLog
from schemas.auth import ResponseBase
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

class LLMHistoryItem(BaseModel):
    id: int
    model: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/history", response_model=ResponseBase)
async def get_history(
    page: int = 1, 
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    stmt = select(LLMCallLog).where(LLMCallLog.user_id == current_user.id)\
        .order_by(desc(LLMCallLog.created_at))\
        .offset(offset).limit(page_size)
    
    result = await db.execute(stmt)
    items = result.scalars().all()
    
    # Count total
    # (Simplified count for async)
    count_stmt = select(func.count()).select_from(LLMCallLog).where(LLMCallLog.user_id == current_user.id)
    # Note: func needs import
    from sqlalchemy import func
    count_res = await db.execute(select(func.count()).select_from(LLMCallLog).where(LLMCallLog.user_id == current_user.id))
    total = count_res.scalar()
    
    data_items = [LLMHistoryItem.model_validate(item).model_dump() for item in items]
    
    return ResponseBase(data={
        "page": page,
        "page_size": page_size,
        "total": total,
        "items": data_items
    })

@router.delete("/history/{log_id}", response_model=ResponseBase)
async def delete_history(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(LLMCallLog).where(LLMCallLog.id == log_id, LLMCallLog.user_id == current_user.id)
    result = await db.execute(stmt)
    log = result.scalars().first()
    
    if not log:
        return ResponseBase(code=404, message="not found")
    
    await db.delete(log)
    await db.commit()
    
    return ResponseBase(message="deleted")

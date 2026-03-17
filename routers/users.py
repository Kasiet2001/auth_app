from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.auth import hash_password
from db.depends import get_async_db
from models.models import User
from schemas.user import (
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_async_db)
):
    result = await db.scalars(select(User).where(User.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email already registered")
    db_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password=hash_password(user.password),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from core.auth import (
    create_access_token,
    get_admin_or_superuser,
    get_current_user,
    hash_password,
    oauth2_scheme,
    verify_password,
)
from db.depends import get_async_db
from dependencies.auth import require_self
from models.models import User
from schemas.user import (
    UpdateUserRole,
    UserCreate,
    UserResponse,
    UserUpdate,
)

token_blacklist: set[str] = set()

router = APIRouter()

@router.post(
    "/registration", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(
    user: UserCreate, db: AsyncSession = Depends(get_async_db)
):
    result = await db.scalars(
        select(User).where(User.email == user.email, User.is_active == True)
    )
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


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db)
):
    result = await db.scalars(
        select(User).where(User.email == form_data.username, User.is_active == True)
    )
    user = result.first()
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value, "id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    token: str = Depends(oauth2_scheme)
):
    token_blacklist.add(token)
    return {"message": "Logged out"}

@router.patch("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_self())
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if data.email is not None:
        existing_email = await db.scalar(
            select(User).where(
                User.email == data.email,
                User.is_active == True,
                User.id != user_id
            )
        )
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    data_dict = data.model_dump(exclude_unset=True)
    for key, value in data_dict.items():
        setattr(user, key, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    data: UpdateUserRole,
    db: AsyncSession = Depends(get_async_db),
    _: User = Depends(get_admin_or_superuser)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.role = data.role
    await db.commit()
    await db.refresh(user)
    return {"message": "Role updated successfully"}


@router.delete("/users/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_self())
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False

    await db.commit()
    await db.refresh(user)

    return user

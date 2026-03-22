from fastapi import Depends, HTTPException, Path

from core.auth import get_current_user
from models.models import User


def require_self():
    async def _require_self(
        user_id: int = Path(...),
        current_user: User = Depends(get_current_user),
    ):
        if current_user.id != user_id:
            raise HTTPException(status_code=403)
        return current_user

    return _require_self

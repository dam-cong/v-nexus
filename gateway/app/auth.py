"""JWT authentication helpers for V-Nexus Gateway."""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import User
from db.password import hash_password, verify_password  # noqa: F401
from .config import settings

security = HTTPBearer(auto_error=False)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours


def create_access_token(entity_id: int, role: str, entity_type: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(entity_id),
        "role": role,
        "type": entity_type,
        "exp": expire,
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.auth_secret, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc hết hạn",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_session),
) -> dict:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chưa đăng nhập",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    entity_id = int(payload.get("sub", 0))
    role = payload.get("role", "")
    entity_type = payload.get("type", "")

    result = await db.execute(select(User).where(User.id == entity_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="Người dùng không tồn tại")
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": role,
        "entity_type": entity_type or "student",
    }


def require_role(*allowed_roles: str):
    async def role_checker(
        user: dict = Depends(get_current_user),
    ) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền truy cập tài nguyên này",
            )
        return user
    return role_checker

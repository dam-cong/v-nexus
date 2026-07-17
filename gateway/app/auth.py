"""Auth qua fastapi-users — JWT + role (student/teacher/parent/school_admin).

Tránh viết đăng nhập/đăng ký/phân quyền từ đầu. parent_id/teacher_id cho các route
dashboard lấy từ token đã xác thực (current_user.id), KHÔNG nhận qua query param —
đây là ranh giới bảo mật thật, khác việc chỉ tin input từ client.
"""
import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.exceptions import UserAlreadyExists
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import SessionLocal
from db.models import User, UserRole

from .config import settings


class UserRead(schemas.BaseUser[uuid.UUID]):
    role: UserRole


class UserCreate(schemas.BaseUserCreate):
    role: UserRole = UserRole.student


class UserUpdate(schemas.BaseUserUpdate):
    role: UserRole | None = None


async def get_user_db() -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    async with SessionLocal() as session:
        yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.auth_secret
    verification_token_secret = settings.auth_secret


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.auth_secret, lifetime_seconds=3600 * 24)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)


def require_role(*roles: UserRole):
    """Dependency: chỉ cho qua nếu current_user.role nằm trong `roles`, else 403."""

    async def _check(user: User = Depends(current_active_user)) -> User:
        from fastapi import HTTPException, status

        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Yêu cầu vai trò {[r.value for r in roles]}, tài khoản này là {user.role.value}.",
            )
        return user

    return _check

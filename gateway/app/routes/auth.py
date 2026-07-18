"""Authentication routes: login, me, register."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import User, Student, Teacher
from app.auth import (
    create_access_token,
    get_current_user,
    require_role,
)
from db.password import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


ROLE_BY_ID = {1: "hoc_sinh", 2: "giao_vien", 3: "admin", 4: "phu_huynh"}


def _entity_type(role_name: str) -> str:
    if role_name == "hoc_sinh":
        return "student"
    if role_name == "giao_vien":
        return "teacher"
    if role_name == "phu_huynh":
        return "parent"
    return "admin"


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    entity_type: str


class AdminUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    entity_type: str
    role_id: int
    grade: Optional[str] = None
    subject: Optional[str] = None
    created_at: Optional[datetime] = None


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    grade: str = "Lớp 3"
    role: str = "hoc_sinh"


class RegisterResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if user and verify_password(req.password, user.hashed_password):
        role_name = ROLE_BY_ID.get(user.role_id, "hoc_sinh")
        token = create_access_token(user.id, role_name, _entity_type(role_name))
        return LoginResponse(
            access_token=token,
            user={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": role_name,
                "entity_type": _entity_type(role_name),
            },
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email hoặc mật khẩu không đúng",
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(**user)


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    if req.role == "hoc_sinh":
        role_id = 1
        new_user = User(
            name=req.name,
            email=req.email,
            hashed_password=hash_password(req.password),
            role_id=role_id,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        # student profile
        from db.models import Student
        profile = Student(user_id=new_user.id, grade=req.grade)
        db.add(profile)
        await db.commit()
        return RegisterResponse(id=new_user.id, name=new_user.name, email=new_user.email, role="hoc_sinh")
    elif req.role in ("giao_vien", "admin"):
        role_id = 3 if req.role == "admin" else 2
        new_user = User(
            name=req.name,
            email=req.email,
            hashed_password=hash_password(req.password),
            role_id=role_id,
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        from db.models import Teacher
        profile = Teacher(user_id=new_user.id, subject=None)
        db.add(profile)
        await db.commit()
        return RegisterResponse(id=new_user.id, name=new_user.name, email=new_user.email, role=req.role)
    else:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    role: Optional[str] = None,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    """Admin-only: list all users with role and profile info."""
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()

    out = []
    for u in users:
        role_name = ROLE_BY_ID.get(u.role_id, "hoc_sinh")
        item = {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": role_name,
            "entity_type": _entity_type(role_name),
            "role_id": u.role_id,
            "created_at": u.created_at,
        }
        if role_name == "hoc_sinh":
            pr = await db.execute(select(Student).where(Student.user_id == u.id))
            prof = pr.scalar_one_or_none()
            item["grade"] = prof.grade if prof else None
        elif role_name == "giao_vien":
            pr = await db.execute(select(Teacher).where(Teacher.user_id == u.id))
            prof = pr.scalar_one_or_none()
            item["subject"] = prof.subject if prof else None
        if role is None or role == role_name:
            out.append(AdminUserResponse(**item))
    return out


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    admin: dict = Depends(require_role("admin")),
):
    """Admin-only: delete a user (and their profile). Cannot delete self."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Không thể xóa tài khoản của chính mình")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Người dùng không tồn tại")

    role_name = ROLE_BY_ID.get(user.role_id, "hoc_sinh")
    if role_name == "hoc_sinh":
        pr = await db.execute(select(Student).where(Student.user_id == user_id))
        prof = pr.scalar_one_or_none()
        if prof:
            await db.delete(prof)
    elif role_name == "giao_vien":
        pr = await db.execute(select(Teacher).where(Teacher.user_id == user_id))
        prof = pr.scalar_one_or_none()
        if prof:
            await db.delete(prof)

    await db.delete(user)
    await db.commit()

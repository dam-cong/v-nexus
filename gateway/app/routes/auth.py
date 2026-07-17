"""Authentication routes: login, me, register."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import Student, Teacher
from app.auth import (
    create_access_token,
    get_current_user,
    require_role,
)
from db.password import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


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
    # Search in students first, then teachers
    result = await db.execute(
        select(Student).where(Student.email == req.email)
    )
    student = result.scalar_one_or_none()

    if student and verify_password(req.password, student.hashed_password):
        token = create_access_token(student.id, "hoc_sinh", "student")
        return LoginResponse(
            access_token=token,
            user={
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "role": "hoc_sinh",
                "entity_type": "student",
            },
        )

    result = await db.execute(
        select(Teacher).where(Teacher.email == req.email)
    )
    teacher = result.scalar_one_or_none()

    if teacher and verify_password(req.password, teacher.hashed_password):
        # Determine role: check role_id. role_id=3 is admin
        role_name = "admin" if teacher.role_id == 3 else "giao_vien"
        token = create_access_token(teacher.id, role_name, "teacher")
        return LoginResponse(
            access_token=token,
            user={
                "id": teacher.id,
                "name": teacher.name,
                "email": teacher.email,
                "role": role_name,
                "entity_type": "teacher",
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
    # Check if email already exists
    existing = await db.execute(
        select(Student).where(Student.email == req.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    existing = await db.execute(
        select(Teacher).where(Teacher.email == req.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email đã được sử dụng")

    if req.role == "hoc_sinh":
        new_student = Student(
            name=req.name,
            email=req.email,
            hashed_password=hash_password(req.password),
            grade=req.grade,
            role_id=1,
        )
        db.add(new_student)
        await db.commit()
        await db.refresh(new_student)
        return RegisterResponse(
            id=new_student.id,
            name=new_student.name,
            email=new_student.email,
            role="hoc_sinh",
        )
    elif req.role in ("giao_vien", "admin"):
        role_id = 3 if req.role == "admin" else 2
        new_teacher = Teacher(
            name=req.name,
            email=req.email,
            hashed_password=hash_password(req.password),
            role_id=role_id,
        )
        db.add(new_teacher)
        await db.commit()
        await db.refresh(new_teacher)
        return RegisterResponse(
            id=new_teacher.id,
            name=new_teacher.name,
            email=new_teacher.email,
            role=req.role,
        )
    else:
        raise HTTPException(status_code=400, detail="Role không hợp lệ")

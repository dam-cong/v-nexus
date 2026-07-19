"""CRUD routes for Roles, Students, Teachers, Rankings, Questions, Placement Tests, and Test Results."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import (
    Role, User, Student, Teacher, Ranking,
    Question, PlacementTest, PlacementTestQuestion, StudentTestResult, Parent, TeacherEvaluation
)
from domain.bkt import run_assessment
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/api", tags=["CRUD Operations"])


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

# Role Schemas
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: int
    class Config:
        from_attributes = True


# Ranking Schemas
class RankingBase(BaseModel):
    score: int
    level: str

class RankingCreate(RankingBase):
    user_id: int

class RankingUpdate(BaseModel):
    score: Optional[int] = None
    level: Optional[str] = None

class RankingResponse(RankingBase):
    id: int
    user_id: Optional[int] = None
    updated_at: datetime
    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr
    grade: Optional[str] = None
    role_id: Optional[int] = 1
    years_studying_english: Optional[int] = None
    learning_environment: Optional[str] = None
    self_assessment_level: Optional[str] = None
    learning_goal: Optional[str] = None
    primary_teacher_id: Optional[int] = None
    parent_id: Optional[int] = None

class StudentCreate(StudentBase):
    password: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None
    years_studying_english: Optional[int] = None
    learning_environment: Optional[str] = None
    self_assessment_level: Optional[str] = None
    learning_goal: Optional[str] = None
    training_plan: Optional[str] = None
    primary_teacher_id: Optional[int] = None
    parent_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    training_plan: Optional[str] = None
    ranking: Optional[RankingResponse] = None
    test_results: List["TestResultResponse"] = []
    class Config:
        from_attributes = True


# Teacher Schemas
class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    role_id: Optional[int] = 2

class TeacherCreate(TeacherBase):
    password: Optional[str] = None

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    subject: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None

class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# Parent Schemas
class ParentBase(BaseModel):
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role_id: Optional[int] = 4

class ParentCreate(ParentBase):
    password: Optional[str] = None
    student_ids: Optional[list[int]] = []

class ParentResponse(ParentBase):
    id: int
    students: Optional[list[dict]] = []
    created_at: datetime
    class Config:
        from_attributes = True


# Teacher Evaluation Schemas
class TeacherEvaluationResponse(BaseModel):
    id: int
    student_id: int
    teacher_id: int
    teacher_name: Optional[str] = None
    comment: str
    created_at: datetime
    class Config:
        from_attributes = True


# Question Schemas
class QuestionResponse(BaseModel):
    id: int
    question_id: str
    type: str
    instruction_label: str
    skill_id: str
    skill_name: str
    difficulty: str
    purpose: str
    prompt: Optional[dict] = None
    options: Optional[list] = None
    correct_option_id: str
    explanation: Optional[str] = None
    class Config:
        from_attributes = True


# Placement Test Schemas
class PlacementTestResponse(BaseModel):
    id: int
    test_id: str
    title: str
    mascot: Optional[dict] = None
    steps: Optional[list] = None
    levels: Optional[list] = None
    adaptive_config: Optional[dict] = None
    created_at: datetime
    class Config:
        from_attributes = True


# Test Result Schemas
class TestResultResponse(BaseModel):
    id: int
    user_id: int
    test_id: int
    answers: Optional[list] = None
    score: int
    max_score: int
    percentage: float
    result_level: str
    cefr: str
    time_total_sec: int
    mastery: Optional[dict] = None
    gaps: Optional[list] = None
    recommendations: Optional[list] = None
    training_plan: Optional[str] = None
    alternative_plans: Optional[dict] = None
    roadmap_completed: bool = False
    quick_check_passed: bool = False
    test_date: datetime
    is_roadmap_approved: Optional[bool] = False
    roadmap_completed: Optional[bool] = False
    quick_check_passed: Optional[bool] = False
    test_date: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True


class TestResultComplete(BaseModel):
    completed: bool = True


class QuickCheckSubmit(BaseModel):
    answers: Optional[list] = None


class QuickCheckResponse(BaseModel):
    passed: bool
    roadmap_completed: bool
    remaining_gaps: list
    mastery: Optional[dict] = None


class TestResultSubmit(BaseModel):
    answers: Optional[list] = None
    score: int
    max_score: int
    percentage: float
    result_level: str
    cefr: str
    time_total_sec: int = 0
    mastery: Optional[dict] = None
    gaps: Optional[list] = None
    recommendations: Optional[list] = None
    training_plan: Optional[str] = None
    alternative_plans: Optional[dict] = None
    test_date: Optional[str] = None


# =====================================================================
# API ENDPOINTS: ROLES
# =====================================================================

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Role))
    return result.scalars().all()

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    db_role = Role(name=role.name, description=role.description)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


# =====================================================================
# API ENDPOINTS: STUDENTS
# =====================================================================

async def _format_students(db: AsyncSession, users: list[User]) -> list[dict]:
    student_list = []
    for u in users:
        rank_res = await db.execute(select(Ranking).where(Ranking.user_id == u.id))
        ranking_obj = rank_res.scalar_one_or_none()
        tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.user_id == u.id))
        test_results_obj = list(tr_res.scalars().all())
        grade = None
        p_res = await db.execute(select(Student).where(Student.user_id == u.id))
        profile = p_res.scalar_one_or_none()
        primary_teacher_id = None
        parent_id = None
        if profile:
            grade = profile.grade
            if profile.primary_teacher_id:
                t_res = await db.execute(select(Teacher).where(Teacher.id == profile.primary_teacher_id))
                t_obj = t_res.scalar_one_or_none()
                if t_obj:
                    primary_teacher_id = t_obj.user_id
            if profile.parent_id:
                p_res_obj = await db.execute(select(Parent).where(Parent.id == profile.parent_id))
                p_obj = p_res_obj.scalar_one_or_none()
                if p_obj:
                    parent_id = p_obj.user_id

        student_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "grade": grade,
            "primary_teacher_id": primary_teacher_id,
            "parent_id": parent_id,
            "role_id": u.role_id,
            "created_at": u.created_at,
            "ranking": ranking_obj,
            "test_results": test_results_obj,
            "training_plan": profile.training_plan if profile else None,
        })
    return student_list

@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    if user["role"] == "hoc_sinh":
        result = await db.execute(select(User).where(User.id == user["id"]))
        users = list(result.scalars().all())
    else:
        result = await db.execute(select(User).where(User.role_id == 1))
        users = list(result.scalars().all())

    return await _format_students(db, users)

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Students can only see themselves
    if user["role"] == "hoc_sinh" and user["id"] != student_id:
        raise HTTPException(status_code=403, detail="Ban chi co the xem du lieu cua chinh minh")

    result = await db.execute(select(User).where(User.id == student_id, User.role_id == 1))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    rank_res = await db.execute(select(Ranking).where(Ranking.user_id == student.id))
    ranking_obj = rank_res.scalar_one_or_none()

    tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.user_id == student.id))
    test_results_obj = list(tr_res.scalars().all())

    p_res = await db.execute(select(Student).where(Student.user_id == student.id))
    profile = p_res.scalar_one_or_none()

    primary_teacher_id = None
    parent_id = None
    if profile:
        if profile.primary_teacher_id:
            t_res = await db.execute(select(Teacher).where(Teacher.id == profile.primary_teacher_id))
            t_obj = t_res.scalar_one_or_none()
            if t_obj:
                primary_teacher_id = t_obj.user_id
        if profile.parent_id:
            p_res_obj = await db.execute(select(Parent).where(Parent.id == profile.parent_id))
            p_obj = p_res_obj.scalar_one_or_none()
            if p_obj:
                parent_id = p_obj.user_id

    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": profile.grade if profile else None,
        "primary_teacher_id": primary_teacher_id,
        "parent_id": parent_id,
        "role_id": student.role_id,
        "years_studying_english": profile.years_studying_english if profile else None,
        "learning_environment": profile.learning_environment if profile else None,
        "self_assessment_level": profile.self_assessment_level if profile else None,
        "learning_goal": profile.learning_goal if profile else None,
        "training_plan": profile.training_plan if profile else None,
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "test_results": test_results_obj,
    }

@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    from db.password import hash_password
    db_user = User(
        name=student.name,
        email=student.email,
        role_id=student.role_id or 1,
        hashed_password=hash_password(student.password or "88888888"),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    t_id = None
    if student.primary_teacher_id:
        t_res = await db.execute(select(Teacher).where(Teacher.user_id == student.primary_teacher_id))
        t_obj = t_res.scalar_one_or_none()
        if t_obj:
            t_id = t_obj.id

    p_id = None
    if student.parent_id:
        p_res_obj = await db.execute(select(Parent).where(Parent.user_id == student.parent_id))
        p_obj = p_res_obj.scalar_one_or_none()
        if p_obj:
            p_id = p_obj.id

    db_profile = Student(
        user_id=db_user.id,
        grade=student.grade,
        primary_teacher_id=t_id,
        parent_id=p_id
    )
    db.add(db_profile)

    db_ranking = Ranking(user_id=db_user.id, score=0, level="Beginner")
    db.add(db_ranking)
    await db.commit()
    await db.refresh(db_user)

    rank_res = await db.execute(select(Ranking).where(Ranking.user_id == db_user.id))
    ranking_obj = rank_res.scalar_one_or_none()

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "grade": db_profile.grade,
        "primary_teacher_id": student.primary_teacher_id,
        "parent_id": student.parent_id,
        "role_id": db_user.role_id,
        "created_at": db_user.created_at,
        "ranking": ranking_obj,
        "test_results": [],
    }

@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    result = await db.execute(select(User).where(User.id == student_id, User.role_id == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")

    from db.password import hash_password
    update_data = student_data.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    if "name" in update_data:
        user.name = update_data["name"]
    if "email" in update_data:
        user.email = update_data["email"]
    if "role_id" in update_data:
        user.role_id = update_data["role_id"]
    if new_password:
        user.hashed_password = hash_password(new_password)

    # grade/relations -> profile
    p_res = await db.execute(select(Student).where(Student.user_id == user.id))
    profile = p_res.scalar_one_or_none()
    if profile:
        if "grade" in update_data:
            profile.grade = update_data["grade"]
        if "primary_teacher_id" in update_data:
            if update_data["primary_teacher_id"] is not None:
                t_res = await db.execute(select(Teacher).where(Teacher.user_id == update_data["primary_teacher_id"]))
                t_obj = t_res.scalar_one_or_none()
                profile.primary_teacher_id = t_obj.id if t_obj else None
            else:
                profile.primary_teacher_id = None
        if "parent_id" in update_data:
            if update_data["parent_id"] is not None:
                p_res_obj = await db.execute(select(Parent).where(Parent.user_id == update_data["parent_id"]))
                p_obj = p_res_obj.scalar_one_or_none()
                profile.parent_id = p_obj.id if p_obj else None
            else:
                profile.parent_id = None
    else:
        t_id = None
        if update_data.get("primary_teacher_id"):
            t_res = await db.execute(select(Teacher).where(Teacher.user_id == update_data["primary_teacher_id"]))
            t_obj = t_res.scalar_one_or_none()
            if t_obj: t_id = t_obj.id
            
        p_id = None
        if update_data.get("parent_id"):
            p_res_obj = await db.execute(select(Parent).where(Parent.user_id == update_data["parent_id"]))
            p_obj = p_res_obj.scalar_one_or_none()
            if p_obj: p_id = p_obj.id

        profile = Student(
            user_id=user.id, 
            grade=update_data.get("grade"),
            primary_teacher_id=t_id,
            parent_id=p_id
        )
        db.add(profile)

    await db.commit()
    await db.refresh(user)

    rank_res = await db.execute(select(Ranking).where(Ranking.user_id == user.id))
    ranking_obj = rank_res.scalar_one_or_none()
    tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.user_id == user.id))
    test_results_obj = list(tr_res.scalars().all())

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "grade": profile.grade if profile else None,
        "primary_teacher_id": update_data.get("primary_teacher_id") if "primary_teacher_id" in update_data else (student_data.primary_teacher_id if hasattr(student_data, 'primary_teacher_id') else None),
        "parent_id": update_data.get("parent_id") if "parent_id" in update_data else (student_data.parent_id if hasattr(student_data, 'parent_id') else None),
        "role_id": user.role_id,
        "created_at": user.created_at,
        "ranking": ranking_obj,
        "test_results": test_results_obj,
    }

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    result = await db.execute(select(User).where(User.id == student_id, User.role_id == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    # cascade deletes profile/ranking/test_results
    await db.delete(user)
    await db.commit()
    return None


@router.post("/students/{student_id}/reset-password")
async def reset_student_password(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    result = await db.execute(select(User).where(User.id == student_id, User.role_id == 1))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Student not found")
    from db.password import hash_password
    default_pw = "88888888"
    user.hashed_password = hash_password(default_pw)
    await db.commit()
    return {"message": "Đã reset mật khẩu thành công", "new_password": default_pw}


# =====================================================================
# API ENDPOINTS: TEACHERS
# =====================================================================

@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.role_id.in_([2, 3])))
    users = result.scalars().all()

    teacher_list = []
    for u in users:
        p_res = await db.execute(select(Teacher).where(Teacher.user_id == u.id))
        profile = p_res.scalar_one_or_none()
        teacher_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "subject": profile.subject if profile else None,
            "role_id": u.role_id,
            "created_at": u.created_at,
        })
    return teacher_list

@router.get("/parents", response_model=List[ParentResponse])
async def get_parents(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.role_id == 4))
    users = result.scalars().all()
    
    parent_list = []
    for u in users:
        p_res = await db.execute(select(Parent).where(Parent.user_id == u.id))
        profile = p_res.scalar_one_or_none()
        
        linked_students = []
        if profile:
            students_res = await db.execute(select(User).join(Student, User.id == Student.user_id).where(Student.parent_id == profile.id))
            linked_students = [{"id": s.id, "name": s.name} for s in students_res.scalars().all()]

        parent_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone_number": profile.phone_number if profile else None,
            "role_id": u.role_id,
            "students": linked_students,
            "created_at": u.created_at,
        })
    return parent_list


@router.get("/parents/{parent_id}", response_model=ParentResponse)
async def get_parent(
    parent_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == parent_id, User.role_id == 4))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")
    p_res = await db.execute(select(Parent).where(Parent.user_id == user.id))
    profile = p_res.scalar_one_or_none()
    
    linked_students = []
    if profile:
        students_res = await db.execute(select(User).join(Student, User.id == Student.user_id).where(Student.parent_id == profile.id))
        linked_students = [{"id": s.id, "name": s.name} for s in students_res.scalars().all()]

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": profile.phone_number if profile else None,
        "role_id": user.role_id,
        "students": linked_students,
        "created_at": user.created_at,
    }

@router.post("/parents", response_model=ParentResponse, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent: ParentCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    from db.password import hash_password
    db_user = User(
        name=parent.name,
        email=parent.email,
        role_id=4,
        hashed_password=hash_password(parent.password or "88888888"),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    db_profile = Parent(user_id=db_user.id, phone_number=parent.phone_number)
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_user)

    linked_students = []
    if parent.student_ids:
        for s_id in parent.student_ids:
            s_res = await db.execute(select(Student).where(Student.user_id == s_id))
            student_profile = s_res.scalar_one_or_none()
            if student_profile:
                student_profile.parent_id = db_profile.id
        await db.commit()
        
        students_res = await db.execute(select(User).join(Student, User.id == Student.user_id).where(Student.parent_id == db_profile.id))
        linked_students = [{"id": s.id, "name": s.name} for s in students_res.scalars().all()]

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "phone_number": db_profile.phone_number,
        "role_id": db_user.role_id,
        "students": linked_students,
        "created_at": db_user.created_at,
    }

@router.put("/parents/{parent_id}", response_model=ParentResponse)
async def update_parent(
    parent_id: int,
    parent_data: ParentCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == parent_id, User.role_id == 4))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")

    user.name = parent_data.name
    user.email = parent_data.email
    if parent_data.password:
        from db.password import hash_password
        user.hashed_password = hash_password(parent_data.password)

    p_res = await db.execute(select(Parent).where(Parent.user_id == user.id))
    profile = p_res.scalar_one_or_none()
    if profile:
        profile.phone_number = parent_data.phone_number
    else:
        profile = Parent(user_id=user.id, phone_number=parent_data.phone_number)
        db.add(profile)
        await db.commit()

    if parent_data.student_ids is not None and profile:
        # Clear existing
        await db.execute(
            update(Student)
            .where(Student.parent_id == profile.id)
            .values(parent_id=None)
        )
        # Set new
        if parent_data.student_ids:
            for s_id in parent_data.student_ids:
                s_res = await db.execute(select(Student).where(Student.user_id == s_id))
                student_profile = s_res.scalar_one_or_none()
                if student_profile:
                    student_profile.parent_id = profile.id

    await db.commit()
    await db.refresh(user)
    
    linked_students = []
    if profile:
        students_res = await db.execute(select(User).join(Student, User.id == Student.user_id).where(Student.parent_id == profile.id))
        linked_students = [{"id": s.id, "name": s.name} for s in students_res.scalars().all()]

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": profile.phone_number if profile else None,
        "role_id": user.role_id,
        "students": linked_students,
        "created_at": user.created_at,
    }

@router.delete("/parents/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent(
    parent_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == parent_id, User.role_id == 4))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")
    await db.delete(user)
    await db.commit()
    return None

@router.post("/parents/{parent_id}/reset-password")
async def reset_parent_password(
    parent_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == parent_id, User.role_id == 4))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Parent not found")
    from db.password import hash_password
    default_pw = "88888888"
    user.hashed_password = hash_password(default_pw)
    await db.commit()
    return {"message": "Đã reset mật khẩu thành công", "new_password": default_pw}

@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(User).where(User.id == teacher_id, User.role_id.in_([2, 3])))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    p_res = await db.execute(select(Teacher).where(Teacher.user_id == teacher.id))
    profile = p_res.scalar_one_or_none()
    return {
        "id": teacher.id,
        "name": teacher.name,
        "email": teacher.email,
        "subject": profile.subject if profile else None,
        "role_id": teacher.role_id,
        "created_at": teacher.created_at,
    }

@router.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher: TeacherCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    from db.password import hash_password
    db_user = User(
        name=teacher.name,
        email=teacher.email,
        role_id=teacher.role_id or 2,
        hashed_password=hash_password(teacher.password or "88888888"),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    db_profile = Teacher(user_id=db_user.id, subject=teacher.subject)
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_user)

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "subject": db_profile.subject,
        "role_id": db_user.role_id,
        "created_at": db_user.created_at,
    }

@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == teacher_id, User.role_id.in_([2, 3])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")

    from db.password import hash_password
    update_data = teacher_data.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    if "name" in update_data:
        user.name = update_data["name"]
    if "email" in update_data:
        user.email = update_data["email"]
    if "role_id" in update_data:
        user.role_id = update_data["role_id"]
    if new_password:
        user.hashed_password = hash_password(new_password)

    p_res = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    profile = p_res.scalar_one_or_none()
    if "subject" in update_data:
        if profile:
            profile.subject = update_data["subject"]
        else:
            profile = Teacher(user_id=user.id, subject=update_data["subject"])
            db.add(profile)

    await db.commit()
    await db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "subject": profile.subject if profile else None,
        "role_id": user.role_id,
        "created_at": user.created_at,
    }

@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == teacher_id, User.role_id.in_([2, 3])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    await db.delete(user)
    await db.commit()
    return None


@router.post("/teachers/{teacher_id}/reset-password")
async def reset_teacher_password(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(User).where(User.id == teacher_id, User.role_id.in_([2, 3])))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Teacher not found")
    from db.password import hash_password
    default_pw = "88888888"
    user.hashed_password = hash_password(default_pw)
    await db.commit()
    return {"message": "Đã reset mật khẩu thành công", "new_password": default_pw}


# =====================================================================
# API ENDPOINTS: RANKINGS (Xếp hạng)
# =====================================================================

@router.get("/rankings", response_model=List[RankingResponse])
async def get_rankings(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Ranking).order_by(Ranking.score.desc()))
    return result.scalars().all()

@router.get("/rankings/{ranking_id}", response_model=RankingResponse)
async def get_ranking(
    ranking_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking record not found")
    return ranking

@router.post("/rankings", response_model=RankingResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_ranking(
    ranking: RankingCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    # Check if user exists
    usr_res = await db.execute(select(User).where(User.id == ranking.user_id))
    if not usr_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="User not found")

    # Check if ranking already exists for this user
    exist_res = await db.execute(select(Ranking).where(Ranking.user_id == ranking.user_id))
    db_ranking = exist_res.scalar_one_or_none()

    if db_ranking:
        db_ranking.score = ranking.score
        db_ranking.level = ranking.level
    else:
        db_ranking = Ranking(
            user_id=ranking.user_id,
            score=ranking.score,
            level=ranking.level
        )
        db.add(db_ranking)

    await db.commit()
    await db.refresh(db_ranking)
    return db_ranking

@router.put("/rankings/{ranking_id}", response_model=RankingResponse)
async def update_ranking(
    ranking_id: int,
    ranking_data: RankingUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking record not found")
    
    update_data = ranking_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ranking, key, value)
        
    await db.commit()
    await db.refresh(ranking)
    return ranking

@router.delete("/rankings/{ranking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ranking(
    ranking_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Ranking).where(Ranking.id == ranking_id))
    ranking = result.scalar_one_or_none()
    if not ranking:
        raise HTTPException(status_code=404, detail="Ranking not found")
    await db.delete(ranking)
    await db.commit()
    return None


# =====================================================================
# API ENDPOINTS: QUESTIONS (Ngân hàng câu hỏi)
# =====================================================================

@router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(
    skill_id: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    query = select(Question)
    if skill_id:
        query = query.where(Question.skill_id == skill_id)
    if difficulty:
        query = query.where(Question.difficulty == difficulty)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


# Question Update/Delete Schemas
class QuestionUpdate(BaseModel):
    question_id: Optional[str] = None
    type: Optional[str] = None
    instruction_label: Optional[str] = None
    skill_id: Optional[str] = None
    skill_name: Optional[str] = None
    difficulty: Optional[str] = None
    purpose: Optional[str] = None
    prompt: Optional[dict] = None
    options: Optional[list] = None
    correct_option_id: Optional[str] = None
    explanation: Optional[str] = None


@router.put("/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    data: QuestionUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(question, key, value)

    await db.commit()
    await db.refresh(question)
    return question


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Question).where(Question.id == question_id))
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    # Delete related placement_test_questions first
    await db.execute(delete(PlacementTestQuestion).where(PlacementTestQuestion.question_id == question_id))
    await db.delete(question)
    await db.commit()
    return None


# =====================================================================
# API ENDPOINTS: PLACEMENT TESTS
# =====================================================================

@router.get("/placement-tests", response_model=List[PlacementTestResponse])
async def get_placement_tests(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(PlacementTest))
    return result.scalars().all()

@router.get("/placement-tests/{test_id}", response_model=PlacementTestResponse)
async def get_placement_test(
    test_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")
    return test

@router.get("/placement-tests/{test_id}/questions", response_model=List[QuestionResponse])
async def get_placement_test_questions(
    test_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    # Get test
    test_res = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = test_res.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")
    
    # Get linked questions in order
    links = await db.execute(
        select(PlacementTestQuestion)
        .where(PlacementTestQuestion.test_id == test_id)
        .order_by(PlacementTestQuestion.order_num)
    )
    link_list = links.scalars().all()
    
    questions = []
    for link in link_list:
        q_res = await db.execute(select(Question).where(Question.id == link.question_id))
        q = q_res.scalar_one_or_none()
        if q:
            questions.append(q)
    return questions


# Placement Test Update/Delete Schemas
class PlacementTestUpdate(BaseModel):
    title: Optional[str] = None
    mascot: Optional[dict] = None
    steps: Optional[list] = None
    levels: Optional[list] = None
    adaptive_config: Optional[dict] = None


@router.put("/placement-tests/{test_id}", response_model=PlacementTestResponse)
async def update_placement_test(
    test_id: int,
    data: PlacementTestUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(test, key, value)

    await db.commit()
    await db.refresh(test)
    return test


@router.delete("/placement-tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_placement_test(
    test_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")
    # Delete related links first
    await db.execute(delete(PlacementTestQuestion).where(PlacementTestQuestion.test_id == test_id))
    await db.delete(test)
    await db.commit()
    return None


@router.put("/placement-tests/{test_id}/questions", response_model=List[QuestionResponse])
async def update_placement_test_questions(
    test_id: int,
    question_ids: List[int],
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    """Replace all questions in a placement test with a new ordered list."""
    result = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")

    # Delete old links
    await db.execute(delete(PlacementTestQuestion).where(PlacementTestQuestion.test_id == test_id))

    # Create new links
    for idx, q_id in enumerate(question_ids):
        link = PlacementTestQuestion(test_id=test_id, question_id=q_id, order_num=idx + 1)
        db.add(link)

    await db.commit()

    # Return updated questions
    links = await db.execute(
        select(PlacementTestQuestion)
        .where(PlacementTestQuestion.test_id == test_id)
        .order_by(PlacementTestQuestion.order_num)
    )
    questions = []
    for link in links.scalars().all():
        q_res = await db.execute(select(Question).where(Question.id == link.question_id))
        q = q_res.scalar_one_or_none()
        if q:
            questions.append(q)
    return questions


# =====================================================================
# API ENDPOINTS: TEST RESULTS (Kết quả bài kiểm tra)
# =====================================================================

@router.get("/test-results", response_model=List[TestResultResponse])
async def get_test_results(
    student_id: Optional[int] = None,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    query = select(StudentTestResult)
    if student_id:
        query = query.where(StudentTestResult.user_id == student_id)
    result = await db.execute(query.order_by(StudentTestResult.test_date.desc()))
    return result.scalars().all()

@router.get("/test-results/{result_id}", response_model=TestResultResponse)
async def get_test_result(
    result_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    return test_result

@router.get("/test-results/student/{student_id}", response_model=List[TestResultResponse])
async def get_student_test_results(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Students can only view their own results; admins/teachers may view any student.
    if user.get("role") == "hoc_sinh":
        student_id = user["id"]

    result = await db.execute(
        select(StudentTestResult)
        .where(StudentTestResult.user_id == student_id)
        .order_by(StudentTestResult.test_date.desc())
    )
    return list(result.scalars().all())


@router.patch("/test-results/{result_id}/complete", response_model=TestResultResponse)
async def mark_test_result_complete(
    result_id: int,
    body: TestResultComplete,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")

    # Students can only update their own results.
    if user.get("role") == "hoc_sinh" and test_result.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Không có quyền")

    test_result.roadmap_completed = body.completed
    await db.commit()
    await db.refresh(test_result)
    return test_result


class SelectAlternativePathSubmit(BaseModel):
    path_key: str  # "path_1_back_to_roots", "path_2_pacing_density", or "path_3_alternative_modality"


@router.post("/test-results/{result_id}/select-alternative-path", response_model=TestResultResponse)
async def select_alternative_path(
    result_id: int,
    body: SelectAlternativePathSubmit,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    """Giáo viên chọn 1 trong 3 lộ trình thay thế cho học sinh.
    
    Lộ trình được chọn sẽ được chuyển đổi cấu trúc và cập nhật thành training_plan chính thức.
    """
    # 1. Kiểm tra phân quyền: Chỉ giáo viên hoặc quản trị viên mới có quyền chọn lộ trình
    if user.get("role") == "hoc_sinh":
        raise HTTPException(
            status_code=403, 
            detail="Chỉ giáo viên hoặc quản trị viên mới có quyền chọn lộ trình thay thế cho học sinh."
        )

    # 2. Truy vấn kết quả bài kiểm tra
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")

    # 3. Kiểm tra sự tồn tại của alternative_plans
    if not test_result.alternative_plans or "alternative_paths" not in test_result.alternative_plans:
        raise HTTPException(
            status_code=400, 
            detail="Bài kiểm tra này chưa kích hoạt hoặc không có sẵn lộ trình thay thế để lựa chọn."
        )

    paths = test_result.alternative_plans["alternative_paths"]
    if body.path_key not in paths:
        raise HTTPException(
            status_code=400, 
            detail=f"Mã lộ trình '{body.path_key}' không hợp lệ. Phải là một trong: {list(paths.keys())}"
        )

    selected_path = paths[body.path_key]

    # 4. Chuyển đổi lộ trình thay thế thành định dạng training_plan chuẩn của hệ thống
    from domain.knowledge_graph import get_skill_name
    
    steps = []
    for i, step in enumerate(selected_path.get("action_steps", [])):
        skill_id = step.get("skill_id", "")
        steps.append({
            "step_order": step.get("step_number") or (i + 1),
            "skill_name": get_skill_name(skill_id) if skill_id else "Kỹ năng chưa xác định",
            "encouragement": f"Lộ trình tối ưu do Giáo viên chỉ định: {selected_path.get('primary_difference', '')}",
            "practice_tip": step.get("action_description", ""),
            "home_tip": f"Dành khoảng {step.get('estimated_duration_mins', 20)} phút luyện tập mỗi ngày."
        })

    formatted_plan = {
        "summary": f"Lộ trình học tập thay thế chiến lược '{body.path_key}' do Giáo viên chỉ định. Lý do sư phạm: {selected_path.get('reasoning_cot', '')}",
        "steps": steps,
        "closing": f"Lộ trình kỳ vọng đạt: {selected_path.get('expected_outcome', '')}. Hãy kiên trì học tập nhé!"
    }

    import json
    test_result.training_plan = json.dumps(formatted_plan, ensure_ascii=False)
    
    # 5. Lưu vào CSDL
    await db.commit()
    await db.refresh(test_result)
    
    return test_result


@router.get("/test-results/{result_id}/quick-check-questions")
async def get_quick_check_questions(
    result_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    """Trả ~5 câu liên quan đến lỗ hổng (gaps) của bài đánh giá, để học sinh đánh giá nhanh."""
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")

    if user.get("role") == "hoc_sinh" and test_result.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Không có quyền")

    gaps = test_result.gaps or []
    skill_ids = [g.get("skill_id") for g in gaps if g.get("skill_id")]

    q_result = await db.execute(select(Question))
    all_q = list(q_result.scalars().all())

    filtered = [q for q in all_q if q.skill_id in skill_ids] if skill_ids else []
    # Nếu không đủ câu theo gaps, bổ sung ngẫu nhiên từ ngân hàng
    if len(filtered) < 5:
        extra = [q for q in all_q if q not in filtered]
        import random
        random.shuffle(extra)
        filtered = (filtered + extra)[:5]
    filtered = filtered[:5]

    return [
        {
            "question_id": q.question_id,
            "skill_id": q.skill_id,
            "skill_name": q.skill_name,
            "prompt": q.prompt,
            "options": q.options,
            "correct_option_id": q.correct_option_id,
        }
        for q in filtered
    ]


@router.post("/test-results/{result_id}/quick-check", response_model=QuickCheckResponse)
async def run_quick_check(
    result_id: int,
    body: QuickCheckSubmit,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    """Đánh giá nhanh: chạy BKT trên answers mini-test, so sánh với gaps gốc.
    Nếu mọi gap gốc đạt mastery >= 0.7 -> pass + đánh dấu hoàn thành lộ trình."""
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")

    if user.get("role") == "hoc_sinh" and test_result.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="Không có quyền")

    orig_gaps = test_result.gaps or []
    assessment = run_assessment(body.answers or [], None)
    new_mastery = assessment["mastery"]

    remaining_gaps = []
    for g in orig_gaps:
        prob = (new_mastery.get(g.get("skill_id"), {}) or {}).get("probability") or 0
        if prob < 0.7:
            remaining_gaps.append({
                "skill_id": g.get("skill_id"),
                "skill_name": g.get("skill_name"),
                "probability": round(prob * 100) / 100,
            })

    passed = len(orig_gaps) > 0 and len(remaining_gaps) == 0
    if passed:
        test_result.quick_check_passed = True
        test_result.roadmap_completed = True
        await db.commit()
        await db.refresh(test_result)

    return {
        "passed": passed,
        "roadmap_completed": test_result.roadmap_completed,
        "remaining_gaps": remaining_gaps,
        "mastery": new_mastery,
    }


@router.post("/placement-tests/{test_id}/submit", response_model=TestResultResponse, status_code=status.HTTP_201_CREATED)
async def submit_placement_test(
    test_id: int,
    body: TestResultSubmit,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    result = await db.execute(select(PlacementTest).where(PlacementTest.id == test_id))
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Placement test not found")

    student_id = user["id"]
    if user.get("type") == "student":
        student_id = int(user["sub"])

    test_date = datetime.utcnow()
    if body.test_date:
        try:
            dt = datetime.fromisoformat(body.test_date.replace("Z", "+00:00"))
            test_date = dt.replace(tzinfo=None)
        except Exception:
            pass

    # --- Tầng 2: BKT Engine chẩn đoán lỗ hổng (ưu tiên backend, fallback body) ---
    mastery = body.mastery
    gaps = body.gaps
    try:
        from domain.bkt import run_assessment

        assessment = run_assessment(body.answers or [], None)
        # Chỉ ghi đè khi body không mang sẵn kết quả (giữ tương thích ngược)
        if not mastery:
            mastery = assessment["mastery"]
        if not gaps:
            gaps = assessment["gaps"]
    except Exception as e:
        print(f"[BKT] assessment failed, using client values: {e}")

    # --- Tầng 3: LLM sinh kế hoạch đào tạo cá nhân hóa (FPT / DeepSeek) ---
    training_plan = body.training_plan
    try:
        from tools.plan_tool import generate_training_plan

        training_plan = generate_training_plan(
            gaps=gaps or [],
            mastery=mastery or {},
            student_name=user.get("name", ""),
            level=body.cefr,
            audience="student",
        )
    except Exception as e:
        print(f"[LLM] training plan generation failed: {e}")
        training_plan = None

    # Query các lần làm bài trước đó của học sinh cho cùng test_id
    previous_attempts_result = await db.execute(
        select(StudentTestResult)
        .where(StudentTestResult.user_id == student_id)
        .where(StudentTestResult.test_id == test_id)
        .order_by(StudentTestResult.test_date.desc())
    )
    previous_attempts = list(previous_attempts_result.scalars().all())

    # --- Tách riêng tính toán điều kiện kích hoạt đề xuất lộ trình mới ---
    alternative_plans = None

    if len(previous_attempts) >= 2:
        last_attempt = previous_attempts[0]
        
        # 1. Bộ lọc thời gian tối thiểu >= 10 phút (600 giây)
        time_gap_sec = (test_date - last_attempt.test_date).total_seconds()
        is_time_gap_ok = time_gap_sec >= 600
        
        # 2. Bộ lọc tỷ lệ hoàn thành >= 80%
        total_questions = 1
        try:
            from sqlalchemy import func
            from db.models import PlacementTestQuestion
            q_count_res = await db.execute(
                select(func.count(PlacementTestQuestion.id))
                .where(PlacementTestQuestion.test_id == test_id)
            )
            total_questions = q_count_res.scalar() or 1
        except Exception:
            total_questions = max(len(body.answers or []), len(last_attempt.answers or []), 1)
            
        completion_rate = len(body.answers or []) / total_questions
        is_completion_rate_ok = completion_rate >= 0.8
        
        # 3. Chưa đạt kết quả tốt (<50%): điểm phần trăm dưới 50
        is_score_low = body.percentage < 50.0
        
        if is_time_gap_ok and is_completion_rate_ok and is_score_low:
            try:
                from tools.plan_tool import generate_alternative_plans
                alternative_plans = generate_alternative_plans(
                    gaps=gaps or [],
                    mastery=mastery or {},
                    student_name=user.get("name", ""),
                    level=body.cefr,
                    old_plan=training_plan
                )
            except Exception as e:
                print(f"[LLM Alternative Plan] error: {e}")
                alternative_plans = None

    test_result = StudentTestResult(
        user_id=student_id,
        test_id=test_id,
        answers=body.answers,
        score=body.score,
        max_score=body.max_score,
        percentage=body.percentage,
        result_level=body.result_level,
        cefr=body.cefr,
        time_total_sec=body.time_total_sec,
        mastery=mastery,
        gaps=gaps,
        recommendations=body.recommendations,
        training_plan=training_plan,
        alternative_plans=alternative_plans,
        test_date=test_date,
    )
    db.add(test_result)

    level_map = {
        "starter": "Starter",
        "beginner": "Beginner",
        "elementary": "Intermediate",
    }
    ranking_level = level_map.get(body.result_level, body.result_level)
    ranking_score = body.score

    ranking_result = await db.execute(select(Ranking).where(Ranking.user_id == student_id))
    ranking = ranking_result.scalar_one_or_none()
    if ranking:
        ranking.score = ranking_score
        ranking.level = ranking_level
    else:
        ranking = Ranking(user_id=student_id, score=ranking_score, level=ranking_level)
        db.add(ranking)

    await db.commit()
    await db.refresh(test_result)
    return test_result


# =====================================================================
# NEW ENDPOINTS FOR TEACHER-STUDENT-PARENT & APPROVAL
# =====================================================================

@router.post("/test-results/{result_id}/approve", response_model=TestResultResponse)
async def approve_roadmap(
    result_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(require_role("giao_vien", "admin")), # Teachers and admins can approve
):
    result = await db.execute(select(StudentTestResult).where(StudentTestResult.id == result_id))
    test_result = result.scalar_one_or_none()
    if not test_result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    test_result.is_roadmap_approved = True
    await db.commit()
    await db.refresh(test_result)
    return test_result

@router.get("/teachers/{teacher_user_id}/students", response_model=List[StudentResponse])
async def get_teacher_students(
    teacher_user_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Find teacher id from user id
    t_res = await db.execute(select(Teacher).where(Teacher.user_id == teacher_user_id))
    teacher = t_res.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found")
        
    # Get students
    students_res = await db.execute(select(Student).where(Student.primary_teacher_id == teacher.id))
    students = list(students_res.scalars().all())
    
    # Get corresponding users
    user_ids = [s.user_id for s in students]
    if not user_ids:
        return []
        
    users_res = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = list(users_res.scalars().all())
    
    return await _format_students(db, users)

@router.get("/parents/{parent_user_id}/students", response_model=List[StudentResponse])
async def get_parent_students(
    parent_user_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Find parent id from user id
    p_res = await db.execute(select(Parent).where(Parent.user_id == parent_user_id))
    parent = p_res.scalar_one_or_none()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent profile not found")
        
    # Get students
    students_res = await db.execute(select(Student).where(Student.parent_id == parent.id))
    students = list(students_res.scalars().all())
    
    # Get corresponding users
    user_ids = [s.user_id for s in students]
    if not user_ids:
        return []
        
    users_res = await db.execute(select(User).where(User.id.in_(user_ids)))
    users = list(users_res.scalars().all())
    
    return await _format_students(db, users)

class EvaluationCreate(BaseModel):
    comment: str

@router.post("/students/{user_id}/evaluations", response_model=TeacherEvaluationResponse)
async def create_teacher_evaluation(
    user_id: int,
    payload: EvaluationCreate,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(require_role("giao_vien", "admin")),
):
    # Lookup teacher profile — admin may not have one, so we handle gracefully
    t_res = await db.execute(select(Teacher).where(Teacher.user_id == user["id"]))
    teacher = t_res.scalar_one_or_none()

    # If admin without teacher profile, we still allow evaluation with teacher_id=None
    teacher_id = teacher.id if teacher else None

    s_res = await db.execute(select(Student).where(Student.user_id == user_id))
    student = s_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    eval_entry = TeacherEvaluation(student_id=student.id, teacher_id=teacher_id, comment=payload.comment)
    db.add(eval_entry)
    await db.commit()
    await db.refresh(eval_entry)

    t_user_res = await db.execute(select(User).where(User.id == user["id"]))
    t_user = t_user_res.scalar_one()

    return {
        "id": eval_entry.id,
        "student_id": eval_entry.student_id,
        "teacher_id": eval_entry.teacher_id,
        "teacher_name": t_user.name,
        "comment": eval_entry.comment,
        "created_at": eval_entry.created_at
    }

@router.get("/students/{user_id}/evaluations", response_model=List[TeacherEvaluationResponse])
async def get_student_evaluations(
    user_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    s_res = await db.execute(select(Student).where(Student.user_id == user_id))
    student = s_res.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")

    result = await db.execute(
        select(TeacherEvaluation, User.name)
        .join(Teacher, TeacherEvaluation.teacher_id == Teacher.id)
        .join(User, Teacher.user_id == User.id)
        .where(TeacherEvaluation.student_id == student.id)
        .order_by(TeacherEvaluation.created_at.desc())
    )
    
    evals = []
    for row in result.all():
        eval_item, name = row
        evals.append({
            "id": eval_item.id,
            "student_id": eval_item.student_id,
            "teacher_id": eval_item.teacher_id,
            "teacher_name": name,
            "comment": eval_item.comment,
            "created_at": eval_item.created_at
        })
    return evals

"""CRUD routes for Roles, Students, Teachers, Rankings, and Survey Evaluations."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import Role, Student, Teacher, Ranking, SurveyEvaluation
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


# Survey Evaluation Schemas
class SurveyBase(BaseModel):
    years_studying_english: int
    learning_environment: Optional[str] = None
    self_assessment_level: Optional[str] = None
    learning_goal: Optional[str] = None

class SurveyCreate(SurveyBase):
    student_id: int

class SurveyResponse(SurveyBase):
    id: int
    student_id: int
    created_at: datetime
    class Config:
        from_attributes = True


# Ranking Schemas
class RankingBase(BaseModel):
    score: int
    level: str

class RankingCreate(RankingBase):
    student_id: int

class RankingUpdate(BaseModel):
    score: Optional[int] = None
    level: Optional[str] = None

class RankingResponse(RankingBase):
    id: int
    student_id: int
    updated_at: datetime
    class Config:
        from_attributes = True


# Student Schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr
    grade: Optional[str] = None
    role_id: Optional[int] = 1

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    grade: Optional[str] = None
    role_id: Optional[int] = None

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    ranking: Optional[RankingResponse] = None
    surveys: List[SurveyResponse] = []
    class Config:
        from_attributes = True


# Teacher Schemas
class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    subject: Optional[str] = None
    role_id: Optional[int] = 2

class TeacherCreate(TeacherBase):
    pass

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    subject: Optional[str] = None
    role_id: Optional[int] = None

class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


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

@router.get("/students", response_model=List[StudentResponse])
async def get_students(
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Students can only see themselves
    if user["role"] == "hoc_sinh":
        result = await db.execute(select(Student).where(Student.id == user["id"]))
        students = list(result.scalars().all())
    else:
        result = await db.execute(select(Student))
        students = list(result.scalars().all())
    
    student_list = []
    for s in students:
        rank_res = await db.execute(select(Ranking).where(Ranking.student_id == s.id))
        ranking_obj = rank_res.scalar_one_or_none()
        survey_res = await db.execute(select(SurveyEvaluation).where(SurveyEvaluation.student_id == s.id))
        surveys_obj = list(survey_res.scalars().all())
        
        student_list.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "grade": s.grade,
            "role_id": s.role_id,
            "created_at": s.created_at,
            "ranking": ranking_obj,
            "surveys": surveys_obj
        })
    return student_list

@router.get("/students/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    user: dict = Depends(get_current_user),
):
    # Students can only see themselves
    if user["role"] == "hoc_sinh" and user["id"] != student_id:
        raise HTTPException(status_code=403, detail="Ban chi co the xem du lieu cua chinh minh")

    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    rank_res = await db.execute(select(Ranking).where(Ranking.student_id == student.id))
    ranking_obj = rank_res.scalar_one_or_none()
    
    survey_res = await db.execute(select(SurveyEvaluation).where(SurveyEvaluation.student_id == student.id))
    surveys_obj = list(survey_res.scalars().all())
    
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": student.grade,
        "role_id": student.role_id,
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "surveys": surveys_obj
    }

@router.post("/students", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student: StudentCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    from db.password import hash_password
    db_student = Student(
        name=student.name,
        email=student.email,
        grade=student.grade,
        role_id=student.role_id,
        hashed_password=hash_password("default123"),
    )
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    
    db_ranking = Ranking(student_id=db_student.id, score=0, level="Beginner")
    db.add(db_ranking)
    await db.commit()
    await db.refresh(db_student)
    
    rank_res = await db.execute(select(Ranking).where(Ranking.student_id == db_student.id))
    ranking_obj = rank_res.scalar_one_or_none()
    
    return {
        "id": db_student.id,
        "name": db_student.name,
        "email": db_student.email,
        "grade": db_student.grade,
        "role_id": db_student.role_id,
        "created_at": db_student.created_at,
        "ranking": ranking_obj,
        "surveys": []
    }

@router.put("/students/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_data = student_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(student, key, value)
        
    await db.commit()
    await db.refresh(student)
    
    # Reload relationships
    rank_res = await db.execute(select(Ranking).where(Ranking.student_id == student.id))
    ranking_obj = rank_res.scalar_one_or_none()
    survey_res = await db.execute(select(SurveyEvaluation).where(SurveyEvaluation.student_id == student.id))
    surveys_obj = list(survey_res.scalars().all())
    
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": student.grade,
        "role_id": student.role_id,
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "surveys": surveys_obj
    }

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await db.delete(student)
    await db.commit()
    return None


# =====================================================================
# API ENDPOINTS: TEACHERS
# =====================================================================

@router.get("/teachers", response_model=List[TeacherResponse])
async def get_teachers(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Teacher))
    return result.scalars().all()

@router.get("/teachers/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher

@router.post("/teachers", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher: TeacherCreate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    from db.password import hash_password
    db_teacher = Teacher(
        name=teacher.name,
        email=teacher.email,
        subject=teacher.subject,
        role_id=teacher.role_id,
        hashed_password=hash_password("default123"),
    )
    db.add(db_teacher)
    await db.commit()
    await db.refresh(db_teacher)
    return db_teacher

@router.put("/teachers/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    
    update_data = teacher_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(teacher, key, value)
        
    await db.commit()
    await db.refresh(teacher)
    return teacher

@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    await db.delete(teacher)
    await db.commit()
    return None


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
    # Check if student exists
    std_res = await db.execute(select(Student).where(Student.id == ranking.student_id))
    if not std_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Check if ranking already exists for this student
    exist_res = await db.execute(select(Ranking).where(Ranking.student_id == ranking.student_id))
    db_ranking = exist_res.scalar_one_or_none()
    
    if db_ranking:
        db_ranking.score = ranking.score
        db_ranking.level = ranking.level
    else:
        db_ranking = Ranking(
            student_id=ranking.student_id,
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
# API ENDPOINTS: SURVEY EVALUATIONS (Khảo sát)
# =====================================================================

@router.get("/surveys", response_model=List[SurveyResponse])
async def get_surveys(
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SurveyEvaluation))
    return result.scalars().all()

@router.get("/surveys/{survey_id}", response_model=SurveyResponse)
async def get_survey(
    survey_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SurveyEvaluation).where(SurveyEvaluation.id == survey_id))
    survey = result.scalar_one_or_none()
    if not survey:
        raise HTTPException(status_code=404, detail="Survey evaluation not found")
    return survey

@router.post("/surveys", response_model=SurveyResponse, status_code=status.HTTP_201_CREATED)
async def create_survey(
    survey: SurveyCreate,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    # Check if student exists
    std_res = await db.execute(select(Student).where(Student.id == survey.student_id))
    if not std_res.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Student not found")
        
    db_survey = SurveyEvaluation(
        student_id=survey.student_id,
        years_studying_english=survey.years_studying_english,
        learning_environment=survey.learning_environment,
        self_assessment_level=survey.self_assessment_level,
        learning_goal=survey.learning_goal
    )
    db.add(db_survey)
    await db.commit()
    await db.refresh(db_survey)
    return db_survey

@router.get("/surveys/student/{student_id}", response_model=List[SurveyResponse])
async def get_student_surveys(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(select(SurveyEvaluation).where(SurveyEvaluation.student_id == student_id))
    return list(result.scalars().all())

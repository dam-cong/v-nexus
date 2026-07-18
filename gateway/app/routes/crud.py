"""CRUD routes for Roles, Students, Teachers, Rankings, Questions, Placement Tests, and Test Results."""
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.connector import get_session
from db.models import (
    Role, Student, Teacher, Ranking,
    Question, PlacementTest, PlacementTestQuestion, StudentTestResult,
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
    years_studying_english: Optional[int] = None
    learning_environment: Optional[str] = None
    self_assessment_level: Optional[str] = None
    learning_goal: Optional[str] = None

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
    student_id: int
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
    roadmap_completed: bool = False
    quick_check_passed: bool = False
    test_date: datetime
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
        tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.student_id == s.id))
        test_results_obj = list(tr_res.scalars().all())
        
        student_list.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "grade": s.grade,
            "role_id": s.role_id,
            "years_studying_english": s.years_studying_english,
            "learning_environment": s.learning_environment,
            "self_assessment_level": s.self_assessment_level,
            "learning_goal": s.learning_goal,
            "training_plan": s.training_plan,
            "created_at": s.created_at,
            "ranking": ranking_obj,
            "test_results": test_results_obj,
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
    
    tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.student_id == student.id))
    test_results_obj = list(tr_res.scalars().all())
    
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": student.grade,
        "role_id": student.role_id,
        "years_studying_english": student.years_studying_english,
        "learning_environment": student.learning_environment,
        "self_assessment_level": student.self_assessment_level,
        "learning_goal": student.learning_goal,
        "training_plan": student.training_plan,
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
    
    # Generate training plan from survey if provided
    training_plan = None
    if student.years_studying_english is not None or student.learning_goal:
        try:
            from tools.plan_tool import generate_training_plan_from_survey
            training_plan = generate_training_plan_from_survey(
                student_name=student.name,
                grade=student.grade or "Lớp 6",
                years_studying_english=student.years_studying_english or 0,
                learning_environment=student.learning_environment or "school",
                self_assessment_level=student.self_assessment_level or "A1",
                learning_goal=student.learning_goal or ""
            )
        except Exception as e:
            print(f"[LLM] Failed to generate training plan from survey: {e}")

    db_student = Student(
        name=student.name,
        email=student.email,
        grade=student.grade,
        role_id=student.role_id,
        years_studying_english=student.years_studying_english,
        learning_environment=student.learning_environment,
        self_assessment_level=student.self_assessment_level,
        learning_goal=student.learning_goal,
        training_plan=training_plan,
        hashed_password=hash_password(student.password or "88888888"),
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
        "years_studying_english": db_student.years_studying_english,
        "learning_environment": db_student.learning_environment,
        "self_assessment_level": db_student.self_assessment_level,
        "learning_goal": db_student.learning_goal,
        "training_plan": db_student.training_plan,
        "created_at": db_student.created_at,
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
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    from db.password import hash_password
    update_data = student_data.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    for key, value in update_data.items():
        setattr(student, key, value)
    if new_password:
        student.hashed_password = hash_password(new_password)
        
    await db.commit()
    await db.refresh(student)
    
    # Reload relationships
    rank_res = await db.execute(select(Ranking).where(Ranking.student_id == student.id))
    ranking_obj = rank_res.scalar_one_or_none()
    tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.student_id == student.id))
    test_results_obj = list(tr_res.scalars().all())
    
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": student.grade,
        "role_id": student.role_id,
        "years_studying_english": student.years_studying_english,
        "learning_environment": student.learning_environment,
        "self_assessment_level": student.self_assessment_level,
        "learning_goal": student.learning_goal,
        "training_plan": student.training_plan,
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "test_results": test_results_obj,
    }

@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    await db.delete(student)
    await db.commit()
    return None


@router.post("/students/{student_id}/reset-password")
async def reset_student_password(
    student_id: int,
    db: AsyncSession = Depends(get_session),
    _user: dict = Depends(require_role("admin", "giao_vien")),
):
    result = await db.execute(select(Student).where(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    from db.password import hash_password
    default_pw = "88888888"
    student.hashed_password = hash_password(default_pw)
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
        hashed_password=hash_password(teacher.password or "88888888"),
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
    
    from db.password import hash_password
    update_data = teacher_data.model_dump(exclude_unset=True)
    new_password = update_data.pop("password", None)
    for key, value in update_data.items():
        setattr(teacher, key, value)
    if new_password:
        teacher.hashed_password = hash_password(new_password)
        
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


@router.post("/teachers/{teacher_id}/reset-password")
async def reset_teacher_password(
    teacher_id: int,
    db: AsyncSession = Depends(get_session),
    _admin: dict = Depends(require_role("admin")),
):
    result = await db.execute(select(Teacher).where(Teacher.id == teacher_id))
    teacher = result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    from db.password import hash_password
    default_pw = "88888888"
    teacher.hashed_password = hash_password(default_pw)
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
        query = query.where(StudentTestResult.student_id == student_id)
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
        .where(StudentTestResult.student_id == student_id)
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
    if user.get("role") == "hoc_sinh" and test_result.student_id != user["id"]:
        raise HTTPException(status_code=403, detail="Không có quyền")

    test_result.roadmap_completed = body.completed
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

    if user.get("role") == "hoc_sinh" and test_result.student_id != user["id"]:
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

    if user.get("role") == "hoc_sinh" and test_result.student_id != user["id"]:
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

    test_result = StudentTestResult(
        student_id=student_id,
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

    ranking_result = await db.execute(select(Ranking).where(Ranking.student_id == student_id))
    ranking = ranking_result.scalar_one_or_none()
    if ranking:
        ranking.score = ranking_score
        ranking.level = ranking_level
    else:
        ranking = Ranking(student_id=student_id, score=ranking_score, level=ranking_level)
        db.add(ranking)

    await db.commit()
    await db.refresh(test_result)
    return test_result

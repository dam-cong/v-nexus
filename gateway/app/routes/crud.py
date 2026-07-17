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
    test_date: datetime
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
        tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.student_id == s.id))
        test_results_obj = list(tr_res.scalars().all())
        
        student_list.append({
            "id": s.id,
            "name": s.name,
            "email": s.email,
            "grade": s.grade,
            "role_id": s.role_id,
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
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "test_results": test_results_obj,
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
        "test_results": [],
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
    tr_res = await db.execute(select(StudentTestResult).where(StudentTestResult.student_id == student.id))
    test_results_obj = list(tr_res.scalars().all())
    
    return {
        "id": student.id,
        "name": student.name,
        "email": student.email,
        "grade": student.grade,
        "role_id": student.role_id,
        "created_at": student.created_at,
        "ranking": ranking_obj,
        "test_results": test_results_obj,
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
    _user: dict = Depends(get_current_user),
):
    result = await db.execute(
        select(StudentTestResult)
        .where(StudentTestResult.student_id == student_id)
        .order_by(StudentTestResult.test_date.desc())
    )
    return list(result.scalars().all())

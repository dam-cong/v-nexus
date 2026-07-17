"""Bài kiểm tra chẩn đoán — chấm ở server, không tin is_correct từ client."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select

from db.connector import get_session
from db.models import Question, Skill, Student, User, UserRole
from domain.bkt import find_root_gaps
from domain.knowledge_graph import load_knowledge_graph
from domain.mastery_store import get_mastery_snapshot, record_response

from ..auth import require_role

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])
_graph = load_knowledge_graph()


async def _student_for(user: User, session) -> Student:
    student = (
        await session.execute(select(Student).where(Student.user_id == user.id))
    ).scalar_one_or_none()
    if student is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy hồ sơ học sinh cho tài khoản này.")
    return student


class QuestionOut(BaseModel):
    question_id: int
    content: str
    question_type: str
    options: list | None


class SubmitAnswerIn(BaseModel):
    question_id: int
    student_answer: str


class SubmitAnswerOut(BaseModel):
    is_correct: bool
    skill_code: str
    p_mastery_before: float
    p_mastery_after: float
    explanations: list[str]


class GapOut(BaseModel):
    skill_code: str
    skill_name: str
    confidence: float
    grade: int


class CompleteOut(BaseModel):
    gaps: list[GapOut]
    recommended_start_skill: str | None


@router.get("/questions", response_model=list[QuestionOut])
async def list_diagnostic_questions(session=Depends(get_session)):
    rows = (await session.execute(select(Question))).scalars().all()
    return [
        QuestionOut(
            question_id=q.id, content=q.content, question_type=q.question_type, options=q.options
        )
        for q in rows
    ]


@router.post("/submit-answer", response_model=SubmitAnswerOut)
async def submit_diagnostic_answer(
    body: SubmitAnswerIn,
    session=Depends(get_session),
    user: User = Depends(require_role(UserRole.student)),
):
    student = await _student_for(user, session)
    result = await record_response(
        session=session,
        student_id=student.id,
        question_id=body.question_id,
        student_answer=body.student_answer,
        session_type="diagnostic",
        graph=_graph,
    )
    return SubmitAnswerOut(
        is_correct=result["is_correct"],
        skill_code=result["skill_code"],
        p_mastery_before=result["p_mastery_before"],
        p_mastery_after=result["p_mastery_after"],
        explanations=result["explanations"],
    )


@router.post("/complete", response_model=CompleteOut)
async def complete_diagnostic(
    session=Depends(get_session),
    user: User = Depends(require_role(UserRole.student)),
):
    student = await _student_for(user, session)
    mastery = await get_mastery_snapshot(session, student.id, _graph)
    root_gaps = find_root_gaps(_graph, mastery)
    return CompleteOut(
        gaps=[
            GapOut(
                skill_code=code,
                skill_name=_graph.skill_name(code),
                confidence=round(1 - mastery[code].p_mastery, 2),
                grade=_graph.skill(code)["grade"],
            )
            for code in root_gaps
        ],
        recommended_start_skill=root_gaps[0] if root_gaps else None,
    )

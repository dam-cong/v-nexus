"""Lộ trình luyện tập cá nhân hóa — nối tiếp bài chẩn đoán."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from db.connector import get_session
from db.models import User, UserRole
from domain.knowledge_graph import load_knowledge_graph
from domain.mastery_store import record_response
from domain.practice_selector import generate_practice_path

from .diagnostic import SubmitAnswerIn, SubmitAnswerOut, _student_for
from ..auth import require_role

router = APIRouter(prefix="/practice", tags=["practice"])
_graph = load_knowledge_graph()


class PracticeItemOut(BaseModel):
    question_id: int
    skill_code: str
    skill_name: str
    content: str
    question_type: str
    options: list | None
    difficulty: int


@router.get("/path", response_model=list[PracticeItemOut])
async def get_practice_path(
    max_items: int = 10,
    session=Depends(get_session),
    user: User = Depends(require_role(UserRole.student)),
):
    student = await _student_for(user, session)
    path = await generate_practice_path(session, student.id, _graph, max_items)
    return [PracticeItemOut(**item) for item in path]


@router.post("/submit-answer", response_model=SubmitAnswerOut)
async def submit_practice_answer(
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
        session_type="practice",
        graph=_graph,
    )
    return SubmitAnswerOut(
        is_correct=result["is_correct"],
        skill_code=result["skill_code"],
        p_mastery_before=result["p_mastery_before"],
        p_mastery_after=result["p_mastery_after"],
        explanations=result["explanations"],
    )

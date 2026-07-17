"""Endpoint /chat — cầu nối duy nhất giữa frontend và Planner Agent."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent.planner import PlannerAgent
from domain.adaptive_tutor_adapter import AdaptiveTutorAdapter

from ..config import settings

router = APIRouter()
_adapter = AdaptiveTutorAdapter()
_agent = PlannerAgent(domain=_adapter, model=settings.llm_model)


class ChatRequest(BaseModel):
    message: str
    student_id: str = ""
    role: str = "student"
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    history: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if req.role not in ("student", "teacher", "parent"):
        raise HTTPException(status_code=422, detail="role must be student, teacher, or parent")
    reply, history = await _agent.run(req.message, req.history)
    return ChatResponse(reply=reply, history=history)

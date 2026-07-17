"""Endpoint /chat — bot hỏi-đáp phụ (online), gọi Planner Agent + Tool Registry.

Bề mặt sản phẩm chính là /diagnostic /practice /teacher /parent (REST, access control
thực thi bằng code). /chat là lớp tiện ích cộng thêm, xem lưu ý về access-control ở
domain/adaptive_tutor_adapter.py.
"""
from fastapi import APIRouter
from pydantic import BaseModel

from agent.planner import PlannerAgent
from domain.adaptive_tutor_adapter import AdaptiveTutorAdapter

from ..config import settings

router = APIRouter()
_adapter = AdaptiveTutorAdapter()
_agent = PlannerAgent(domain=_adapter, model=settings.llm_model)


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str
    history: list[dict]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    reply, history = await _agent.run(req.message, req.history)
    return ChatResponse(reply=reply, history=history)

"""Endpoint /chat — cầu nối duy nhất giữa frontend và Planner Agent."""
from fastapi import APIRouter
from pydantic import BaseModel

from agent.planner import PlannerAgent
from domain.sme_innovation_adapter import VNexusTutorAdapter

from ..config import settings

router = APIRouter()
_adapter = VNexusTutorAdapter()
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

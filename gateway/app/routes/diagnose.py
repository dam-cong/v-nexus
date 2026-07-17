"""Endpoint /diagnose — chẩn đoán lỗ hổng kiến thức trực tiếp (không qua chat)."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from ai.bkt_engine import GapResult
from domain.adaptive_tutor_adapter import AdaptiveTutorAdapter

router = APIRouter()

_adapter: AdaptiveTutorAdapter | None = None


def _get_adapter() -> AdaptiveTutorAdapter:
    global _adapter
    if _adapter is None:
        _adapter = AdaptiveTutorAdapter()
    return _adapter


class AnswerItem(BaseModel):
    question_id: str
    skill_id: str
    correct: bool


class DiagnoseRequest(BaseModel):
    student_id: str
    answers: list[AnswerItem]


class GapItem(BaseModel):
    skill_id: str
    skill_name: str
    mastery_prob: float
    gap_depth: int
    grade: int
    explanation: str
    recommended_action: str


class DiagnoseResponse(BaseModel):
    student_id: str
    total_answers: int
    correct_count: int
    gaps: list[GapItem]
    mastery_snapshot: dict[str, float]
    has_gaps: bool
    summary: str


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(req: DiagnoseRequest) -> DiagnoseResponse:
    adapter = _get_adapter()
    engine = adapter.engine

    if not req.answers:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Danh sách answers không được rỗng.")

    wrong_skills: set[str] = set()
    for ans in req.answers:
        engine.update(req.student_id, ans.skill_id, ans.correct)
        if not ans.correct:
            wrong_skills.add(ans.skill_id)

    all_gaps: list[GapResult] = []
    for skill_id in wrong_skills:
        gaps = engine.diagnose_root_cause(req.student_id, skill_id)
        all_gaps.extend(gaps)

    seen: set[str] = set()
    unique_gaps: list[GapResult] = []
    for g in all_gaps:
        if g.skill_id not in seen:
            seen.add(g.skill_id)
            unique_gaps.append(g)
    unique_gaps.sort(key=lambda g: g.gap_depth, reverse=True)

    mastery_snapshot = engine.get_all_mastery(req.student_id)
    correct_count = sum(1 for a in req.answers if a.correct)

    if not unique_gaps:
        summary = f"Học sinh {req.student_id} trả lời đúng {correct_count}/{len(req.answers)}. Không phát hiện lỗ hổng."
    else:
        deepest = unique_gaps[0]
        summary = (
            f"Học sinh {req.student_id} trả lời đúng {correct_count}/{len(req.answers)}. "
            f"Phát hiện {len(unique_gaps)} lỗ hổng. Ưu tiên: {deepest.recommended_action}"
        )

    return DiagnoseResponse(
        student_id=req.student_id,
        total_answers=len(req.answers),
        correct_count=correct_count,
        gaps=[
            GapItem(
                skill_id=g.skill_id, skill_name=g.skill_name,
                mastery_prob=g.mastery_prob, gap_depth=g.gap_depth,
                grade=g.grade, explanation=g.explanation,
                recommended_action=g.recommended_action,
            )
            for g in unique_gaps
        ],
        mastery_snapshot={k: round(v, 4) for k, v in mastery_snapshot.items()},
        has_gaps=len(unique_gaps) > 0,
        summary=summary,
    )

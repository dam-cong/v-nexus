"""Lớp DB-facing nối domain/bkt.py (thuần) với StudentResponse/StudentSkillMastery."""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Question, Skill, StudentResponse, StudentSkillMastery
from domain.bkt import (
    FAIL_THRESHOLD,
    MasteryState,
    bayes_update,
    explain_trace,
    propagate_to_prerequisites,
)
from domain.knowledge_graph import KnowledgeGraph


async def _load_mastery_map(
    session: AsyncSession, student_id: int, graph: KnowledgeGraph
) -> dict[str, MasteryState]:
    rows = (
        await session.execute(
            select(StudentSkillMastery, Skill.code)
            .join(Skill, Skill.id == StudentSkillMastery.skill_id)
            .where(StudentSkillMastery.student_id == student_id)
        )
    ).all()
    mastery: dict[str, MasteryState] = {}
    existing_codes = set()
    for row, code in rows:
        mastery[code] = MasteryState(
            p_mastery=row.p_mastery, attempts=row.attempts, correct_count=row.correct_count
        )
        existing_codes.add(code)
    for code in graph.skill_codes():
        if code not in existing_codes:
            mastery[code] = MasteryState(p_mastery=graph.bkt_params(code).p_init)
    return mastery


async def _persist_mastery(
    session: AsyncSession, student_id: int, skill_code: str, skill_id: int, state: MasteryState
) -> None:
    existing = (
        await session.execute(
            select(StudentSkillMastery).where(
                StudentSkillMastery.student_id == student_id,
                StudentSkillMastery.skill_id == skill_id,
            )
        )
    ).scalar_one_or_none()
    was_weak = existing is not None and existing.p_mastery < FAIL_THRESHOLD
    now_weak = state.p_mastery < FAIL_THRESHOLD

    if existing is None:
        existing = StudentSkillMastery(student_id=student_id, skill_id=skill_id)
        session.add(existing)

    existing.p_mastery = state.p_mastery
    existing.attempts = state.attempts
    existing.correct_count = state.correct_count

    if now_weak and not was_weak:
        existing.stuck_since = datetime.utcnow()
    elif not now_weak:
        existing.stuck_since = None


async def record_response(
    session: AsyncSession,
    student_id: int,
    question_id: int,
    student_answer: str,
    session_type: str,
    graph: KnowledgeGraph,
) -> dict:
    """Chấm 1 câu trả lời ở server, chạy BKT update + lan truyền, lưu DB.

    Trả về dict có is_correct, skill_code, p_mastery_before/after, propagation trace.
    """
    question = (
        await session.execute(select(Question).where(Question.id == question_id))
    ).scalar_one()
    skill = (await session.execute(select(Skill).where(Skill.id == question.skill_id))).scalar_one()
    skill_code = skill.code

    is_correct = student_answer.strip().lower() == question.correct_answer.strip().lower()

    mastery = await _load_mastery_map(session, student_id, graph)
    params_by_skill = {code: graph.bkt_params(code) for code in graph.skill_codes()}

    state = mastery[skill_code]
    params = params_by_skill[skill_code]
    p_before = state.p_mastery
    state.p_mastery = bayes_update(
        p_before, is_correct, params.p_slip, params.p_guess, params.p_transit
    )
    state.attempts += 1
    if is_correct:
        state.correct_count += 1

    trace = propagate_to_prerequisites(skill_code, graph, mastery, params_by_skill)

    session.add(
        StudentResponse(
            student_id=student_id,
            question_id=question_id,
            skill_id=skill.id,
            is_correct=is_correct,
            session_type=session_type,
            p_mastery_before=p_before,
            p_mastery_after=state.p_mastery,
        )
    )

    skill_rows = (await session.execute(select(Skill))).scalars().all()
    skill_id_by_code = {s.code: s.id for s in skill_rows}
    for code, m_state in mastery.items():
        await _persist_mastery(session, student_id, code, skill_id_by_code[code], m_state)

    await session.commit()

    return {
        "is_correct": is_correct,
        "skill_code": skill_code,
        "p_mastery_before": p_before,
        "p_mastery_after": state.p_mastery,
        "propagation": [
            {
                "skill_code": e.skill_code,
                "from": e.p_before,
                "to": e.p_after,
                "reason_skill_code": e.reason_skill_code,
                "depth": e.depth,
            }
            for e in trace
        ],
        "explanations": explain_trace(trace, graph),
    }


async def get_mastery_snapshot(
    session: AsyncSession, student_id: int, graph: KnowledgeGraph
) -> dict[str, MasteryState]:
    return await _load_mastery_map(session, student_id, graph)

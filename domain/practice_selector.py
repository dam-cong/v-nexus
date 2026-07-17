"""Sinh lộ trình luyện tập cá nhân hóa từ gap đã chẩn đoán — không phải LLM tự chọn bài."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Question, Skill
from domain.bkt import find_root_gaps
from domain.knowledge_graph import KnowledgeGraph
from domain.mastery_store import get_mastery_snapshot


async def generate_practice_path(
    session: AsyncSession, student_id: int, graph: KnowledgeGraph, max_items: int = 10
) -> list[dict]:
    """Đi từ gap gốc sâu nhất lên qua dependents_of, lấy câu hỏi theo skill, tăng dần độ khó."""
    mastery = await get_mastery_snapshot(session, student_id, graph)
    root_gaps = find_root_gaps(graph, mastery)

    ordered_skill_codes: list[str] = []
    seen = set()

    def add_skill_chain(code: str) -> None:
        if code in seen:
            return
        seen.add(code)
        ordered_skill_codes.append(code)
        for dep in graph.dependents_of(code):
            if mastery[dep].p_mastery < 0.6:
                add_skill_chain(dep)

    for root in root_gaps:
        add_skill_chain(root)

    if not ordered_skill_codes:
        return []

    skill_rows = (await session.execute(select(Skill))).scalars().all()
    skill_id_by_code = {s.code: s.id for s in skill_rows}
    skill_ids = [skill_id_by_code[c] for c in ordered_skill_codes if c in skill_id_by_code]

    questions = (
        await session.execute(
            select(Question, Skill.code)
            .join(Skill, Skill.id == Question.skill_id)
            .where(Question.skill_id.in_(skill_ids))
            .order_by(Question.difficulty.asc())
        )
    ).all()

    by_skill: dict[str, list] = {}
    for q, code in questions:
        by_skill.setdefault(code, []).append(q)

    path = []
    for code in ordered_skill_codes:
        for q in by_skill.get(code, []):
            path.append(
                {
                    "question_id": q.id,
                    "skill_code": code,
                    "skill_name": graph.skill_name(code),
                    "content": q.content,
                    "question_type": q.question_type,
                    "options": q.options,
                    "difficulty": q.difficulty,
                }
            )
            if len(path) >= max_items:
                return path
    return path

"""Tool generate_practice_path — sinh lộ trình luyện tập cá nhân hóa.

Từ danh sách gap (từ diagnose_gap), chọn câu hỏi từ Question Bank,
sắp xếp theo thứ tự: gap sâu nhất trước, độ khó tăng dần.
"""
from __future__ import annotations

from ai.bkt_engine import BKTEngine
from ai.knowledge_graph import KnowledgeGraph
from tools.base import Tool
from tools.question_bank import QuestionBank

_engine: BKTEngine | None = None
_kg: KnowledgeGraph | None = None
_bank: QuestionBank | None = None


def set_dependencies(
    engine: BKTEngine, kg: KnowledgeGraph, bank: QuestionBank
) -> None:
    global _engine, _kg, _bank
    _engine = engine
    _kg = kg
    _bank = bank


def _generate_practice_path(student_id: str, gaps: list[dict]) -> str:
    if _engine is None or _kg is None or _bank is None:
        return "Lỗi: Hệ thống chưa được khởi tạo đầy đủ."

    if not gaps:
        return "Không có lỗ hổng nào cần luyện tập. Em đã nắm vững các kỹ năng."

    sorted_gaps = sorted(gaps, key=lambda g: g.get("gap_depth", 0), reverse=True)

    path: list[dict] = []
    fallback_used: list[str] = []

    for gap in sorted_gaps:
        skill_id = gap.get("skill_id", "")
        mastery = gap.get("mastery_prob", 0.0)

        if mastery < 0.2:
            difficulty = 1
        elif mastery < 0.4:
            difficulty = 2
        else:
            difficulty = 3

        questions = _bank.get_by_skill(skill_id, difficulty)
        if not questions:
            questions = _bank.get_by_skill(skill_id)

        if not questions and _kg:
            prereqs = _kg.get_prerequisites(skill_id)
            for pre in prereqs:
                questions = _bank.get_by_skill(pre.id)
                if questions:
                    fallback_used.append(skill_id)
                    break

        if not questions:
            continue

        for q in questions[:3]:
            path.append({
                "question_id": q.id,
                "skill_id": q.skill_id,
                "skill_name": _kg.get_skill(q.skill_id).name_vi if _kg else q.skill_id,
                "difficulty": q.difficulty,
                "content": q.content,
                "options": list(q.options),
            })

    if not path:
        return (
            "Không tìm thấy câu hỏi phù hợp trong ngân hàng. "
            "Vui lòng bổ sung câu hỏi cho các kỹ năng bị hổng."
        )

    lines = ["**Lộ trình luyện tập cá nhân hóa:**\n"]

    current_skill = None
    step = 0
    for item in path:
        if item["skill_id"] != current_skill:
            current_skill = item["skill_id"]
            step += 1
            lines.append(f"**Bước {step}: Luyện '{item['skill_name']}'** (độ khó {item['difficulty']})")

        lines.append(f"  - [{item['question_id']}] {item['content']}")
        for i, opt in enumerate(item["options"]):
            lines.append(f"    {chr(65+i)}. {opt}")
        lines.append("")

    if fallback_used:
        lines.append(
            f"\n*Lưu ý: Một số kỹ năng ({', '.join(fallback_used)}) "
            f"không có câu hỏi trực tiếp → hệ thống gợi ý câu hỏi "
            f"từ kỹ năng tiên quyết.*"
        )

    lines.append(f"\n**Tổng cộng:** {len(path)} câu hỏi, "
                 f"bắt đầu từ lỗ hổng sâu nhất, độ khó tăng dần.")

    return "\n".join(lines)


generate_practice_path_tool = Tool(
    name="generate_practice_path",
    description=(
        "Sinh lộ trình luyện tập cá nhân hóa từ danh sách lỗ hổng. "
        "Sắp xếp theo thứ tự: gap sâu nhất trước, độ khó tăng dần. "
        "Fallback: nếu skill không có câu hỏi → dùng câu hỏi skill tiên quyết."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "ID học sinh",
            },
            "gaps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill_id": {"type": "string"},
                        "gap_depth": {"type": "integer"},
                        "mastery_prob": {"type": "number"},
                    },
                    "required": ["skill_id"],
                },
                "description": "Danh sách gap từ diagnose_gap",
            },
        },
        "required": ["student_id", "gaps"],
    },
    func=_generate_practice_path,
)

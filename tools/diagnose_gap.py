"""Tool diagnose_gap — chẩn đoán root cause lỗ hổng kiến thức.

Gọi BKTEngine.diagnose_root_cause() để suy ngược qua Knowledge Graph.
Output: sorted gap list + explanation + recommended action.
"""
from __future__ import annotations

from ai.bkt_engine import BKTEngine
from tools.base import Tool

_engine: BKTEngine | None = None


def set_engine(engine: BKTEngine) -> None:
    global _engine
    _engine = engine


def _diagnose_gap(student_id: str, answers: list[dict]) -> str:
    if _engine is None:
        return "Lỗi: BKT Engine chưa được khởi tạo."

    if not answers:
        return "Chưa đủ dữ liệu để chẩn đoán. Vui lòng làm bài kiểm tra trước."

    wrong_skills: set[str] = set()
    for ans in answers:
        skill_id = ans.get("skill_id")
        correct = ans.get("correct")
        if skill_id is None or correct is None:
            continue
        _engine.update(student_id, skill_id, correct)
        if not correct:
            wrong_skills.add(skill_id)

    if not wrong_skills:
        return "Chúc mừng! Em trả lời đúng tất cả các câu hỏi. Không phát hiện lỗ hổng."

    all_gaps = []
    for skill_id in wrong_skills:
        gaps = _engine.diagnose_root_cause(student_id, skill_id)
        all_gaps.extend(gaps)

    seen: set[str] = set()
    unique_gaps = []
    for g in all_gaps:
        if g.skill_id not in seen:
            seen.add(g.skill_id)
            unique_gaps.append(g)

    unique_gaps.sort(key=lambda g: g.gap_depth, reverse=True)

    if not unique_gaps:
        return (
            "Đã phân tích xong. Em chưa nắm vững một số kỹ năng, "
            "nhưng hệ thống chưa xác định được nguyên nhân gốc cụ thể. "
            "Vui lòng thử lại với bài kiểm tra chi tiết hơn."
        )

    lines = ["**Kết quả chẩn đoán lỗ hổng kiến thức:**\n"]
    for i, gap in enumerate(unique_gaps, 1):
        lines.append(f"{i}. **{gap.skill_name}** (lớp {gap.grade})")
        lines.append(f"   - Mức nắm vững: {gap.mastery_prob * 100:.0f}%")
        lines.append(f"   - Độ sâu lỗ hổng: cấp {gap.gap_depth}")
        lines.append(f"   - {gap.explanation}")
        lines.append(f"   - Gợi ý: {gap.recommended_action}")
        lines.append("")

    deepest = unique_gaps[0]
    lines.append(f"**Ưu tiên:** {deepest.recommended_action}")

    return "\n".join(lines)


diagnose_gap_tool = Tool(
    name="diagnose_gap",
    description=(
        "Chẩn đoán nguyên nhân gốc lỗ hổng kiến thức của học sinh. "
        "Nhận danh sách câu trả lời (skill_id + đúng/sai), gọi BKT Engine "
        "suy ngược qua đồ thị tiên quyết, trả về danh sách gap đã xếp hạng "
        "kèm giải thích và gợi ý hành động."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "ID học sinh",
            },
            "answers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "skill_id": {"type": "string"},
                        "correct": {"type": "boolean"},
                    },
                    "required": ["skill_id", "correct"],
                },
                "description": "Danh sách câu trả lời",
            },
        },
        "required": ["student_id", "answers"],
    },
    func=_diagnose_gap,
)

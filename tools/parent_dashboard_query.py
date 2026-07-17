"""Tool parent_dashboard_query — bảng theo dõi tiến độ cho phụ huynh.

Input: student_id, parent_id → tiến độ theo thời gian, gợi ý tại nhà.
Access control: verify parent_id có quyền với student_id.
"""
from __future__ import annotations

from ai.bkt_engine import BKTEngine, MASTERY_THRESHOLD
from ai.knowledge_graph import KnowledgeGraph
from tools.base import Tool

_engine: BKTEngine | None = None
_kg: KnowledgeGraph | None = None
_parent_student_map: dict[str, list[str]] = {}


def set_dependencies(
    engine: BKTEngine, kg: KnowledgeGraph, parent_student_map: dict[str, list[str]]
) -> None:
    global _engine, _kg, _parent_student_map
    _engine = engine
    _kg = kg
    _parent_student_map = parent_student_map


def _parent_dashboard_query(student_id: str, parent_id: str) -> str:
    if _engine is None or _kg is None:
        return "Lỗi: Hệ thống chưa được khởi tạo."

    children = _parent_student_map.get(parent_id, [])
    if student_id not in children:
        return (
            f"Lỗi quyền truy cập: Phụ huynh '{parent_id}' "
            f"không có quyền xem dữ liệu của học sinh '{student_id}'."
        )

    mastery_map = _engine.get_all_mastery(student_id)
    history = _engine.get_student_history(student_id)

    if not history:
        return (
            f"Học sinh **{student_id}** chưa có dữ liệu học tập. "
            f"Vui lòng cho con làm bài kiểm tra chẩn đoán trước."
        )

    mastered = []
    struggling = []
    improving = []

    for skill_id, mastery in mastery_map.items():
        try:
            skill = _kg.get_skill(skill_id)
            name = skill.name_vi
            grade = skill.grade
        except Exception:
            name = skill_id
            grade = 0

        info = {
            "skill_id": skill_id,
            "skill_name": name,
            "grade": grade,
            "mastery": round(mastery, 4),
            "mastery_pct": round(mastery * 100),
        }

        if mastery >= 0.7:
            mastered.append(info)
        elif mastery < MASTERY_THRESHOLD:
            skill_history = [h for h in history if h["skill_id"] == skill_id]
            if len(skill_history) >= 2:
                first = skill_history[0]["mastery_before"]
                last = skill_history[-1]["mastery_after"]
                if last > first:
                    info["trending"] = "up"
                    improving.append(info)
                else:
                    info["trending"] = "down"
                    struggling.append(info)
            else:
                info["trending"] = "new"
                struggling.append(info)

    lines = [f"**Tiến độ học tập — {student_id}**\n"]

    total_skills = len(mastery_map)
    mastered_count = len(mastered)
    lines.append(f"- **Tổng kỹ năng theo dõi:** {total_skills}")
    lines.append(f"- **Đã nắm vững (>=70%):** {mastered_count}")
    lines.append(f"- **Cần hỗ trợ (<50%):** {len(struggling)}")
    lines.append(f"- **Đang cải thiện:** {len(improving)}\n")

    if struggling:
        lines.append("**Các kỹ năng cần hỗ trợ:**")
        for s in sorted(struggling, key=lambda x: x["mastery"])[:5]:
            lines.append(
                f"  - {s['skill_name']} (lớp {s['grade']}): "
                f"{s['mastery_pct']}%"
            )
        lines.append("")

    if improving:
        lines.append("**Các kỹ năng đang cải thiện:**")
        for s in improving[:5]:
            lines.append(
                f"  - {s['skill_name']} (lớp {s['grade']}): "
                f"{s['mastery_pct']}% ↑"
            )
        lines.append("")

    if mastered:
        lines.append("**Các kỹ năng đã nắm vững:**")
        for s in mastered[:5]:
            lines.append(f"  - {s['skill_name']}: {s['mastery_pct']}% ✅")
        lines.append("")

    lines.append("**Gợi ý cho phụ huynh:**")
    if struggling:
        weakest = sorted(struggling, key=lambda x: x["mastery"])[0]
        lines.append(
            f"  - Mỗi ngày 15 phút ôn cùng con bài về "
            f"'{weakest['skill_name']}' (lớp {weakest['grade']})"
        )
        lines.append(f"  - Không so sánh với bạn khác, hãy khen con khi tiến bộ")
    else:
        lines.append("  - Con đang học tốt! Tiếp tục động viên con giữ vững phong độ.")

    if history:
        recent = history[-5:]
        correct_count = sum(1 for h in recent if h["correct"])
        lines.append(
            f"\n  - 5 câu gần nhất: đúng {correct_count}/5"
        )

    return "\n".join(lines)


parent_dashboard_tool = Tool(
    name="parent_dashboard_query",
    description=(
        "Bảng theo dõi tiến độ cho phụ huynh: tiến độ theo thời gian, "
        "gợi ý hành động tại nhà. Access control: verify parent_id có quyền."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_id": {
                "type": "string",
                "description": "ID học sinh cần xem",
            },
            "parent_id": {
                "type": "string",
                "description": "ID phụ huynh (để xác thực quyền)",
            },
        },
        "required": ["student_id", "parent_id"],
    },
    func=_parent_dashboard_query,
)

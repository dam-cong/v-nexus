"""Tool teacher_dashboard_query — tổng hợp gap theo lớp cho giáo viên.

Input: class_id → heatmap skill, nhóm học sinh, xếp ưu tiên, cảnh báo.
"""
from __future__ import annotations

from ai.bkt_engine import BKTEngine, MASTERY_THRESHOLD
from ai.knowledge_graph import KnowledgeGraph
from tools.base import Tool

_engine: BKTEngine | None = None
_kg: KnowledgeGraph | None = None
_class_students: dict[str, list[str]] = {}


def set_dependencies(
    engine: BKTEngine, kg: KnowledgeGraph, class_students: dict[str, list[str]]
) -> None:
    global _engine, _kg, _class_students
    _engine = engine
    _kg = kg
    _class_students = class_students


def _teacher_dashboard_query(class_id: str) -> str:
    if _engine is None or _kg is None:
        return "Lỗi: Hệ thống chưa được khởi tạo."

    students = _class_students.get(class_id, [])
    if not students:
        return f"Không tìm thấy học sinh nào trong lớp '{class_id}'."

    skill_gap_counts: dict[str, int] = {}
    student_gaps: dict[str, list[dict]] = {}
    student_priority: dict[str, float] = {}

    for sid in students:
        mastery_map = _engine.get_all_mastery(sid)
        gaps = []
        total_depth = 0
        for skill_id, mastery in mastery_map.items():
            if mastery < MASTERY_THRESHOLD:
                skill_gap_counts[skill_id] = skill_gap_counts.get(skill_id, 0) + 1
                try:
                    skill = _kg.get_skill(skill_id)
                    gaps.append({
                        "skill_id": skill_id,
                        "skill_name": skill.name_vi,
                        "mastery": round(mastery, 4),
                        "grade": skill.grade,
                    })
                except Exception:
                    gaps.append({
                        "skill_id": skill_id,
                        "skill_name": skill_id,
                        "mastery": round(mastery, 4),
                        "grade": 0,
                    })
                total_depth += (1.0 - mastery)

        student_gaps[sid] = gaps
        student_priority[sid] = total_depth

    total = len(students)
    heatmap: list[dict] = []
    for skill_id, count in sorted(
        skill_gap_counts.items(), key=lambda x: x[1], reverse=True
    ):
        pct = round(count / total * 100)
        try:
            skill = _kg.get_skill(skill_id)
            name = skill.name_vi
            grade = skill.grade
        except Exception:
            name = skill_id
            grade = 0
        heatmap.append({
            "skill_id": skill_id,
            "skill_name": name,
            "grade": grade,
            "gap_count": count,
            "gap_pct": pct,
            "alert": pct >= 50,
        })

    alert_skills = [h for h in heatmap if h["alert"]]

    priority_list = sorted(
        student_priority.items(), key=lambda x: x[1], reverse=True
    )

    grouped: dict[str, list[str]] = {}
    for sid, gaps in student_gaps.items():
        for g in gaps:
            key = g["skill_id"]
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(sid)

    lines = [f"**Dashboard Giáo viên — Lớp {class_id}**\n"]
    lines.append(f"- **Tổng học sinh:** {total}")
    lines.append(f"- **Số kỹ năng có gap:** {len(skill_gap_counts)}\n")

    if alert_skills:
        lines.append("**CẢNH BÁO: Lỗ hổng diện rộng** (>=50% học sinh hổng):")
        for h in alert_skills[:5]:
            lines.append(f"  - {h['skill_name']} ({h['grade']}): {h['gap_count']}/{total} ({h['gap_pct']}%)")
        lines.append("")

    lines.append("**Heatmap lỗ hổng theo kỹ năng:**")
    for h in heatmap[:10]:
        bar = "█" * (h["gap_pct"] // 10) + "░" * (10 - h["gap_pct"] // 10)
        lines.append(f"  {h['skill_name']:<35} {bar} {h['gap_pct']}% ({h['gap_count']}/{total})")
    lines.append("")

    lines.append("**Học sinh cần ưu tiên giúp đỡ trước:**")
    for sid, score in priority_list[:10]:
        gap_count = len(student_gaps[sid])
        if gap_count == 0:
            status = "✅ OK"
        else:
            status = f"⚠️ {gap_count} gap(s)"
        lines.append(f"  - {sid}: {status} (mức ưu tiên: {score:.2f})")
    lines.append("")

    if grouped:
        lines.append("**Nhóm học sinh theo lỗ hổng:**")
        top_skills = sorted(grouped.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        for skill_id, sids in top_skills:
            try:
                name = _kg.get_skill(skill_id).name_vi
            except Exception:
                name = skill_id
            lines.append(f"  - {name}: {', '.join(sids[:8])}")
            if len(sids) > 8:
                lines.append(f"    ... và {len(sids) - 8} học sinh khác")
        lines.append("")

    return "\n".join(lines)


teacher_dashboard_tool = Tool(
    name="teacher_dashboard_query",
    description=(
        "Tổ hợp gap theo lớp cho giáo viên: heatmap kỹ năng, "
        "nhóm học sinh cùng gap, xếp hạng ưu tiên, cảnh báo lỗ hổng diện rộng."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "class_id": {
                "type": "string",
                "description": "ID lớp học",
            },
        },
        "required": ["class_id"],
    },
    func=_teacher_dashboard_query,
)

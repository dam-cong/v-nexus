"""Tool 3: Tổng hợp cho giáo viên — biểu đồ nhiệt lỗ hổng của một lớp học.

Nhận dữ liệu tổng hợp tình trạng lỗ hổng của học sinh trong lớp, nhóm theo kỹ năng,
cảnh báo kỹ năng vượt ngưỡng. Chỉ trả dữ liệu của đúng lớp được yêu cầu (docs §5.3).
"""
import json

from agent.llm_client import create_message_fpt
from tools.base import Tool

SYSTEM_PROMPT = (
    "Bạn là trợ lý giáo viên AI của V-Nexus Tutor. Từ dữ liệu lỗ hổng của MỘT lớp học, "
    "hãy tóm tắt cho giáo viên: kỹ năng nào nhiều học sinh hổng nhất, nhóm học sinh cần "
    "can thiệp, và mức độ ưu tiên. Chỉ dùng dữ liệu được cung cấp, dùng thuật ngữ chuyên môn."
)


def teacher_class_summary(class_id: str, class_name: str = "", skill_gap_counts: dict = None,
                          students: list = None, alert_threshold: float = 0.4) -> str:
    """Tổng hợp lỗ hổng lớp. skill_gap_counts: {skill_name: số_học_sinh_hổng}.
    students: [{name, weak_skills:[...]}]. Trả về văn bản tóm tắt."""
    skill_gap_counts = skill_gap_counts or {}
    students = students or []

    alerts = [
        f"{skill}: {count} học sinh"
        for skill, count in skill_gap_counts.items()
        if count and count / max(1, len(students)) >= alert_threshold
    ]

    user_msg = (
        f"Lớp: {class_name or class_id} (mã {class_id}). Tổng số học sinh: {len(students)}.\n"
        f"Số học sinh hổng từng kỹ năng: {json.dumps(skill_gap_counts, ensure_ascii=False)}.\n"
        f"Chi tiết học sinh (tên - kỹ năng yếu): "
        + "; ".join(f"{s.get('name')}: {', '.join(s.get('weak_skills', []))}" for s in students)
        + f"\nCảnh báo vượt ngưỡng ({int(alert_threshold*100)}% lớp): "
        + (", ".join(alerts) if alerts else "không có.")
    )

    try:
        resp = create_message_fpt(
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        return resp.get("text") or "(Chưa sinh được tóm tắt.)"
    except Exception as e:
        return f"[Tóm tắt tạm thời - LLM chưa khả dụng: {e}]\nCảnh báo: " + (", ".join(alerts) or "không có.")


teacher_summary_tool = Tool(
    name="teacher_class_summary",
    description=(
        "Tổng hợp tình trạng lỗ hổng của MỘT lớp học thành tóm tắt cho giáo viên: biểu đồ "
        "nhiệt theo kỹ năng, nhóm học sinh cùng vấn đề, xếp hạng ưu tiên can thiệp, cảnh báo "
        "kỹ năng vượt ngưỡng. Chỉ trả dữ liệu lớp được yêu cầu."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "class_id": {"type": "string", "description": "Mã lớp học."},
            "class_name": {"type": "string", "description": "Tên lớp."},
            "skill_gap_counts": {"type": "object", "description": "{tên_kỹ_năng: số_học_sinh_hổng}."},
            "students": {"type": "array", "description": "[{name, weak_skills:[...]}]."},
            "alert_threshold": {"type": "number", "description": "Ngưỡng tỷ lệ cảnh báo (mặc định 0.4)."},
        },
        "required": ["class_id"],
    },
    func=teacher_class_summary,
)

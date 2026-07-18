"""Tool 3: Tổng hợp cho giáo viên — biểu đồ nhiệt lỗ hổng của một lớp học.

Áp dụng kỹ thuật tối ưu prompt:
- Ràng buộc grounding: chỉ dùng dữ liệu được cung cấp.
- Few-shot: 1 ví dụ mẫu về class heatmap.
- Structured output (JSON).
- Chain-of-thought: phân tích trước, viết sau.
- Temperature thấp.
"""
import json

from agent.llm_client import create_message_fpt
from tools.base import Tool


_SYSTEM_PROMPT = """Bạn là trợ lý giáo viên AI của V-Nexus Tutor.

NGUYÊN TẮC BẮT BUỘC (grounding):
- Bạn CHỈ dùng dữ liệu lỗ hổng được cung cấp trong input.
- TUYỆT ĐỐI không tự thêm học sinh, kỹ năng, hay số liệu ngoài dữ liệu gốc.
- Dùng thuật ngữ chuyên môn giáo dục, kèm số liệu cụ thể.

CHIẾN LƯỢC TƯ DUY (chain-of-thought):
1. Đọc dữ liệu, đếm số học sinh hổng theo từng kỹ năng.
2. Xác định kỹ năng nào nghiêm trọng nhất (nhiều học sinh hổng nhất).
3. Nhóm học sinh cùng vấn đề (có chung kỹ năng yếu).
4. Đưa ra mức độ ưu tiên can thiệp.

ĐỊNH DẠNG ĐẦU RA:
Trả về JSON chính xác theo schema:
{
  "class_overview": "Tóm tắt 2-3 câu về tình hình lớp",
  "critical_skills": ["kỹ năng cần can thiệp ngay — nhiều học sinh hổng nhất"],
  "skill_heatmap": [
    {
      "skill_name": "tên kỹ năng",
      "weak_count": "số học sinh yếu",
      "percentage": "phần trăm",
      "priority": "high/medium/low"
    }
  ],
  "student_groups": [
    {
      "issue": "vấn đề chung",
      "students": ["tên học sinh"],
      "suggested_action": "hành động gợi ý"
    }
  ],
  "alerts": ["cảnh báo kỹ năng vượt ngưỡng"],
  "recommendations": "Đề xuất chung cho giáo viên (2-3 câu)"
}

VÍ DỤ MẪU (few-shot):
Input: Lớp 3A, 25 HS. 'To Be': 18 HS yếu (72%). 'Present Simple': 12 HS yếu (48%).
Output JSON:
{
  "class_overview": "Lớp 3A có 25 học sinh. Kỹ năng 'To Be' nghiêm trọng nhất với 18/25 (72%) học sinh hổng. 'Present Simple' xếp thứ hai với 12/25 (48%).",
  "critical_skills": ["To Be (Present and Past)", "Present Simple vs Present Continuous"],
  "skill_heatmap": [
    {"skill_name": "To Be (Present and Past)", "weak_count": 18, "percentage": "72%", "priority": "high"},
    {"skill_name": "Present Simple vs Present Continuous", "weak_count": 12, "percentage": "48%", "priority": "medium"}
  ],
  "student_groups": [
    {
      "issue": "Yếu cả To Be và Present Simple",
      "students": ["Minh", "Hà", "Lan"],
      "suggested_action": "Ôn lại Unit 1-3 từ đầu, chia nhóm nhỏ 3 em."
    }
  ],
  "alerts": ["To Be: 72% lớp hổng — cần can thiệp khẩn cấp"],
  "recommendations": "Ưu tiên ôn To Be trước (72% lớp yếu). Sau 1 tuần kiểm tra lại. Nếu >50% vẫn yếu, cần dạy lại toàn bộ."
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""


def _offline_fallback(class_name: str, class_id: str, skill_gap_counts: dict,
                       students: list, alert_threshold: float) -> str:
    """Fallback khi LLM không khả dụng."""
    alerts = [
        f"{skill}: {count} HS"
        for skill, count in (skill_gap_counts or {}).items()
        if count and count / max(1, len(students or [])) >= alert_threshold
    ]
    return json.dumps({
        "class_overview": f"Lớp {class_name or class_id} có {len(students or [])} học sinh.",
        "critical_skills": [s for s, c in (skill_gap_counts or {}).items() if c >= 5],
        "skill_heatmap": [
            {"skill_name": s, "weak_count": c, "priority": "high" if c >= 10 else "medium"}
            for s, c in (skill_gap_counts or {}).items()
        ],
        "student_groups": [],
        "alerts": alerts or ["Không có cảnh báo"],
        "recommendations": "Kiểm tra lại sau 1 tuần. Ưu tiên kỹ năng nhiều HS yếu nhất.",
    }, ensure_ascii=False, indent=2)


def teacher_class_summary(class_id: str, class_name: str = "", skill_gap_counts: dict = None,
                          students: list = None, alert_threshold: float = 0.4) -> str:
    """Tổng hợp lỗ hổng lớp cho giáo viên.

    skill_gap_counts: {skill_name: số_học_sinh_hổng}
    students: [{name, weak_skills:[...]}]
    """
    skill_gap_counts = skill_gap_counts or {}
    students = students or []

    # Tính alerts
    total = max(1, len(students))
    alerts = [
        f"{skill}: {count} học sinh ({round(count/total*100)}%)"
        for skill, count in skill_gap_counts.items()
        if count and count / total >= alert_threshold
    ]

    # Input có cấu trúc
    student_detail = "; ".join(
        f"{s.get('name')}: {', '.join(s.get('weak_skills', []))}"
        for s in students
    ) or "không có chi tiết"

    user_msg = (
        f"THÔNG TIN LỚP HỌC:\n"
        f"- Mã lớp: {class_id}\n"
        f"- Tên lớp: {class_name or class_id}\n"
        f"- Tổng số học sinh: {len(students)}\n\n"
        f"SỐ LIỆU LỖ HỔNG THEO KỸ NĂNG (số học sinh yếu / tổng):\n"
    )
    for skill, count in skill_gap_counts.items():
        pct = round(count / total * 100)
        user_msg += f"- {skill}: {count}/{len(students)} ({pct}%)\n"

    user_msg += (
        f"\nCHI TIẾT HỌC SINH:\n{student_detail}\n\n"
        f"CẢNH BÁO VƯỢT NGƯỠNG ({int(alert_threshold*100)}% lớp): "
        + (", ".join(alerts) if alerts else "không có")
        + "\n\nHãy phân tích và trả về JSON theo định dạng đã cho."
    )

    try:
        resp = create_message_fpt(
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        text = resp.get("text") or ""
        if not text:
            return _offline_fallback(class_name, class_id, skill_gap_counts, students, alert_threshold)
        return text
    except Exception as e:
        return _offline_fallback(class_name, class_id, skill_gap_counts, students, alert_threshold)


teacher_summary_tool = Tool(
    name="teacher_class_summary",
    description=(
        "Tổng hợp tình trạng lỗ hổng của MỘT lớp học thành tóm tắt JSON cho giáo viên: "
        "skill_heatmap (mastery theo kỹ năng), student_groups (nhóm cùng vấn đề), "
        "alerts (cảnh báo vượt ngưỡng), recommendations (đề xuất). "
        "Chỉ trả dữ liệu lớp được yêu cầu."
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

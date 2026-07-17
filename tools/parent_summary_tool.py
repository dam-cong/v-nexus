"""Tool 4: Tổng hợp cho phụ huynh — tiến độ học tập + gợi ý tại nhà.

Bắt buộc kiểm tra quyền: chỉ phụ huynh ĐÚNG của học sinh đó mới xem được. Nếu không khớp,
trả thông báo từ chối rõ ràng (không trả rỗng gây hiểu lầm) (docs §5.4).
"""
from agent.llm_client import create_message_fpt
from tools.base import Tool

SYSTEM_PROMPT = (
    "Bạn là trợ lý AI của V-Nexus Tutor, viết cho PHỤ HUYNH. Dùng ngôn ngữ đơn giản, phi "
    "kỹ thuật, khích lệ. Đưa ra gợi ý hành động cụ thể tại nhà (ví dụ: dành 15 phút/ngày ôn "
    "một kỹ năng). Chỉ dùng dữ liệu tiến độ được cung cấp."
)


def parent_student_summary(student_name: str, parent_name: str, authorized: bool = False,
                            progress: list = None, weak_skills: list = None) -> str:
    """Tổng hợp tiến độ cho phụ huynh. authorized = phụ huynh có đúng quyền không."""
    if not authorized:
        return (
            "Truy cập bị từ chối: bạn không phải là phụ huynh/người giám hộ hợp lệ của học "
            f"sinh {student_name}. Vui lòng liên hệ nhà trường để được cấp quyền xem báo cáo."
        )

    progress = progress or []
    weak_skills = weak_skills or []

    user_msg = (
        f"Phụ huynh: {parent_name}. Học sinh: {student_name}.\n"
        f"Tiến độ theo thời gian: " + "; ".join(progress) + ".\n"
        f"Kỹ năng cần củng cố: " + (", ".join(weak_skills) if weak_skills else "không có.")
    )

    try:
        resp = create_message_fpt(
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        return resp.get("text") or "(Chưa sinh được báo cáo.)"
    except Exception as e:
        return f"[Báo cáo tạm thời - LLM chưa khả dụng: {e}]\nKỹ năng cần ôn: " + (
            ", ".join(weak_skills) if weak_skills else "không có."
        )


parent_summary_tool = Tool(
    name="parent_student_summary",
    description=(
        "Trả báo cáo tiến độ học tập và gợi ý ôn tập tại nhà cho PHỤ HUYNH. Bắt buộc kiểm "
        "tra quyền: chỉ phụ huynh đúng của học sinh mới xem được; nếu sai phải trả thông báo "
        "từ chối rõ ràng, không trả rỗng."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_name": {"type": "string", "description": "Tên học sinh."},
            "parent_name": {"type": "string", "description": "Tên phụ huynh."},
            "authorized": {"type": "boolean", "description": "Phụ huynh có đúng quyền xem không."},
            "progress": {"type": "array", "description": "Danh sách tiến độ theo thời gian (text)."},
            "weak_skills": {"type": "array", "description": "Danh sách kỹ năng cần củng cố."},
        },
        "required": ["student_name", "parent_name", "authorized"],
    },
    func=parent_student_summary,
)

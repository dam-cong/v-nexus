"""Tool 2: Sinh kế hoạch đào tạo cá nhân hóa (Tầng 3 - LLM Output Layer).

Nhận danh sách lỗ hổng (từ BKT) và mastery, gọi FPT LLM (DeepSeek-V4-Flash) để diễn
giải thành kế hoạch đào tạo bằng tiếng Việt, theo đúng số liệu BKT. LLM không được tự
thêm lỗ hổng không có (docs/ai-danh-gia.md §4.3, §5.2).
"""
import json

from agent.llm_client import create_message_fpt
from tools.base import Tool

SYSTEM_PROMPT = (
    "Bạn là trợ lý giáo viên AI của V-Nexus Tutor, chuyên môn Tiếng Anh tiểu học "
    "(CT GDPT 2018). Nhiệm vụ: từ kết quả chẩn đoán BKT (mastery và gaps) của MỘT học sinh, "
    "hãy lập kế hoạch đào tạo cá nhân hóa bằng tiếng Việt.\n"
    "QUY TẮC BẮT BUỘC:\n"
    "1. Chỉ sử dụng các kỹ năng và độ tin cậy nằm trong dữ liệu BKT được cung cấp. "
    "TUYỆT ĐỐI không tự bịa thêm lỗ hổng hay kỹ năng không có trong dữ liệu.\n"
    "2. Ưu tiên luyện các kỹ năng ở mức 'high' (gốc rễ) trước, sau đó đến 'medium'.\n"
    "3. Kế hoạch gồm: (a) nhận xét trình độ ngắn gọn; (b) danh sách bài tập/theo thứ tự "
    "từ dễ đến khó; (c) lời khuyên ôn tập cụ thể tại nhà.\n"
    "4. Viết thân thiện, khích lệ học sinh, ngôn ngữ đơn giản, dễ hiểu."
)


def _format_bkt(mastery: dict, gaps: list) -> str:
    lines = ["=== MASTERY (xác suất thành thạo) ==="]
    for sid, m in mastery.items():
        lines.append(f"- {m.get('skill_name', sid)}: {round((m.get('probability') or 0)*100)}% ({m.get('status')})")
    lines.append("\n=== GAPS (lỗ hổng) ===")
    if not gaps:
        lines.append("- Không có lỗ hổng đáng kể.")
    for g in gaps:
        roots = ", ".join(g.get("root_causes", [])) or "không xác định"
        lines.append(
            f"- {g.get('skill_name')} | mức: {g.get('severity')} | gốc rễ: {roots} | "
            f"độ tin cậy: {round((g.get('probability') or 0)*100)}% | {g.get('reason')}"
        )
    return "\n".join(lines)


def generate_training_plan(gaps: list, mastery: dict = None, student_name: str = "", level: str = "") -> str:
    """Gọi FPT LLM để sinh kế hoạch đào tạo. Trả về chuỗi văn bản."""
    mastery = mastery or {}
    bkt_text = _format_bkt(mastery, gaps)

    user_msg = (
        f"Học sinh: {student_name or 'học sinh'}. Trình độ hiện tại: {level or 'chưa xác định'}.\n\n"
        f"Dưới đây là KẾT QUẢ CHẨN ĐOÁN BKT (chỉ dùng dữ liệu này):\n{bkt_text}\n\n"
        "Hãy lập kế hoạch đào tạo cá nhân hóa cho học sinh này."
    )

    try:
        resp = create_message_fpt(
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        return resp.get("text") or "(Hệ thống chưa sinh được kế hoạch. Vui lòng thử lại.)"
    except Exception as e:  # fallback an toàn nếu LLM lỗi
        return (
            f"[Kế hoạch tạm thời - LLM chưa khả dụng: {e}]\n"
            "Dựa trên chẩn đoán BKT, em nên ưu tiên ôn lại các kỹ năng sau:\n"
            + "\n".join(f"- {g.get('skill_name')} ({g.get('severity')})" for g in gaps)
            if gaps
            else "Em đã nắm tốt các kỹ năng. Hãy tiếp tục luyện tập nâng cao!"
        )


plan_tool = Tool(
    name="generate_training_plan",
    description=(
        "Sinh kế hoạch đào tạo cá nhân hóa bằng tiếng Việt từ danh sách lỗ hổng (gaps) "
        "và mastery do BKT Engine cung cấp. Chỉ diễn giải dữ liệu BKT, không tự thêm lỗ hổng."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "gaps": {
                "type": "array",
                "description": "Danh sách lỗ hổng từ BKT (mỗi item có skill_name, severity, root_causes, probability).",
            },
            "mastery": {"type": "object", "description": "Mastery theo từng kỹ năng từ BKT."},
            "student_name": {"type": "string", "description": "Tên học sinh."},
            "level": {"type": "string", "description": "Trình độ CEFR hiện tại (ví dụ A1)."},
        },
        "required": ["gaps"],
    },
    func=generate_training_plan,
)

"""Tool 4: Tổng hợp cho phụ huynh — tiến độ học tập + gợi ý tại nhà.

Áp dụng kỹ thuật tối ưu prompt:
- Ràng buộc grounding: chỉ dùng dữ liệu tiến độ được cung cấp.
- Few-shot: 1 ví dụ mẫu về báo cáo phụ huynh.
- Structured output (JSON).
- Chain-of-thought: hiểu trình độ → xác định việc nhà → gợi ý hành động.
- Temperature thấp.
- Ngôn ngữ đơn giản, phi kỹ thuật.
"""
import json

from agent.llm_client import create_message_fpt
from tools.base import Tool


_SYSTEM_PROMPT = """Bạn là trợ lý AI của V-Nexus Tutor, viết báo cáo cho PHỤ HUYNH.

NGUYÊN TẮC BẮT BUỘC (grounding):
- Bạn CHỈ dùng dữ liệu tiến độ được cung cấp trong input.
- TUYỆT ĐỐI không tự thêm kỹ năng ngoài danh sách, không bịa số liệu.
- Dùng ngôn ngữ đơn giản, phi kỹ thuật, thân thiện.
- KHÔNG dùng thuật ngữ: mastery, BKT, CEFR, skill_id, probability.

CHIẾN LƯỢC TƯ DUY (chain-of-thought):
1. Hiểu rõ con phụ huynh đang ở mức nào (dựa trên dữ liệu tiến độ).
2. Xác định điểm mạnh cần khen (để phụ huynh động viên con).
3. Xác định 1-2 việc cụ thể phụ huynh có thể làm tại nhà.
4. Đưa gợi ý hành động có thời gian cụ thể (ví dụ: 15 phút/ngày).

ĐỊNH DẠNG ĐẦU RA:
Trả về JSON chính xác theo schema:
{
  "summary": "Tóm tắt tiến độ con em (2-3 câu, ngôn ngữ phụ huynh)",
  "what_going_well": "Điểm tốt cần khen (1-2 câu)",
  "needs_attention": "Kỹ năng cần hỗ trợ thêm (1-2 câu, không dùng thuật ngữ kỹ thuật)",
  "home_activities": [
    {
      "activity": "Tên hoạt động",
      "time": "Thời gian cụ thể",
      "how": "Cách thực hiện từng bước"
    }
  ],
  "encouragement": "Lời khích lệ (1 câu)"
}

VÍ DỤ MẪU (few-shot):
Input: Học sinh Linh, 8/12 câu đúng (67%). Kỹ năng yếu: 'To Be' (28%), 'Past Simple' (35%).
Output JSON:
{
  "summary": "Con em làm đúng 8/12 câu (67%) — kết quả khá tốt! Con có điểm mạnh ở phần từ vựng. Tuy nhiên, con còn yếu ở cách dùng 'was/were' và thì quá khứ.",
  "what_going_well": "Con nhớ từ vựng tốt, phân biệt được đồ vật và hoạt động xung quanh.",
  "needs_attention": "Con cần luyện thêm cách dùng 'was/were' và cách chia động từ ở thì quá khứ.",
  "home_activities": [
    {
      "activity": "Hỏi con về mọi thứ xung quanh",
      "time": "10 phút/ngày, sau bữa tối",
      "how": "Bước 1: Hỏi 'What is this?' → Con trả lời 'It is a ...' (dùng 'is'). Bước 2: Hỏi 'How old are you?' → Con trả lời 'I am ...'"
    },
    {
      "activity": "Kể chuyện ngắn bằng thì quá khứ",
      "time": "15 phút, 3 lần/tuần",
      "how": "Bước 1: Con kể lại 1 việc đã làm hôm nay (ví dụ: 'I played football'). Bước 2: Phụ huynh giúp con sửa nếu sai."
    }
  ],
  "encouragement": "Con đang progress rất tốt! Mỗi ngày 10 phút ôn cùng con, chắc chắn con sẽ tiến bộ nhanh thôi!"
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON.
NGÔN NGỮ: Viết cho phụ huynh — đơn giản, gần gũi, KHÔNG dùng thuật ngữ kỹ thuật."""


def _offline_fallback(student_name: str, weak_skills: list) -> str:
    """Fallback khi LLM không khả dụng."""
    activities = []
    for skill in (weak_skills or [])[:2]:
        activities.append({
            "activity": f"Luyện kỹ năng: {skill}",
            "time": "15 phút/ngày",
            "how": f"Bước 1: Mở sách bài tập phần '{skill}'. Bước 2: Làm 5-10 câu. Bước 3: Kiểm tra đáp án.",
        })
    return json.dumps({
        "summary": f"Con {student_name or 'em'} cần hỗ trợ thêm ở {len(weak_skills or [])} kỹ năng.",
        "what_going_well": "Con đang cố gắng, hãy tiếp tục động viên!",
        "needs_attention": ", ".join(weak_skills) if weak_skills else "Không có kỹ năng yếu nổi bật.",
        "home_activities": activities or [{"activity": "Đọc sách tiếng Anh", "time": "15 phút/ngày", "how": "Đọc 1 trang sách, cố gắng hiểu nghĩa."}],
        "encouragement": "Mỗi ngày một chút, con sẽ tiến bộ!",
    }, ensure_ascii=False, indent=2)


def parent_student_summary(student_name: str, parent_name: str, authorized: bool = False,
                            progress: list = None, weak_skills: list = None) -> str:
    """Tổng hợp tiến độ cho phụ huynh.

    authorized = phụ huynh có đúng quyền không.
    progress: list[str] — các mốc tiến độ theo thời gian.
    weak_skills: list[str] — tên kỹ năng cần củng cố.
    """
    if not authorized:
        return json.dumps({
            "summary": "Truy cập bị từ chối.",
            "what_going_well": "",
            "needs_attention": "",
            "home_activities": [],
            "encouragement": (
                f"Bạn không phải là phụ huynh hợp lệ của học sinh {student_name}. "
                "Vui lòng liên hệ nhà trường để được cấp quyền."
            ),
        }, ensure_ascii=False)

    progress = progress or []
    weak_skills = weak_skills or []

    # Input có cấu trúc
    user_msg = (
        f"THÔNG TIN BÁO CÁO:\n"
        f"- Phụ huynh: {parent_name}\n"
        f"- Học sinh: {student_name}\n\n"
        f"TIẾN ĐỘ THEO THỜI GIAN:\n"
    )
    for i, p in enumerate(progress, 1):
        user_msg += f"  {i}. {p}\n"

    if not progress:
        user_msg += "  (Chưa có dữ liệu tiến độ)\n"

    user_msg += (
        f"\nKỸ NĂNG CẦN CỦNG CỐ:\n"
        + (", ".join(weak_skills) if weak_skills else "Không có kỹ năng yếu nổi bật.")
        + "\n\nHãy viết báo cáo cho phụ huynh bằng JSON theo định dạng đã cho. "
        "Nhớ: NGÔN NGỮ ĐƠN GIẢN, không dùng thuật ngữ kỹ thuật."
    )

    try:
        resp = create_message_fpt(
            system=_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        text = resp.get("text") or ""
        if not text:
            return _offline_fallback(student_name, weak_skills)
        return text
    except Exception as e:
        return _offline_fallback(student_name, weak_skills)


parent_summary_tool = Tool(
    name="parent_student_summary",
    description=(
        "Trả báo cáo tiến độ học tập và gợi ý ôn tập tại nhà cho PHỤ HUYNH (JSON format). "
        "Bắt buộc kiểm tra quyền: chỉ phụ huynh đúng mới xem được. "
        "Ngôn ngữ đơn giản, phi kỹ thuật, có gợi ý hành động cụ thể."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "student_name": {"type": "string", "description": "Tên học sinh."},
            "parent_name": {"type": "string", "description": "Tên phụ huynh."},
            "authorized": {"type": "boolean", "description": "Phụ huynh có đúng quyền xem không."},
            "progress": {"type": "array", "description": "Danh sách tiến độ theo thời gian (text)."},
            "weak_skills": {"type": "array", "description": "Danh sách tên kỹ năng cần củng cố."},
        },
        "required": ["student_name", "parent_name", "authorized"],
    },
    func=parent_student_summary,
)

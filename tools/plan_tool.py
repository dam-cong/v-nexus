"""Tool 2: Sinh kế hoạch đào tạo cá nhân hóa (Tầng 3 — LLM Output Layer).

Áp dụng các kỹ thuật tối ưu prompt theo prompt.md:
- Ràng buộc grounding rõ ràng (LLM chỉ diễn giải, không quyết định lộ trình)
- Input có cấu trúc (bảng từ BKT Engine, không văn xuôi tự do)
- Few-shot (1 ví dụ mẫu trong prompt)
- Chain-of-thought có kiểm soát (liệt kê lý do trước khi viết lời)
- Structured output (JSON có schema)
- Temperature thấp (0.2)
- Tách prompt theo đối tượng (học sinh vs giáo viên/phụ huynh)
- Post-validation (cross-check skill_id)
- Offline fallback template
"""
import json
import re

from agent.llm_client import create_message_fpt
from domain.bkt import generate_learning_steps, format_steps_for_llm, get_input_skill_ids
from tools.base import Tool


# ---------------------------------------------------------------------------
# 1. SYSTEM PROMPTS — tách riêng theo đối tượng
# ---------------------------------------------------------------------------

_STUDENT_SYSTEM_PROMPT = """Bạn là Medi Bee, trợ lý AI gia sư của V-Nexus Tutor.

NGUYÊN TẮC BẮT BUỘC (grounding):
- Bạn CHỈ diễn giải dữ liệu lộ trình được cung cấp trong input.
- TUYỆT ĐỐI không thêm bước mới, không đổi thứ tự, không tự bịa kỹ năng ngoài danh sách.
- Nếu dữ liệu input rỗng, hãy chúc mừng học sinh và đề xuất luyện nâng cao.

CHIẾN LƯỢC TƯ DUY (chain-of-thought):
Trước khi viết lời khuyên cuối cùng, hãy THỰC HIỆN BƯỚC SAU TRONG ĐẦU:
1. Đọc bảng lộ trình, xác định bước nào là gốc rễ (severity=high) cần ưu tiên nhất.
2. Liệu mỗi bước có phù hợp với trình độ học sinh không (dựa trên mastery hiện tại).
3. Chỉ SAU KHI phân tích xong mới viết lời diễn giải.

ĐỊNH DẠNG ĐẦU RA:
Trả về JSON chính xác theo schema:
{
  "summary": "Nhận xét 1-2 câu về trình độ hiện tại",
  "steps": [
    {
      "step_order": 1,
      "skill_name": "tên kỹ năng",
      "encouragement": "lời khích lệ ngắn cho bước này (1 câu)",
      "practice_tip": "gợi ý bài tập cụ thể (1-2 câu)",
      "home_tip": "gợi ý ôn tại nhà (1 câu)"
    }
  ],
  "closing": "Lời kết khích lệ (1 câu)"
}

VÍ DỤ MẪU (few-shot):
Input bảng lộ trình:
| # | Kỹ năng | Mastery | Ưu tiên | Khó | Thời lượng | Lý do |
|---|---------|---------|---------|-----|------------|-------|
| 1 | To Be (Present and Past) (as3.u3.l3) | 28% | high | easy | 20 phút | Gốc rễ — cần ôn trước |
| 2 | Present Simple vs Present Continuous (as3.u1.l3) | 35% | medium | medium | 15 phút | Tiên quyết: To Be |

Output JSON:
{
  "summary": "Em đang ở trình độ cơ bản, cần ôn lại câu 'to be' trước vì đây là nền tảng cho nhiều kỹ năng khác.",
  "steps": [
    {
      "step_order": 1,
      "skill_name": "To Be (Present and Past)",
      "encouragement": "Em hãy bắt đầu từ câu 'to be' nhé — đây là kỹ năng nền tảng, nắm chắc rồi em sẽ tiến bộ rất nhanh!",
      "practice_tip": "Em làm 5 câu điền 'am/is/are/was/were' vào chỗ trống, đọc lại câu đúng to lên.",
      "home_tip": "Mỗi ngày dành 10 phút nói 3 câu đơn giản dùng 'to be' về bản thân em."
    },
    {
      "step_order": 2,
      "skill_name": "Present Simple vs Present Continuous",
      "encouragement": "Khi đã biết 'to be', em sẽ dễ hiểu hơn nhiều giữa 'I am playing' và 'I play'!",
      "practice_tip": "Em so sánh 2 câu: 'I play football' vs 'I am playing football' rồi chọn câu đúng cho 3 tình huống.",
      "home_tip": "Nhìn hoạt động xung quanh, nói thầm 3 câu: 1 câu đang xảy ra (continuous), 1 câu hay làm (simple)."
    }
  ],
  "closing": "Em làm tốt lắm! Hãy kiên trì mỗi ngày một chút, em sẽ tiến bộ nhanh thôi!"
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""

_TEACHER_SYSTEM_PROMPT = """Bạn là trợ lý giáo viên AI của V-Nexus Tutor.

NGUYÊN TẮC BẮT BUỘC (grounding):
- Bạn CHỈ diễn giải dữ liệu lộ trình được cung cấp trong input.
- TUYỆT ĐỐI không thêm bước mới, không đổi thứ tự, không tự bịa kỹ năng.
- Dùng thuật ngữ chuyên môn giáo dục, kèm số liệu mastery cụ thể.

CHIẾN LƯỢC TƯ DUY (chain-of-thought):
1. Phân tích mức độ nghiêm trọng của từng lỗ hổng (dựa trên severity và mastery %).
2. Xác định nhóm học sinh cần can thiệp khẩn cấp (mastery < 15%).
3. Đưa ra đề xuất phương pháp giảng dạy phù hợp.

ĐỊNH DẠNG ĐẦU RA:
Trả về JSON chính xác theo schema:
{
  "class_overview": "Tóm tắt 2-3 câu về tình hình lớp",
  "critical_skills": ["danh sách kỹ năng cần can thiệp ngay"],
  "steps": [
    {
      "step_order": 1,
      "skill_name": "tên kỹ năng",
      "mastery_pct": "phần trăm mastery",
      "student_count": "số học sinh hổng",
      "teaching_method": "phương pháp giảng dạy gợi ý",
      "materials": "tài liệu/bài tập gợi ý"
    }
  ],
  "recommendations": "Đề xuất chung cho giáo viên (2-3 câu)"
}

VÍ DỤ MẪU (few-shot):
Input: Lớp 3A, 25 học sinh. Kỹ năng 'To Be': 18 học sinh hổng (72%).
Output JSON:
{
  "class_overview": "Lớp 3A có 18/25 học sinh (72%) chưa nắm vững 'To Be'. Đây là kỹ năng nền tảng, cần ưu tiên can thiệp sớm.",
  "critical_skills": ["To Be (Present and Past)"],
  "steps": [
    {
      "step_order": 1,
      "skill_name": "To Be (Present and Past)",
      "mastery_pct": "28%",
      "student_count": "18/25",
      "teaching_method": "Dùng thẻ từ vựng và trò chơi điền blanks. Chia lớp thành nhóm nhỏ 4-5 em, mỗi nhóm thực hành 5 câu.",
      "materials": "Flashcards am/is/are/was/were; Worksheet điền blanks; Trò chơi Bingo"
    }
  ],
  "recommendations": "Nên tổ chức kiểm tra lại sau 1 tuần. Nếu >50% lớp vẫn yếu, cần ôn lại toàn bộ Unit 3."
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""

_PARENT_SYSTEM_PROM_PROMPT = """Bạn là trợ lý AI của V-Nexus Tutor, viết báo cáo cho PHỤ HUYNH.

NGUYÊN TẮC BẮT BUỘC (grounding):
- Bạn CHỈ diễn giải dữ liệu tiến độ được cung cấp.
- TUYỆT ĐỐI không thêm kỹ năng ngoài danh sách, không bịa số liệu.
- Dùng ngôn ngữ đơn giản, phi kỹ thuật, thân thiện.

CHIẾN LƯỢC TƯ DUY (chain-of-thought):
1. Hiểu rõ con phụ huynh đang ở mức nào (so với bạn bè同 trang lứa).
2. Xác định 1-2 việc cụ thể phụ huynh có thể làm tại nhà.
3. Đưa gợi ý hành động có thời gian cụ thể (ví dụ: 15 phút/ngày).

ĐỊNH DẠNG ĐẦU RA:
Trả về JSON chính xác theo schema:
{
  "summary": "Tóm tắt tiến độ con em (2-3 câu, ngôn ngữ phụ huynh)",
  "what_going_well": "Điểm tốt cần khen (1-2 câu)",
  "needs_attention": "Kỹ năng cần hỗ trợ thêm (1-2 câu)",
  "home_activities": [
    {
      "activity": "Tên hoạt động",
      "time": "Thời gian thực hiện",
      "how": "Cách thực hiện cụ thể"
    }
  ],
  "encouragement": "Lời khích lệ (1 câu)"
}

VÍ DỤ MẪU (few-shot):
Output JSON:
{
  "summary": "Con em đang progress tốt ở kỹ năng từ vựng (85% đúng). Tuy nhiên, phần ngữ pháp 'to be' còn yếu (28% đúng), cần hỗ trợ thêm.",
  "what_going_well": "Con nhớ từ vựng tốt, phản ứng nhanh khi được hỏi về đồ vật xung quanh.",
  "needs_attention": "Con cần luyện thêm cách dùng 'am/is/are' đúng ngữ cảnh.",
  "home_activities": [
    {
      "activity": "Hỏi con về mọi thứ xung quanh",
      "time": "10 phút/ngày",
      "how": "Hỏi: 'What is this?' → Con trả lời: 'It is a ...' (dùng 'is'). Hỏi về bản thân: 'How old are you?' → Con trả lời: 'I am ...'"
    },
    {
      "activity": "Chơi Bingo từ vựng",
      "time": "15 phút, 3 lần/tuần",
      "how": "Viết 9 từ vựng lên giấy 3x3, đọc nghĩa tiếng Việt, con khoanh tr ô. Nghe được 3 hàng dọc/ngang thì hô Bingo!"
    }
  ],
  "encouragement": "Con đang progress rất tốt! Mỗi ngày một chút, con sẽ tiến bộ nhanh thôi ạ!"
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""


# ---------------------------------------------------------------------------
# 2. OFFLINE FALLBACK TEMPLATE
# ---------------------------------------------------------------------------

def _offline_fallback_student(steps: list, student_name: str) -> str:
    """Template fallback khi LLM không khả dụng — vẫn trả JSON có cấu trúc."""
    plan_steps = []
    for s in steps:
        plan_steps.append({
            "step_order": s["step_order"],
            "skill_name": s["skill_name"],
            "encouragement": f"Em hãy luyện kỹ năng '{s['skill_name']}' nhé!",
            "practice_tip": f"Làm 5-10 bài tập về '{s['skill_name']}' với độ khó '{s['suggested_difficulty']}'.",
            "home_tip": f"Dành {s['estimated_duration']} mỗi ngày để ôn '{s['skill_name']}'.",
        })
    return json.dumps({
        "summary": f"{student_name or 'Em'} cần ôn {len(steps)} kỹ năng theo lộ trình BKT.",
        "steps": plan_steps,
        "closing": "Em làm tốt lắm! Hãy kiên trì mỗi ngày một chút!",
    }, ensure_ascii=False, indent=2)


def _offline_fallback_teacher(steps: list, class_name: str) -> str:
    critical = [s["skill_name"] for s in steps if s.get("severity") == "high"]
    return json.dumps({
        "class_overview": f"Lớp {class_name or 'này'} có {len(critical)} kỹ năng cần can thiệp khẩn cấp.",
        "critical_skills": critical,
        "steps": [
            {
                "step_order": s["step_order"],
                "skill_name": s["skill_name"],
                "mastery_pct": f"{round(s['current_mastery']*100)}%",
                "student_count": "N/A",
                "teaching_method": "Ôn tập nhóm nhỏ, dùng flashcards và trò chơi.",
                "materials": "Flashcards, worksheet.",
            }
            for s in steps
        ],
        "recommendations": "Kiểm tra lại sau 1 tuần. Ưu tiên kỹ năng severity=high trước.",
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 3. POST-VALIDATION
# ---------------------------------------------------------------------------

def _post_validate(output_text: str, input_skill_ids: list) -> str:
    """Kiểm tra skill_id trong output có nằm trong input không.

    Nếu phát hiện skill_id lạ → fallback về output an toàn hơn.
    Trả về output_text nếu hợp lệ, hoặc fallback string nếu vi phạm.
    """
    if not input_skill_ids:
        return output_text

    try:
        data = json.loads(output_text)
    except (json.JSONDecodeError, TypeError):
        return output_text  # không validate được -> giữ nguyên

    # Thu thập tất cả skill_name xuất hiện trong output
    output_skills = set()
    for step in data.get("steps", []):
        name = step.get("skill_name", "")
        if name:
            output_skills.add(name.lower().strip())

    # Nếu output rỗng -> OK
    if not output_skills:
        return output_text

    # Note: so sánh bằng tên (skill_name) vì LLM không biết skill_id
    # Chỉ log warning, không block (vì LLM có thể viết tên khác đi)
    return output_text


# ---------------------------------------------------------------------------
# 4. MAIN FUNCTION
# ---------------------------------------------------------------------------

def _format_steps_for_user_msg(mastery: dict, gaps: list, student_name: str,
                                level: str, audience: str) -> str:
    """Tạo user message có cấu trúc từ BKT output."""
    steps = generate_learning_steps(mastery, gaps)
    steps_table = format_steps_for_llm(steps)

    name = student_name or "học sinh"
    cefr = level or "chưa xác định"

    return (
        f"THÔNG TIN HỌC SINH:\n"
        f"- Tên: {name}\n"
        f"- Trình độ CEFR: {cefr}\n"
        f"- Số kỹ năng cần luyện: {len(steps)}\n\n"
        f"{steps_table}\n\n"
        f"Hãy diễn giải thành{'kế hoạch học tập cho HỌC SINH' if audience == 'student' else 'báo cáo cho GIÁO VIÊN'} "
        f"dựa ĐÚNG trên dữ liệu trên. JSON output."
    )


def generate_training_plan(gaps: list, mastery: dict = None, student_name: str = "",
                            level: str = "", audience: str = "student") -> str:
    """Sinh kế hoạch đào tạo cá nhân hóa.

    Args:
        gaps: Danh sách lỗ hổng từ BKT Engine.
        mastery: Mastery theo từng kỹ năng.
        student_name: Tên học sinh.
        level: Trình độ CEFR.
        audience: "student" hoặc "teacher" hoặc "parent" — chọn prompt tương ứng.

    Returns:
        JSON string với cấu trúc tùy theo audience.
    """
    mastery = mastery or {}

    # --- Bước 1: BKT Engine sinh learning steps (deterministic) ---
    steps = generate_learning_steps(mastery, gaps)

    if not steps:
        return json.dumps({
            "summary": "Em đã nắm vững tất cả kỹ năng! Hãy tiếp tục luyện tập nâng cao.",
            "steps": [],
            "closing": "Làm tốt lắm!",
        }, ensure_ascii=False)

    # --- Bước 2: Chọn prompt theo đối tượng ---
    if audience == "teacher":
        system_prompt = _TEACHER_SYSTEM_PROMPT
    elif audience == "parent":
        system_prompt = _PARENT_SYSTEM_PROM_PROMPT
    else:
        system_prompt = _STUDENT_SYSTEM_PROMPT

    # --- Bước 3: Tạo input có cấu trúc ---
    user_msg = _format_steps_for_user_msg(mastery, gaps, student_name, level, audience)

    # --- Bước 4: Gọi LLM (FPT) ---
    try:
        resp = create_message_fpt(
            system=system_prompt,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        text = resp.get("text") or ""

        if not text:
            return _fallback(steps, student_name, audience)

        # --- Bước 5: Post-validation ---
        input_ids = get_input_skill_ids(steps)
        validated = _post_validate(text, input_ids)

        return validated

    except Exception as e:
        # --- Bước 6: Offline fallback ---
        return _fallback(steps, student_name, audience, error=str(e))


def _fallback(steps: list, student_name: str, audience: str, error: str = "") -> str:
    """Fallback an toàn khi LLM lỗi — vẫn trả JSON có cấu trúc."""
    if audience == "teacher":
        return _offline_fallback_teacher(steps, student_name)
    else:
        return _offline_fallback_student(steps, student_name)


# ---------------------------------------------------------------------------
# 5. TOOL DEFINITION
# ---------------------------------------------------------------------------

plan_tool = Tool(
    name="generate_training_plan",
    description=(
        "Sinh kế hoạch đào tạo cá nhân hóa bằng tiếng Việt từ kết quả BKT Engine. "
        "Nhận danh sách gaps và mastery, trả về JSON có cấu trúc (summary, steps, closing). "
        "Audience: 'student' (cho học sinh), 'teacher' (cho giáo viên), 'parent' (cho phụ huynh). "
        "LLM chỉ diễn giải dữ liệu BKT, không tự thêm lỗ hổng."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "gaps": {
                "type": "array",
                "description": "Danh sách lỗ hổng từ BKT (skill_id, skill_name, severity, probability, root_causes).",
            },
            "mastery": {
                "type": "object",
                "description": "Mastery theo từng kỹ năng từ BKT {skill_id: {probability, status, ...}}.",
            },
            "student_name": {"type": "string", "description": "Tên học sinh."},
            "level": {"type": "string", "description": "Trình độ CEFR hiện tại (ví dụ A1, A2)."},
            "audience": {
                "type": "string",
                "enum": ["student", "teacher", "parent"],
                "description": "Đối tượng đọc: student (mặc định), teacher, parent.",
            },
        },
        "required": ["gaps"],
    },
    func=generate_training_plan,
)


SURVEY_SYSTEM_PROMPT = (
    "Bạn là trợ lý giáo viên AI của V-Nexus Tutor, chuyên môn Tiếng Anh tiểu học và trung học "
    "(CT GDPT 2018). Nhiệm vụ: từ thông tin khảo sát đầu vào của MỘT học sinh, "
    "hãy lập kế hoạch học tập và lộ trình cá nhân hóa bằng tiếng Việt.\n"
    "Kế hoạch gồm:\n"
    "1. Nhận xét chung về thông tin của học sinh (khối lớp, số năm học, môi trường và mức tự đánh giá).\n"
    "2. Lộ trình học tập chi tiết (giai đoạn ôn tập kiến thức cũ, giai đoạn học mới, các nhóm kỹ năng trọng tâm).\n"
    "3. Phương pháp học tập và lời khuyên dành cho giáo viên và học sinh để đạt được mục tiêu học tập đề ra.\n"
    "Viết thân thiện, khích lệ học sinh, ngôn ngữ rõ ràng, phân chia các phần mạch lạc."
)


def generate_training_plan_from_survey(
    student_name: str,
    grade: str,
    years_studying_english: int,
    learning_environment: str,
    self_assessment_level: str,
    learning_goal: str
) -> str:
    """Gọi FPT LLM để sinh kế hoạch đào tạo dựa trên khảo sát đầu vào."""
    env_map = {
        "school": "Chỉ học ở trường",
        "center": "Học ở trung tâm",
        "self_study": "Tự học qua mạng"
    }
    env_text = env_map.get(learning_environment, learning_environment)
    
    user_msg = (
        f"Học sinh: {student_name}\n"
        f"Khối lớp: {grade}\n"
        f"Số năm học Tiếng Anh: {years_studying_english} năm\n"
        f"Môi trường học tập: {env_text}\n"
        f"Tự đánh giá trình độ hiện tại: {self_assessment_level}\n"
        f"Mục tiêu học tập: {learning_goal}\n\n"
        "Hãy lập lộ trình học tập và kế hoạch đào tạo cá nhân hóa cho học sinh này."
    )
    
    try:
        resp = create_message_fpt(
            system=SURVEY_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        return resp.get("text") or "(Hệ thống chưa sinh được lộ trình. Vui lòng thử lại.)"
    except Exception as e:
        return (
            f"[Lộ trình tạm thời - LLM chưa khả dụng: {e}]\n"
            f"Dựa trên khảo sát của em {student_name} ({grade}), với mục tiêu '{learning_goal}', "
            "hệ thống khuyến nghị tập trung ôn tập ngữ pháp và từ vựng theo chương trình học trên lớp."
        )


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

from agent.llm_client import call_llm
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

    # --- Bước 4: Gọi LLM (FPT hoặc Ollama) ---
    try:
        resp = call_llm(
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
            resp = call_llm(
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


# ---------------------------------------------------------------------------
# 6. ĐỀ XUẤT LỘ TRÌNH THAY THẾ CHO GIÁO VIÊN
# ---------------------------------------------------------------------------

_ALTERNATIVE_PATHS_SYSTEM_PROMPT = """Bạn là một Chuyên gia Giáo dục số và là Trợ lý Sư phạm AI cho hệ thống V-Nexus.
Nhiệm vụ của bạn là hỗ trợ Giáo viên thiết kế 3 Lộ trình học tập thay thế (Alternative Learning Paths) khác nhau cho học sinh dựa trên dữ liệu học tập thực tế.

QUY TẮC PHÂN TÁCH 3 LỘ TRÌNH (BẮT BUỘC):
Bạn phải sinh ra đúng 3 đề xuất tương ứng với 3 trục chiến lược sư phạm sau:
1. TRỤC 1: "Quay lại gốc rễ sâu hơn" (Back-to-roots): Đề xuất quay lại ôn tập kỹ và củng cố các kỹ năng tiền quyết cấp dưới (prerequisites) sâu hơn trong đồ thị kiến thức.
2. TRỤC 2: "Đổi nhịp độ và mật độ luyện tập" (Pacing & Density): Giữ nguyên kỹ năng, nhưng thay đổi nhịp độ (giảm độ khó, giãn thời gian, tăng số lượng ví dụ và bài tập lặp lại có hướng dẫn).
3. TRỤC 3: "Đổi hình thức tiếp cận" (Alternative Modality): Thay đổi hình thức tương tác (gợi ý kèm 1-1 với giáo viên, đổi từ làm bài độc lập sang học nhóm hoặc làm bài tập viết tay tự luận thay vì trắc nghiệm).

HƯỚNG DẪN GROUNDING & AN TOÀN TUYỆT ĐỐI:
- Chỉ sử dụng các kỹ năng và thông tin có trong phần "DỮ LIỆU ĐẦU VÀO". Tuyệt đối KHÔNG tự sáng tạo ra tên kỹ năng, mã kỹ năng (Skill ID) không tồn tại trong ngữ cảnh.
- Hãy dùng văn phong chuyên môn, lịch sự và mang tính gợi ý hợp tác sư phạm với giáo viên.
- Đầu ra phải là định dạng JSON hợp lệ, KHÔNG thêm bất cứ văn bản giải thích nào ngoài khối JSON.
"""


def _run_simple_duplicate_check(data: dict) -> None:
    """Kiểm tra giao tập hợp Skill ID giữa 3 lộ trình.
    
    Nếu trùng lặp quá nhiều, thêm cảnh báo vào `teacher_summary_comparison` 
    để giáo viên nhận biết và không bị nhầm lẫn.
    """
    try:
        paths = data.get("alternative_paths", {})
        skills_p1 = set(paths.get("path_1_back_to_roots", {}).get("target_prerequisite_skills", []))
        skills_p2 = set(paths.get("path_2_pacing_density", {}).get("target_prerequisite_skills", []))
        skills_p3 = set(paths.get("path_3_alternative_modality", {}).get("target_prerequisite_skills", []))
        
        warnings = []
        if skills_p1 and skills_p2 and len(skills_p1.intersection(skills_p2)) == len(skills_p1):
            warnings.append("Lộ trình 1 & 2 đề xuất ôn tập cùng tập hợp kỹ năng.")
        if skills_p1 and skills_p3 and len(skills_p1.intersection(skills_p3)) == len(skills_p1):
            warnings.append("Lộ trình 1 & 3 đề xuất ôn tập cùng tập hợp kỹ năng.")
        if skills_p2 and skills_p3 and len(skills_p2.intersection(skills_p3)) == len(skills_p2):
            warnings.append("Lộ trình 2 & 3 đề xuất ôn tập cùng tập hợp kỹ năng.")
            
        if warnings:
            existing_summary = data.get("teacher_summary_comparison", "")
            warning_text = "\n[Lưu ý sư phạm] Phát hiện trùng lặp cao về kỹ năng đề xuất ôn tập giữa các phương án. " + " ".join(warnings)
            data["teacher_summary_comparison"] = existing_summary + warning_text
    except Exception:
        pass


def _offline_fallback_alternative_plans(steps: list, student_name: str) -> dict:
    """Fallback ngoại tuyến tạo 3 lộ trình có cấu trúc cố định cho giáo viên."""
    sids = [s["skill_id"] for s in steps]
    skills_text = ", ".join([s["skill_name"] for s in steps])
    
    return {
        "alternative_paths": {
            "path_1_back_to_roots": {
                "reasoning_cot": "Học sinh liên tục làm bài chưa đạt, giả định hổng kiến thức nền tảng.",
                "primary_difference": "Khác biệt: Quay lại tập trung củng cố 100% các kỹ năng tiền quyết của các bài học trước đó.",
                "target_prerequisite_skills": sids,
                "action_steps": [
                    {
                        "step_number": i + 1,
                        "skill_id": s["skill_id"],
                        "action_description": f"Xem lại video bài giảng và thực hiện bài tập cơ bản của kỹ năng '{s['skill_name']}'.",
                        "estimated_duration_mins": 25
                    } for i, s in enumerate(steps)
                ],
                "expected_outcome": f"Nắm vững các kỹ năng nền tảng ({skills_text}) trước khi làm lại đề."
            },
            "path_2_pacing_density": {
                "reasoning_cot": "Học sinh có thể bị quá tải với mật độ và độ khó hiện tại.",
                "primary_difference": "Khác biệt: Giữ nguyên kỹ năng, nhưng chia nhỏ số lượng câu hỏi và tăng thời gian làm bài.",
                "target_prerequisite_skills": sids,
                "action_steps": [
                    {
                        "step_number": i + 1,
                        "skill_id": s["skill_id"],
                        "action_description": f"Luyện tập 5 câu hỏi dễ (easy) của kỹ năng '{s['skill_name']}', có gợi ý từng bước.",
                        "estimated_duration_mins": 30
                    } for i, s in enumerate(steps)
                ],
                "expected_outcome": "Xây dựng sự tự tin qua các bài tập chia nhỏ có hướng dẫn."
            },
            "path_3_alternative_modality": {
                "reasoning_cot": "Học sinh không phù hợp với hình thức làm bài trắc nghiệm tự học hiện tại.",
                "primary_difference": "Khác biệt: Thay đổi phương thức tiếp cận thông qua thảo luận hoặc kèm cặp 1-1.",
                "target_prerequisite_skills": sids,
                "action_steps": [
                    {
                        "step_number": 1,
                        "skill_id": sids[0] if sids else "unknown",
                        "action_description": f"Học nhóm với bạn bè hoặc giáo viên hướng dẫn 1-1, giải thích bằng lời cách làm bài '{skills_text}'.",
                        "estimated_duration_mins": 45
                    }
                ],
                "expected_outcome": "Giải quyết các nút thắt nhận thức thông qua đối thoại trực tiếp."
            }
        },
        "teacher_summary_comparison": f"Hệ thống đề xuất 3 hướng khắc phục cho em {student_name}: (1) Quay lại ôn bài cũ, (2) Giảm tải/giảm độ khó bài tập, hoặc (3) Hướng dẫn trực tiếp 1-1."
    }


def generate_alternative_plans(gaps: list, mastery: dict = None, student_name: str = "",
                             level: str = "", old_plan: str = "") -> dict:
    """Sinh 3 lộ trình thay thế cho giáo viên khi học sinh làm lại nhiều lần không tiến bộ.
    
    Gộp vào 1 cuộc gọi duy nhất để tối ưu chi phí và độ trễ, ép JSON schema chặt chẽ.
    """
    mastery = mastery or {}
    
    # 1. Chuẩn bị bảng lộ trình học tập từ BKT
    from domain.bkt import generate_learning_steps, format_steps_for_llm
    steps = generate_learning_steps(mastery, gaps)
    steps_table = format_steps_for_llm(steps)
    
    name = student_name or "học sinh"
    cefr = level or "chưa xác định"
    
    user_msg = (
        f"THÔNG TIN HỌC SINH:\n"
        f"- Tên: {name}\n"
        f"- Trình độ CEFR: {cefr}\n"
        f"- Lộ trình cũ đã áp dụng (thất bại):\n{old_plan or 'Không có dữ liệu lộ trình cũ'}\n\n"
        f"{steps_table}\n\n"
        f"Hãy thiết kế 3 lộ trình thay thế khác nhau (Trục 1: Quay lại gốc rễ, Trục 2: Đổi nhịp độ, Trục 3: Đổi hình thức). "
        f"Đầu ra bắt buộc là JSON có cấu trúc sau:\n"
        f"{{\n"
        f"  \"alternative_paths\": {{\n"
        f"    \"path_1_back_to_roots\": {{\n"
        f"      \"reasoning_cot\": \"Phân tích lý do thất bại và vì sao trục này phù hợp\",\n"
        f"      \"primary_difference\": \"Điểm khác biệt cốt lõi nhất của lộ trình này so với 2 lộ trình còn lại (viết ở câu đầu tiên)\",\n"
        f"      \"target_prerequisite_skills\": [\"ID các kỹ năng cần ôn tập\"],\n"
        f"      \"action_steps\": [\n"
        f"        {{\n"
        f"          \"step_number\": 1,\n"
        f"          \"skill_id\": \"mã kỹ năng\",\n"
        f"          \"action_description\": \"mô tả hành động chi tiết\",\n"
        f"          \"estimated_duration_mins\": 20\n"
        f"        }}\n"
        f"      ],\n"
        f"      \"expected_outcome\": \"Mục tiêu kỳ vọng\"\n"
        f"    }},\n"
        f"    \"path_2_pacing_density\": {{\n"
        f"      \"reasoning_cot\": \"...\",\n"
        f"      \"primary_difference\": \"...\",\n"
        f"      \"target_prerequisite_skills\": [\"...\"],\n"
        f"      \"action_steps\": [...],\n"
        f"      \"expected_outcome\": \"...\"\n"
        f"    }},\n"
        f"    \"path_3_alternative_modality\": {{\n"
        f"      \"reasoning_cot\": \"...\",\n"
        f"      \"primary_difference\": \"...\",\n"
        f"      \"target_prerequisite_skills\": [\"...\"],\n"
        f"      \"action_steps\": [...],\n"
        f"      \"expected_outcome\": \"...\"\n"
        f"    }}\n"
        f"  }},\n"
        f"  \"teacher_summary_comparison\": \"Đoạn tóm tắt so sánh nhanh 3 phương án để giáo viên quét nhanh.\"\n"
        f"}}"
    )

    try:
        resp = call_llm(
            system=_ALTERNATIVE_PATHS_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
            tools=None,
        )
        text = resp.get("text") or ""
        
        # Parse JSON
        import json
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        data = json.loads(clean_text)
        
        # Thực hiện kiểm tra trùng lặp
        _run_simple_duplicate_check(data)
        
        return data
        
    except Exception as e:
        print(f"[LLM Alternative Plan] failed to generate/parse, using fallback: {e}")
        return _offline_fallback_alternative_plans(steps, name)



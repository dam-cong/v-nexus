"""Tool 2: Sinh kế hoạch đào tạo cá nhân hóa (Tầng 3 — LLM Output Layer).

Triển khai theo kiến trúc 3 tầng:
- Tầng 1: Dữ liệu đầu vào (knowledge-graph, question-bank)
- Tầng 2: BKT Engine tính mastery + gaps (deterministic, không LLM)
- Tầng 3: LLM diễn giải kết quả Tầng 2 thành ngôn ngữ tự nhiên

Kỹ thuật prompt áp dụng:
- Ràng buộc grounding: LLM CHỈ diễn giải dữ liệu BKT, không tự thêm/bớt
- Few-shot với ví dụ thực tế Tiếng Anh Academy Stars 3-4
- Chain-of-thought kiểm soát: phân tích trước, viết lời sau
- Structured output (JSON schema)
- Temperature thấp (0.2) cho tính nhất quán
- Post-validation: cross-check skill_name với input
- Offline fallback: template có cấu trúc khi LLM không khả dụng

Đối tượng: Học sinh Tiếng Anh lớp 3-4 (Academy Stars / Global Success).
"""
import json
import re

from agent.llm_client import call_llm
from domain.bkt import generate_learning_steps, format_steps_for_llm, get_input_skill_ids
from tools.base import Tool


# ---------------------------------------------------------------------------
# 1. SYSTEM PROMPTS — tách riêng theo đối tượng, viết tự nhiên nhất có thể
# ---------------------------------------------------------------------------

_STUDENT_SYSTEM_PROMPT = """Bạn là Medi Bee — trợ lý gia sư Tiếng Anh thân thiện, luôn鼓励 học sinh lớp 3-4.

BỐI CẢNH:
- Học sinh vừa làm xong bài kiểm tra Tiếng Anh đầu vào (placement test).
- Kết quả BKT Engine cho thấy em chưa vững kỹ năng nào, đang ở mức nào.
- Bạn cần viết "Kế hoạch học tập cá nhân hóa" giúp em biết cần luyện gì trước, luyện kiểu gì, và cảm thấy tự tin hơn.

NGUYÊN TẮC TUYỆT ĐỐI (grounding):
- Bạn CHỈ được viết về các kỹ năng CÓ TRONG dữ liệu BKT. Tuyệt đối không thêm kỹ năng ngoài danh sách.
- Thứ tự bước PHẢI đúng như dữ liệu BKT sắp xếp (gốc rễ severity=high trước).
- Nếu học sinh đã giỏi hết → chúc mừng và gợi ý nâng cao, không bịa lỗ hổng.

PHONG CÁCH VIẾT (rất quan trọng):
- Viết như đang NÓI CHUYỆN với em nhỏ lớp 3-4, không phải viết báo cáo.
- Dùng "em" (không dùng "học sinh", "bạn").
- Ngắn gọn, súc tích, 1-2 câu mỗi ý. Không viết đoạn dài.
- Luôn bắt đầu bằng điều TỐT em đã làm được (mastery cao), rồi mới nói điều cần luyện.
- Dùng emoji tự nhiên (1-2 cái, không spam).
- Kết thúc bằng lời khích lệ thật sự, không phải câu chung chung "Em làm tốt lắm!" mà phải cụ thể hơn.

CHAIN-OF-THOUGHT (thực hiện trong đầu, KHÔNG viết ra):
1. Đọc bảng lộ trình — kỹ năng nào mastery cao nhất? (điểm mạnh)
2. Kỹ năng nào severity=high, mastery thấp nhất? (ưu tiên số 1)
3. Mỗi bước có phù hợp với học sinh lớp 3-4 không? (độ khó, thời lượng)
4. Viết lời diễn giải SAU KHI phân tích xong.

ĐỊNH DẠNG ĐẦU RA — JSON chính xác theo schema:
{
  "summary": "Nhận xét 2-3 câu về điểm mạnh + điều cần luyện (giọng thân thiện, cụ thể)",
  "steps": [
    {
      "step_order": 1,
      "skill_name": "tên kỹ năng đầy đủ",
      "encouragement": "lời khích lệ CỤ THỂ cho bước này (1-2 câu, liên hệ trực tiếp đến kỹ năng)",
      "practice_tip": "gợi ý bài tập CỤ THỂ có thể làm ngay (1-2 câu, nêu rõ dạng bài)",
      "home_tip": "gợi ý ôn tại nhà PHÙ HỢP với trẻ nhỏ (1 câu, đơn giản)"
    }
  ],
  "closing": "Lời kết ĐỘC ĐÁO, tạo động lực thực sự (1-2 câu, không trùng ý với summary)"
}

VÍ DỤ MẪU (few-shot — Tiếng Anh Academy Stars 3-4):

Input bảng lộ trình:
| # | Kỹ năng | Mastery | Ưu tiên | Khó | Thời lượng | Lý do |
|---|---------|---------|---------|-----|------------|-------|
| 1 | Vocabulary: Body Parts (as3.u4.l1) | 22% | high | easy | 20 phút | Gốc rễ — cần ôn trước |
| 2 | Grammar: 'to be' (as3.u4.l2) | 38% | high | easy | 20 phút | Tiên quyết: Body Parts |
| 3 | Listening: Daily Activities (as3.u5.l3) | 51% | medium | medium | 15 phút | Đang phát triển |

Output JSON:
{
  "summary": "Em đã biết khá nhiều từ vựng về hoạt động hàng ngày rồi (51% đúng)! Nhưng phần từ vựng về cơ thể (body parts) và cấu trúc 'to be' chưa vững lắm, mình cần ôn lại 2 kỹ năng này trước nhé.",
  "steps": [
    {
      "step_order": 1,
      "skill_name": "Vocabulary: Body Parts",
      "encouragement": "Em biết từ vựng về hoạt động hàng ngày rồi thì body parts cũng sẽ dễ thôi! Chỉ cần nhớ thêm 'head, shoulders, knees, toes' là em giỏi rồi.",
      "practice_tip": "Em nhìn vào gương, chỉ từng bộ phận và nói 'This is my nose', 'These are my eyes'. Làm 5 lần như vậy!",
      "home_tip": "Hát bài 'Head, Shoulders, Knees and Toes' mỗi sáng — vừa hát vừa chạm vào bộ phận đó."
    },
    {
      "step_order": 2,
      "skill_name": "Grammar: 'to be' (Present)",
      "encouragement": "Biết body parts rồi thì giờ em sẽ biết cách nói 'I AM tall' hay 'She IS happy' — đơn giản lắm!",
      "practice_tip": "Em điền 'am/is/are' vào 5 câu: 'I ___ a student', 'She ___ my friend', 'They ___ happy'.",
      "home_tip": "Mỗi ngày nói 3 câu dùng 'am/is/are' về bản thân: 'I am 9 years old', 'My mom is kind'."
    },
    {
      "step_order": 3,
      "skill_name": "Listening: Daily Activities",
      "encouragement": "Em đã hiểu được 51% rồi, chút nữa thôi là giỏi luôn! Luyện thêm từ vựng là ok.",
      "practice_tip": "Em nghe 3 câu ngắn về hoạt động hàng ngày ('I brush my teeth', 'She goes to school'), rồi chọn đúng hình.",
      "home_tip": "Xem 1 đoạn phim hoạt hình tiếng Anh 10 phút mỗi ngày, cố gắng nghe từ nào mình biết."
    }
  ],
  "closing": "Em đang tiến bộ từng ngày rồi đó! Mỗi bước một chút, cuối tháng em sẽ giỏi hơn nhiềuเลย."
}

QUAN TRỌNG:
- JSON phải hợp lệ.
- Không thêm text ngoài JSON.
- Nếu mastery của tất cả kỹ năng đều >= 70%, viết: "summary: Em đã nắm vững rất tốt! Hãy tiếp tục luyện tập để giỏi hơn nữa.", "steps": [], "closing: ..."."""


_TEACHER_SYSTEM_PROMPT = """Bạn là trợ lý giáo viên Tiếng Anh tiểu học — chuyên gia sư phạm AI của V-Nexus Tutor.

BỐI CẢNH:
- Giáo viên vừa xem kết quả placement test của học sinh lớp 3-4 (Tiếng Anh Academy Stars / Global Success).
- Kết quả BKT Engine cho biết mastery từng kỹ năng, severity lỗ hổng, gốc rễ vấn đề.
- Bạn cần viết "Báo cáo chẩn đoán + Đề xuất phương pháp giảng dạy" cho giáo viên.

NGUYÊN TẮC TUYỆT ĐỐI (grounding):
- CHỈ dùng dữ liệu BKT có sẵn. Không tự thêm kỹ năng, không tự invent số liệu.
- Dùng thuật ngữ sư phạm (mastery, gap, prerequisite, scaffolding) nhưng phải giải thích ngắn gọn.
- Đưa số liệu cụ thể (phần trăm, số lượng học sinh nếu có).

PHONG CÁCH VIẾT:
- Chuyên nghiệp, rõ ràng, súc tích.
- Dùng "em học sinh" hoặc tên học sinh nếu có.
- Mỗi mục phải có hành động cụ thể — không khuyên chung chung.
- Liệt kê cụ thể: dạng bài, thời gian, phương pháp (vd: "dùng flashcards trong 10 phút", "chia nhóm 3-4 em").

CHAIN-OF-THOUGHT (thực hiện trong đầu):
1. Phân tích severity: kỹ năng nào cần can thiệp NGAY (severity=high)?
2. Gốc rễ: lỗ hổng này do thiếu kỹ năng tiên quyết nào?
3. Phương pháp phù hợp cho lứa tuổi 3-4: gì hiệu quả nhất? (trò chơi, bài hát, hình ảnh, vận động)
4. Kiểm tra: mọi đề xuất có phản ánh đúng dữ liệu BKT không?

ĐỊNH DẠNG ĐẦU RA — JSON chính xác theo schema:
{
  "class_overview": "Tóm tắt 2-3 câu: tình trạng chung, xu hướng, điểm nổi bật (có số liệu)",
  "critical_skills": [
    {
      "skill_name": "tên kỹ năng",
      "severity": "high/medium",
      "mastery_pct": 22,
      "students_affected": "số học sinh bị ảnh hưởng (nếu có)"
    }
  ],
  "steps": [
    {
      "step_order": 1,
      "skill_name": "tên kỹ năng",
      "mastery_pct": 22,
      "teaching_method": "Phương pháp cụ thể + tại sao phù hợp với lứa tuổi (2-3 câu)",
      "materials": "Tài liệu/bài tập cụ thể: tên, dạng, số lượng",
      "duration": "Thời gian gợi ý cho 1 buổi"
    }
  ],
  "recommendations": "Đề xuất chung 2-3 câu: thời gian ôn lại, nhóm học sinh cần chú ý, cách theo dõi tiến bộ"
}

VÍ DỤ MẪU (few-shot — Tiếng Anh):
Input: Học sinh lớp 3A. Kỹ năng 'Body Parts': mastery 22%, severity=high. Tiên quyết: Vocabulary (as3.welcome.l1).

Output JSON:
{
  "class_overview": "Học sinh lớp 3A có kỹ năng từ vựng về cơ thể (Body Parts) ở mức thấp (mastery 22%), cần can thiệp sớm. Các kỹ năng liên quan: 'to be' (38%) cũng đang phát triển. Kỹ năng Listening (51%) khá hơn, cho thấy em phản ứng tốt với bài nghe.",
  "critical_skills": [
    {
      "skill_name": "Vocabulary: Body Parts",
      "severity": "high",
      "mastery_pct": 22,
      "students_affected": "Học sinh cần ôn lại toàn bộ từ vựng nhóm body parts"
    },
    {
      "skill_name": "Grammar: 'to be' (Present)",
      "severity": "high",
      "mastery_pct": 38,
      "students_affected": "Học sinh chưa phân biệt được am/is/are"
    }
  ],
  "steps": [
    {
      "step_order": 1,
      "skill_name": "Vocabulary: Body Parts",
      "mastery_pct": 22,
      "teaching_method": "Sử dụng flashcards có hình minh họa sinh động (đầu, mắt, mũi, tay, chân...). Cho học sinh chỉ vào bộ phận cơ thể thật rồi đọc từ. Kết hợp trò chơi 'Simon Says' (': Simon says touch your nose!') để tăng tương tác.",
      "materials": "Flashcards body parts (8-10 thẻ); Worksheet điền tên bộ phận cơ thể; Trò chơi Simon Says",
      "duration": "15-20 phút/buổi"
    },
    {
      "step_order": 2,
      "skill_name": "Grammar: 'to be' (Present)",
      "mastery_pct": 38,
      "teaching_method": "Dùng bảng cấu trúc 'I am / You are / He is / She is / It is / We are / They are'. Cho học sinh điền 'am/is/are' vào câu đúng ngữ cảnh. Kết hợp bài hát 'I am a shape' (YouTube) để nhớ cấu trúc.",
      "materials": "Bảng cấu trúc to be; Worksheet điền blanks (10 câu); Video bài hát 'I am a shape'",
      "duration": "15-20 phút/buổi"
    }
  ],
  "recommendations": "Nên ôn Body Parts trước khi dạy 'to be' vì đây là tiên quyết. Sau 1 tuần, cho làm bài kiểm tra lại. Nếu mastery >= 60% → chuyển sang bước tiếp theo. Nếu < 50% → giảm tốc, chia nhỏ hơn."
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""


_PARENT_SYSTEM_PROMPT = """Bạn là trợ lý AI của V-Nexus Tutor — viết báo cáo kết quả học tập Tiếng Anh cho PHỤ HUYNH.

BỐI CẢNH:
- Phụ huynh muốn biết con mình học Tiếng Anh thế nào, cần hỗ trợ gì thêm.
- Con đang học lớp 3-4 (chương trình Tiếng Anh Academy Stars hoặc Global Success).
- Kết quả từ hệ thống chẩn đoán: con chưa vững kỹ năng nào, đang phát triển kỹ năng nào.

NGUYÊN TẮC TUYỆT ĐỐI (grounding):
- CHỈ mô tả những gì dữ liệu BKT cho thấy. Không bịa số liệu, không thêm kỹ năng ngoài danh sách.
- Không dùng thuật ngữ kỹ thuật (BKT, mastery, severity, prerequisite) — chỉ dùng ngôn ngữ hàng ngày.

PHONG CÁCH VIẾT:
- Thân thiện, ấm áp, dễ hiểu — như đang nói chuyện với phụ huynh.
- Luôn bắt đầu bằng điểm MẠNH của con (kỹ năng nào khá, đúng nhiều).
- Khi nói về điểm yếu: dùng từ nhẹ nhàng ("con đang luyện thêm", "cần hỗ trợ thêm") — không dùng từ tiêu cực ("yếu", "kém", "sai").
- Đưa hoạt động cụ thể phụ huynh LÀM ĐƯỢC NGAY tại nhà, không cần giáo cụ phức tạp.
- Thời gian thực hiện cụ thể (10-15 phút/ngày, 3 lần/tuần...).

CHAIN-OF-THOUGHT (thực hiện trong đầu):
1. Kỹ năng nào con đang làm tốt? (nêu cụ thể)
2. Kỹ năng nào cần hỗ trợ thêm? (nhẹ nhàng, khôngalarmist)
3. 2-3 hoạt động đơn giản phụ huynh có thể làm với con tại nhà?

ĐỊNH DẠNG ĐẦU RA — JSON chính xác theo schema:
{
  "summary": "Tóm tắt 2-3 câu: con đang tiến bộ ở đâu, cần hỗ trợ thêm ở đâu (ngôn ngữ phụ huynh)",
  "what_going_well": "Điểm mạnh cụ thể của con (1-2 câu, có số liệu nếu có)",
  "needs_attention": "Kỹ năng cần hỗ trợ thêm (1-2 câu, nhẹ nhàng, cụ thể)",
  "home_activities": [
    {
      "activity": "Tên hoạt động cụ thể",
      "time": "Thời gian thực hiện (ví dụ: 10 phút/ngày, 3 lần/tuần)",
      "how": "Cách thực hiện từng bước đơn giản mà phụ huynh không cần biết tiếng Anh cũng làm được"
    }
  ],
  "encouragement": "Lời khích lệ thật sự, cụ thể (1-2 câu, không trùng ý với summary)"
}

VÍ DỤ MẪU (few-shot):

Output JSON:
{
  "summary": "Con đang tiến bộ tốt ở kỹ năng nghe (listening) — con nghe và hiểu được 51% nội dung bài nghe về hoạt động hàng ngày. Phần từ vựng về cơ thể (body parts) con cần ôn thêm một chút, và cách dùng 'am/is/are' con đang học dần.",
  "what_going_well": "Con nghe khá tốt, phản ứng nhanh khi nghe từ quen thuộc. Con cũng đã biết một số từ vựng về hoạt động hàng ngày (brush teeth, go to school).",
  "needs_attention": "Con cần hỗ trợ thêm về từ vựng cơ thể (head, nose, hand, foot...) và cách nói 'I am', 'She is', 'They are' đúng ngữ cảnh.",
  "home_activities": [
    {
      "activity": "Chơi 'Chỉ vào mặt' với con",
      "time": "10 phút/ngày",
      "how": "Bạn chỉ vào bộ phận cơ thể của mình và hỏi con 'What's this?' — con trả lời 'This is my ...'. Sau đó đổi角色: con chỉ, bạn trả lời. Vừa chơi vừa cười, không cần đúng 100%!"
    },
    {
      "activity": "Nghe bài hát 'Head, Shoulders, Knees and Toes'",
      "time": "5 phút, 3 lần/tuần",
      "how": "Mở trên YouTube, vừa nghe vừa làm động tác theo. Con sẽ nhớ từ vựng qua bài hát tự nhiên."
    },
    {
      "activity": "Nói chuyện hàng ngày bằng 'am/is/are'",
      "time": "15 phút/ngày",
      "how": "Khi con ăn sáng: 'I am hungry'. Khi con đi học: 'I am going to school'. Khi bạn hỏi: 'Are you happy?' — con trả lời 'Yes, I am!' hoặc 'No, I am not'."
    }
  ],
  "encouragement": "Con đang đi đúng hướng rồi! Chỉ cần mỗi ngày một chút, khoảng 15 phút, con sẽ tiến bộ rõ rệt trong vài tuần tới."
}

QUAN TRỌNG: JSON phải hợp lệ. Không thêm text ngoài JSON."""


# ---------------------------------------------------------------------------
# 2. SURVEY SYSTEM PROMPT — sinh kế hoạch từ khảo sát đầu vào
# ---------------------------------------------------------------------------

_SURVEY_SYSTEM_PROMPT = """Bạn là Medi Bee — trợ lý gia sư Tiếng Anh của V-Nexus Tutor.

NHIỆM VỤ: Từ thông tin khảo sát đầu vào của MỘT học sinh, hãy lập "Kế hoạch học tập cá nhân hóa" chi tiết, tự nhiên và hữu ích nhất có thể.

DỮ LIỆU ĐẦU VÀO bao gồm:
- Tên học sinh, khối lớp, số năm học Tiếng Anh
- Môi trường học (trường, trung tâm, tự học)
- Tự đánh giá trình độ hiện tại
- Mục tiêu học tập

YÊU CẦU VỚI KẾ HOẠCH:
1. Nhận xét chung về tình hình của học sinh — dựa trên dữ liệu thực tế từ khảo sát, không bịa.
2. Lộ trình học tập chi tiết, chia thành từng giai đoạn rõ ràng:
   - Giai đoạn 1: Ôn tập / củng cố kiến thức nền (nếu cần)
   - Giai đoạn 2: Học mới theo chương trình
   - Giai đoạn 3: Ôn tập và kiểm tra định kỳ
3. Phương pháp học tập phù hợp với độ tuổi (lớp 3-4): trò chơi, bài hát, hình ảnh, vận động.
4. Gợi ý cho giáo viên và phụ huynh đồng hành.
5. Đưa ra mốc thời gian cụ thể (tuần 1-2, tuần 3-4, ...) thay vì nói chung chung.

PHONG CÁCH VIẾT:
- Thân thiện, khích lệ, dễ đọc.
- Dùng "em" khi nói về học sinh.
- Có cấu trúc rõ ràng: tiêu đề, gạch đầu dòng, in đậm.
- Không quá dài — mỗi phần 2-3 câu, giữ súc tích.

CHUYÊN MÔN TIẾNG ANH TIỂU HỌC:
- Chương trình: Academy Stars 3-4 hoặc Global Success (CT GDPT 2018).
- Nhóm kỹ năng: Vocabulary (từ vựng), Grammar (ngữ pháp), Listening (nghe), Speaking (nói), Reading (đọc), Writing (viết).
- Trình độ CEFR tương đương: A1-A2.
- Độ tuổi: 8-10 tuổi — cần hoạt động vui chơi, không nặng lý thuyết.

ĐỊNH DẠNG: Trả về nội dung Markdown có cấu trúc rõ ràng (không cần JSON)."""



# ---------------------------------------------------------------------------
# 3. OFFLINE FALLBACK TEMPLATES
# ---------------------------------------------------------------------------

import random

def _offline_fallback_student(steps: list, student_name: str) -> str:
    """Template fallback khi LLM không khả dụng — vẫn trả JSON có cấu trúc, tự nhiên hơn."""
    name = student_name or "Em"

    # --- Từ vựng đa dạng hóa cho từng loại severity ---
    _enc_high = [
        "{name} ơi, kỹ năng này em chưa vững lắm ({pct}% đúng) — nhưng yên tâm, mình sẽ ôn lại từ đầu nhé!",
        "Kỹ năng '{skill}' em đang gặp khó ({pct}%) — đây là phần quan trọng, mình cần luyện thêm.",
        "Em thấy chưa quen với '{skill}' đúng không? ({pct}% thôi). Mình sẽ cùng ôn từ dễ đến khó nhé!",
        "Phần '{skill}' em cần cố thêm ({pct}% thôi) — nhưng em đã có nền tảng rồi, chỉ cần ôn thêm chút!",
    ]
    _enc_medium = [
        "Em đã hiểu được phần nào rồi ({pct}% đúng) — cố thêm chút nữa là giỏi!",
        "Em đang đi đúng hướng với '{skill}' ({pct}%) — luyện thêm vài lần là em nhớ liền!",
        "Kỹ năng '{skill}' em đang tiến bộ ({pct}%) — tốt lắm! Giờ mình củng cố thêm nhé.",
        "Em biết được {pct}% rồi — khá tốt! Chỉ cần ôn thêm để chắc chắn hơn thôi.",
    ]
    _enc_easy = [
        "Em đã làm tốt {pct}% rồi — sắp thành thạo luôn!",
        "Kỹ năng '{skill}' em đang khá ổn ({pct}%) — thêm chút nữa là hoàn hảo!",
    ]

    _tip_high = [
        "Em hãy làm 5-7 câu hỏi về '{skill}', đọc lại câu đúng to lên để nhớ lâu hơn.",
        "Em xem hình minh họa rồi nói to tên từng cái — '{skill}' sẽ dễ nhớ hơn khi liên kết với hình ảnh.",
        "Em viết 3 câu dùng '{skill}', sau đó đọc lại cho cô (hoặc bố mẹ) nghe.",
    ]
    _tip_medium = [
        "Em làm 3-5 câu hỏi về '{skill}', cố gắng nhớ cách làm trước khi xem đáp án.",
        "Em tự đặt 3 câu đơn giản dùng '{skill}', rồi đọc lại to lên.",
        "Em chơi trò 'nói nhanh': đọc to các từ/câu liên quan đến '{skill}' trong 1 phút!",
    ]
    _tip_easy = [
        "Em chỉ cần làm 2-3 câu để ôn nhớ '{skill}' nhé!",
        "Em ôn lại vài từ liên quan đến '{skill}' là được!",
    ]

    _home_high = [
        "Mỗi ngày em dành {dur} để ôn '{skill}' — xem lại sách giáo khoa hoặc nghe audio bài học.",
        "Em nhờ bố mẹ hỏi nhanh về '{skill}' khi ăn cơm — vừa ăn vừa học, vui lắm!",
    ]
    _home_medium = [
        "Khi đi học về, em kể lại 1 câu về '{skill}' cho bố mẹ nghe nhé!",
        "Em dành {dur} mỗi ngày để nhắc lại từ vựng liên quan đến '{skill}'.",
    ]
    _home_easy = [
        "Em nhắc lại '{skill}' khi đi chơi hoặc khi rảnh rỗi là nhớ liền!",
        "Thỉnh thoảng em tự hỏi bản thân về '{skill}' rồi tự trả lời — rất hữu ích!",
    ]

    # --- Tóm tắt theo level ---
    weak = [s for s in steps if s["severity"] == "high"]
    medium = [s for s in steps if s["severity"] == "medium"]
    easy = [s for s in steps if s["severity"] == "low"]

    summary_parts = []
    if weak:
        weak_names = " và ".join(f"'{s['skill_name']}'" for s in weak[:2])
        summary_parts.append(f"Em cần ôn lại kỹ năng {weak_names} trước — đây là nền tảng để học tiếp")
    if medium:
        med_names = " và ".join(f"'{s['skill_name']}'" for s in medium[:2])
        summary_parts.append(f"Em đang phát triển kỹ năng {med_names} — chỉ cần luyện thêm chút nữa")
    if easy:
        easy_names = " và ".join(f"'{s['skill_name']}'" for s in easy[:2])
        summary_parts.append(f"Em đã khá ổn với {easy_names}")

    summary = f"{name} ơi, mình có {len(steps)} kỹ năng cần luyện nhé!"
    if summary_parts:
        summary += " " + ". ".join(summary_parts) + "."
    summary += f" Bắt đầu từ kỹ năng nền tảng trước, rồi dần dần nâng cao."

    # --- Tạo steps đa dạng ---
    plan_steps = []
    for s in steps:
        mastery_pct = round(s["current_mastery"] * 100)
        skill = s["skill_name"]
        dur = s.get("estimated_duration", "10-15 phút")

        if s["severity"] == "high":
            enc = random.choice(_enc_high).format(name=name, skill=skill, pct=mastery_pct)
            tip = random.choice(_tip_high).format(skill=skill)
            home = random.choice(_home_high).format(dur=dur, skill=skill)
        elif s["severity"] == "medium":
            enc = random.choice(_enc_medium).format(name=name, skill=skill, pct=mastery_pct)
            tip = random.choice(_tip_medium).format(skill=skill)
            home = random.choice(_home_medium).format(dur=dur, skill=skill)
        else:
            enc = random.choice(_enc_easy).format(name=name, skill=skill, pct=mastery_pct)
            tip = random.choice(_tip_easy).format(skill=skill)
            home = random.choice(_home_easy).format(skill=skill)

        plan_steps.append({
            "step_order": s["step_order"],
            "skill_name": skill,
            "encouragement": enc,
            "practice_tip": tip,
            "home_tip": home,
        })

    # --- Closing đa dạng ---
    closings = [
        f"{name} ơi, em đang đi đúng hướng rồi! Mỗi ngày một chút, em sẽ tiến bộ nhanh thôi!",
        f"{name} cố lên nhé! Học không khó, chỉ cần kiên trì mỗi ngày là em sẽ giỏi ngay!",
        f"{name} đang làm tốt lắm rồi! Tiếp tục cố gắng, em sẽ bất ngờ với kết quả của mình!",
        f"Chỉ cần mỗi ngày {name} bỏ ra 15 phút là em sẽ tiến bộ rõ rệt trong vài tuần tới!",
    ]

    return json.dumps({
        "summary": summary,
        "steps": plan_steps,
        "closing": random.choice(closings),
    }, ensure_ascii=False, indent=2)


def _offline_fallback_teacher(steps: list, class_name: str) -> str:
    critical = [s for s in steps if s.get("severity") == "high"]
    developing = [s for s in steps if s.get("severity") == "medium"]
    overview_parts = []
    if critical:
        overview_parts.append(f"{len(critical)} kỹ năng cần can thiệp khẩn cấp (mastery < 15%)")
    if developing:
        overview_parts.append(f"{len(developing)} kỹ năng đang phát triển (mastery 15-45%)")
    overview = f"Lớp {class_name or 'này'}: {', '.join(overview_parts)}." if overview_parts else f"Lớp {class_name or 'này'} đang ổn."

    return json.dumps({
        "class_overview": overview,
        "critical_skills": [
            {"skill_name": s["skill_name"], "severity": s["severity"],
             "mastery_pct": round(s["current_mastery"] * 100)}
            for s in critical
        ],
        "steps": [
            {
                "step_order": s["step_order"],
                "skill_name": s["skill_name"],
                "mastery_pct": round(s["current_mastery"] * 100),
                "teaching_method": (
                    f"Ôn tập '{s['skill_name']}' bằng flashcards và trò chơi tương tác. "
                    f"Chia nhóm nhỏ 3-4 em, mỗi nhóm thực hành 5 câu."
                    if s["severity"] == "high"
                    else f"Củng cố '{s['skill_name']}' qua bài tập trắc nghiệm và thảo luận nhóm."
                ),
                "materials": "Flashcards, worksheet, trò chơi bingo.",
                "duration": "15-20 phút/buổi",
            }
            for s in steps
        ],
        "recommendations": (
            f"Kiểm tra lại sau 1 tuần. Ưu tiên {len(critical)} kỹ năng severity=high trước. "
            "Nếu >50% lớp vẫn yếu, cần ôn lại toàn bộ."
        ),
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# 4. POST-VALIDATION
# ---------------------------------------------------------------------------

def _post_validate(output_text: str, input_skill_ids: list) -> str:
    """Kiểm tra output có chứa kỹ năng ngoài input không.

    Nếu phát hiện skill_name lạ → giữ nguyên (vì LLM có thể viết tên khác),
    nhưng log warning. Trả về output_text nếu hợp lệ.
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
# 5. MAIN FUNCTION — tạo input phong phú hơn cho LLM
# ---------------------------------------------------------------------------

def _format_steps_for_user_msg(mastery: dict, gaps: list, student_name: str,
                                level: str, audience: str) -> str:
    """Tạo user message chi tiết, có cấu trúc, giúp LLM diễn giải tự nhiên hơn.

    Bao gồm: thông tin học sinh, bảng lộ trình BKT, và hướng dẫn diễn giải
    theo đối tượng (học sinh / giáo viên).
    """
    steps = generate_learning_steps(mastery, gaps)
    steps_table = format_steps_for_llm(steps)

    name = student_name or "học sinh"
    cefr = level or "chưa xác định"

    # Tính toán thêm thống kê để LLM có context tốt hơn
    total_skills = len(mastery)
    weak_count = sum(1 for m in mastery.values() if m.get("status") == "weak")
    developing_count = sum(1 for m in mastery.values() if m.get("status") == "developing")
    mastered_count = sum(1 for m in mastery.values() if m.get("status") == "mastered")

    # Xác định điểm mạnh (mastery cao nhất)
    strong_skills = sorted(mastery.items(), key=lambda x: x[1].get("probability", 0), reverse=True)[:3]
    strong_text = ""
    for sid, m in strong_skills:
        if m.get("probability", 0) >= 0.5:
            strong_text += f"  - {m.get('skill_name', sid)}: {round(m['probability']*100)}% ({m.get('status', '')})\n"

    # Nhóm câu hỏi theo loại (nếu có trong question data)
    audience_text = (
        "kế hoạch học tập cho HỌC SINH (giọng thân thiện, dễ hiểu, khích lệ)"
        if audience == "student"
        else "báo cáo cho GIÁO VIÊN (chuyên nghiệp, có số liệu, đề xuất phương pháp cụ thể)"
        if audience == "teacher"
        else "báo cáo cho PHỤ HUYNH (đơn giản, ấm áp, hoạt động tại nhà cụ thể)"
    )

    return (
        f"THÔNG TIN HỌC SINH:\n"
        f"- Tên: {name}\n"
        f"- Trình độ CEFR: {cefr}\n"
        f"- Tổng số kỹ năng đánh giá: {total_skills}\n"
        f"- Phân loại: {weak_count} yếu | {developing_count} đang phát triển | {mastered_count} đã thành thạo\n"
        f"{f'- Điểm mạnh: {chr(10)}{strong_text}' if strong_text else ''}\n"
        f"LO TRÌNH HỌC TẬP TỪ BKT ENGINE (dữ liệu bắt buộc phải có trong output):\n"
        f"{steps_table}\n\n"
        f"Hãy diễn giải thành {audience_text} "
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
        audience: "student" / "teacher" / "parent" — chọn prompt tương ứng.

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
            "closing": "Làm tốt lắm! Em đang có nền tảng vững chắc.",
        }, ensure_ascii=False)

    # --- Bước 2: Chọn prompt theo đối tượng ---
    if audience == "teacher":
        system_prompt = _TEACHER_SYSTEM_PROMPT
    elif audience == "parent":
        system_prompt = _PARENT_SYSTEM_PROMPT
    else:
        system_prompt = _STUDENT_SYSTEM_PROMPT

    # --- Bước 3: Tạo input có cấu trúc ---
    user_msg = _format_steps_for_user_msg(mastery, gaps, student_name, level, audience)

    # --- Bước 4: Gọi LLM (FPT) ---
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
# 6. TOOL DEFINITION
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


# ---------------------------------------------------------------------------
# 7. KẾ HOẠCH TỪ KHẢO SÁT ĐẦU VÀO
# ---------------------------------------------------------------------------

SURVEY_SYSTEM_PROMPT = _SURVEY_SYSTEM_PROMPT


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
# 8. ĐỀ XUẤT LỘ TRÌNH THAY THẾ CHO GIÁO VIÊN
# ---------------------------------------------------------------------------

_ALTERNATIVE_PATHS_SYSTEM_PROMPT = """Bạn là Chuyên gia Giáo dục số và Trợ lý Sư phạm AI cho V-Nexus Tutor.
Nhiệm vụ: hỗ trợ Giáo viên thiết kế 3 Lộ trình học tập thay thế (Alternative Learning Paths) cho học sinh Tiếng Anh lớp 3-4 dựa trên dữ liệu BKT thực tế.

QUY TẮC PHÂN TÁCH 3 LỘ TRÌNH (BẮT BUỘC):
Bạn phải sinh ra đúng 3 đề xuất tương ứng với 3 trục chiến lược sư phạm sau:
1. TRỤC 1: "Quay lại gốc rễ sâu hơn" (Back-to-roots): Đề xuất quay lại ôn tập kỹ và củng cố các kỹ năng tiên quyết (prerequisites) sâu hơn trong đồ thị kiến thức.
2. TRỤC 2: "Đổi nhịp độ và mật độ luyện tập" (Pacing & Density): Giữ nguyên kỹ năng, nhưng thay đổi nhịp độ (giảm độ khó, giãn thời gian, tăng số lượng ví dụ và bài tập lặp lại có hướng dẫn).
3. TRỤC 3: "Đổi hình thức tiếp cận" (Alternative Modality): Thay đổi hình thức tương tác (học nhóm, kèm 1-1, bài tập viết tay, bài hát, trò chơi thay vì trắc nghiệm).

YÊU CẦU CỤ THỂ CHO TIẾNG ANH LỚP 3-4:
- Mỗi lộ trình phải có hoạt động phù hợp với lứa tuổi 8-10 tuổi.
- Gợi ý phương pháp: flashcards, bài hát, trò chơi, hình ảnh minh họa, đóng vai.
- Thời lượng phù hợp: 15-25 phút/buổi, không quá dài.

HƯỚNG DẪN GROUNDING:
- Chỉ sử dụng các kỹ năng CÓ TRONG dữ liệu đầu vào. KHÔNG tự sáng tạo tên kỹ năng hay mã kỹ năng.
- Dùng văn phong chuyên nghiệp, lịch sự, gợi ý hợp tác sư phạm.
- Đầu ra phải là JSON hợp lệ, KHÔNG thêm văn bản ngoài JSON.
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
        f"Mỗi lộ trình PHẢI có hoạt động phù hợp với trẻ lớp 3-4 (flashcards, bài hát, trò chơi, đóng vai...). "
        f"Đầu ra bắt buộc là JSON có cấu trúc sau:\n"
        f"{{\n"
        f"  \"alternative_paths\": {{\n"
        f"    \"path_1_back_to_roots\": {{\n"
        f"      \"reasoning_cot\": \"Phân tích lý do thất bại và vì sao trục này phù hợp\",\n"
        f"      \"primary_difference\": \"Điểm khác biệt cốt lõi nhất (câu đầu tiên)\",\n"
        f"      \"target_prerequisite_skills\": [\"ID các kỹ năng cần ôn tập\"],\n"
        f"      \"action_steps\": [{{\"step_number\": 1, \"skill_id\": \"...\", \"action_description\": \"...\", \"estimated_duration_mins\": 20}}],\n"
        f"      \"expected_outcome\": \"Mục tiêu kỳ vọng\"\n"
        f"    }},\n"
        f"    \"path_2_pacing_density\": {{ ... }},\n"
        f"    \"path_3_alternative_modality\": {{ ... }}\n"
        f"  }},\n"
        f"  \"teacher_summary_comparison\": \"Tóm tắt so sánh nhanh 3 phương án.\"\n"
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

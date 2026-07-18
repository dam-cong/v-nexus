# Phân tích đề bài: Gia sư thích ứng thu hẹp khoảng cách năng lực trong lớp học

**Nhóm bài toán:** Giáo dục phổ thông — Adaptive Learning

> Đây là đề bài **thay thế** cho Đề 8 (Vbee — slide/giáo án thành video bài giảng).
> `docs/PHAN_TICH_DE_8.md` được giữ lại làm tài liệu tham khảo, không còn là đề đang
> theo đuổi.

## Đề bài (tóm tắt)

Vấn đề cấp bách nhất của giáo dục phổ thông Việt Nam không phải thiếu nội dung — mà là
**khoảng cách năng lực trong cùng một lớp học**, đặc biệt ở vùng khó khăn nơi 1 giáo
viên phải dạy lớp 40 học sinh với nền tảng rất khác nhau. Học sinh yếu bị bỏ lại phía
sau; học sinh giỏi bị kìm hãm. Các app học tập hiện có chỉ đẩy bài học theo thứ tự cố
định, không thực sự thích ứng, và bỏ qua vai trò giáo viên.

## Yêu cầu

- Chẩn đoán **tận gốc lỗ hổng kiến thức** của từng học sinh (vd: sai Toán lớp 7 vì hổng
  phân số từ lớp 5) — không chỉ chấm đúng/sai.
- Sinh **lộ trình luyện tập cá nhân hóa** nhắm đúng lỗ hổng đó.
- **Bắt buộc có dashboard giáo viên**: tự động nhóm học sinh theo nhu cầu, gợi ý ưu tiên
  hỗ trợ ai trước, phát hiện lỗ hổng chung của cả lớp để dạy lại.
- **Ràng buộc:** chạy được offline/mạng yếu; nội dung bám Chương trình GDPT 2018.

## Điểm khác với app học tập hiện có

Không "học theo thứ tự cố định" mà **chẩn đoán nguyên nhân gốc** xuyên suốt các
lớp/khối trước, và **giữ giáo viên làm trung tâm quyết định** — AI hỗ trợ ra quyết định,
không thay thế giáo viên.

## Thách thức kỹ thuật cốt lõi

1. **Sơ đồ tri thức tiên quyết** — mô hình hoá quan hệ phụ thuộc kỹ năng xuyên các
   lớp/khối theo GDPT 2018. Khó nhất, cần dựng trước (dù rút gọn 1 môn, 2–3 khối cho
   demo) để chẩn đoán có ý nghĩa.
2. **Chẩn đoán nguyên nhân gốc** — mỗi câu hỏi gắn nhãn kỹ năng tiên quyết; khi sai, lan
   truyền ngược qua đồ thị bằng **Bayesian Knowledge Tracing (BKT)** để suy ra kỹ năng
   tiên quyết có xác suất "chưa vững" cao nhất — xem chi tiết cơ chế ở mục
   [Áp dụng AI vào từng bước](#áp-dụng-ai-vào-từng-bước--và-vì-sao-không-chỉ-là-gọi-llm).
   LLM chỉ diễn giải kết quả thành câu giải thích tự nhiên, không tự suy đoán gap.
3. **Sinh lộ trình luyện tập** — chọn/sinh bài tập nhắm đúng kỹ năng thiếu, độ khó tăng
   dần, không ngẫu nhiên.
4. **Dashboard giáo viên** — nhóm học sinh theo gap tương đồng, xếp ưu tiên theo mức độ
   nghiêm trọng, phát hiện lỗi lặp lại ở tỷ lệ % học sinh cao trong lớp.
5. **Offline/mạng yếu** — ràng buộc khó nhất với kiến trúc dựa LLM cloud. Hướng xử lý:
   tách **soạn nội dung** (LLM, có mạng, làm trước, cache sẵn) khỏi **chấm & chẩn đoán
   lúc học** (chạy local, rule-based, không cần gọi LLM realtime); lưu local-first
   (SQLite/IndexedDB), đồng bộ khi có mạng.

## Giải pháp đề xuất

**Kiến trúc:** vẫn map vào khung V-NEXUS SCHOOL, nhưng vai trò LLM chuyển từ "runtime mọi
request" sang "soạn nội dung trước + hỗ trợ phân tích", do ràng buộc offline. Domain
Adapter mới: `domain/adaptive_tutor_adapter.py`.

- **Tool `diagnose_gap`**: cập nhật mastery probability từng skill bằng Bayesian
  Knowledge Tracing (prior từ CV, posterior từ kết quả bài làm), lan truyền ngược qua
  đồ thị tiên quyết để tìm skill gốc có xác suất "chưa vững" cao nhất — LLM chỉ dịch kết
  quả này thành câu giải thích, không tự suy đoán.
- **Tool `generate_practice_path`**: sinh danh sách bài tập nhắm đúng gap (ngân hàng câu
  hỏi soạn sẵn bằng LLM offline-batch, gắn nhãn kỹ năng, cache local).
- **Tool `teacher_dashboard_query`**: tổng hợp gap theo lớp — nhóm học sinh, xếp ưu
  tiên, phát hiện lỗ hổng chung.
- **Dữ liệu:** sơ đồ tri thức GDPT 2018 rút gọn (1 môn, 2–3 khối) + ngân hàng câu hỏi
  gắn nhãn kỹ năng.

**Nguồn nội dung — số hóa bài giảng giáo viên giỏi:** thay vì để LLM tự sinh nội dung
giảng dạy chung chung, ngân hàng học liệu ưu tiên **số hóa bài giảng thật của giáo viên
giỏi** (video/transcript có sẵn hoặc thu thập trong phạm vi demo) → LLM trích xuất, gắn
nhãn theo đúng kỹ năng trong sơ đồ tri thức → khi hệ thống chẩn đoán ra gap, ưu tiên gợi
ý đúng đoạn giảng của giáo viên giỏi khớp kỹ năng đó, thay vì bài tập tự sinh không có
ngữ cảnh sư phạm. Đây là cách đưa chất lượng giảng dạy đô thị/trường điểm tới học sinh
và giáo viên vùng sâu vùng xa — nơi thiếu giáo viên giỏi tại chỗ.

**Luồng chính (happy path):**
1. Học sinh làm bài kiểm tra chẩn đoán ngắn.
2. Hệ thống (local) đối chiếu sơ đồ tri thức → xác định gap gốc.
3. Sinh lộ trình luyện tập nhắm đúng gap, độ khó tăng dần.
4. Học sinh luyện tập offline; dữ liệu đồng bộ khi có mạng.
5. Giáo viên xem dashboard: nhóm học sinh theo gap, gợi ý ưu tiên, cảnh báo lỗ hổng
   chung của lớp.

## Input & Output

> **Cập nhật phạm vi:** chuyển từ demo Toán 6–7 (GDPT 2018 quốc gia) sang **môn Tiếng
> Anh**, mở rộng input sang bài kiểm tra đầu vào + hồ sơ học viên (CV) + chương trình
> **cấp 1-2-3 của một trường cụ thể** (khác GDPT 2018 chuẩn quốc gia — đây là chương
> trình riêng, có thể khác nhau giữa các trường). Xem ghi chú về ảnh hưởng tới phạm vi
> MVP ở cuối mục này.

### Ở cấp hệ thống

**Input**
1. Môn học: **Tiếng Anh**.
2. Bài kiểm tra đầu vào (placement test) — đọc/nghe/viết, có thể cả nói nếu có ASR.
3. Thông tin học viên (CV) — lịch sử học tập, số năm học tiếng Anh, môi trường học
   (trường/trung tâm), tự đánh giá, mục tiêu học.
4. Chương trình Tiếng Anh cấp 1-2-3 **của trường** — toàn bộ khung chương trình Tiểu
   học → THCS → THPT theo tài liệu riêng của trường đó.

**Output**
- **Dashboard học sinh:** level hiện tại (quy đổi theo khung năng lực chuẩn, vd CEFR
  hoặc khung 6 bậc VN) + lộ trình phát triển cá nhân hóa theo thời gian.
- **Dashboard giáo viên:** tổng quan lớp — phân bố trình độ, gap phổ biến, học sinh cần
  ưu tiên, gợi ý nội dung dạy lại.
- **Dashboard phụ huynh:** tiến độ của riêng con theo thời gian (không thuật ngữ kỹ
  thuật, không so sánh với học sinh khác), gợi ý cụ thể có thể hỗ trợ tại nhà, cảnh báo
  nhẹ khi con kẹt lâu ở một kỹ năng.

### Áp dụng AI vào từng bước — và vì sao không chỉ là "gọi LLM"

Rủi ro: nếu mỗi bước đều là "LLM làm hộ", đội không có gì khác biệt với các đội chỉ bọc
prompt quanh GPT — giám khảo chấm tiêu chí *Kiến trúc AI-Native & Đổi mới sáng tạo*
(20đ) sẽ thấy ngay. Điểm khác biệt thật sự phải nằm ở **một cơ chế suy luận tường minh,
giải thích được**, còn LLM chỉ đứng ở 2 đầu (input thô → dữ liệu có cấu trúc, và kết quả
suy luận → ngôn ngữ tự nhiên) — không phải bộ não chẩn đoán.

**Cơ chế lõi — không phải LLM, mà là mô hình xác suất trên đồ thị tri thức:**

1. **Bayesian Knowledge Tracing (BKT) trên đồ thị tiên quyết.** Mỗi skill node có một
   xác suất "đã nắm vững" (mastery probability). Mỗi câu trả lời đúng/sai cập nhật xác
   suất này theo công thức Bayes chuẩn (P(mastery | evidence)). Khi một skill liên tục
   sai dù đã thử nhiều lần, xác suất mastery của **skill tiên quyết** (cha trong đồ thị)
   bị hạ theo — đây chính là "truy gốc", nhưng bằng công thức xác suất tường minh, có
   thể in ra từng bước suy luận, không phải "LLM đoán".
2. **Kết hợp CV + bài test bằng Bayesian prior/posterior**, không phải "đưa cả hai vào
   prompt rồi để LLM tự cân nhắc". CV (tự báo cáo, số năm học) cho ra **prior** — xác
   suất mastery ban đầu trước khi làm bài. Bài kiểm tra là **evidence** cập nhật prior
   thành **posterior** theo đúng lý thuyết xác suất. Cách này giải thích được: "vì sao
   hệ thống tin học sinh ở mức A2" luôn có thể truy ngược về con số cụ thể.
3. **Kiểm tra đầu vào thích ứng (adaptive testing), không phải bộ đề cố định.** Sau mỗi
   câu, chọn câu tiếp theo nhắm vào skill có **độ bất định cao nhất** (entropy cao nhất
   trong phân phối mastery) — giống cơ chế CAT (Computerized Adaptive Testing) dùng
   trong TOEFL/GRE. Kết quả: bài test ngắn hơn nhưng chẩn đoán chính xác hơn — một con
   số đo lường được để khoe trong pitch ("giảm X% số câu hỏi so với đề cố định").

**LLM chỉ giữ 3 vai trò biên (input/output layer, không phải reasoning layer):**

| Vai trò LLM | Input | Output |
|---|---|---|
| Trích xuất có cấu trúc | Chương trình nhà trường (PDF/Word), CV học viên (text tự do) | Skill graph có nhãn, hồ sơ ngữ cảnh học viên (structured) |
| Chấm phần chủ quan | Bài viết/tự luận, audio nói (qua STT) | Điểm + nhận xét lỗi cụ thể theo rubric — nơi LLM thực sự vượt trội rule-based |
| Diễn giải kết quả suy luận | Mastery probability + gap graph từ BKT | Câu giải thích tự nhiên cho giáo viên/học sinh, lộ trình phát triển dạng văn bản |
| Diễn giải cho phụ huynh (tông khác) | Mastery probability + lịch sử luyện tập của 1 học sinh | Tóm tắt tiến độ bằng ngôn ngữ không kỹ thuật + 1 gợi ý hành động cụ thể tại nhà — cùng dữ liệu với dòng trên nhưng **tông giọng và mức chi tiết khác hẳn** (không heatmap, không thuật ngữ) |

**Nếu còn thời gian (stretch, không bắt buộc cho MVP):** content bandit đơn giản
(epsilon-greedy) — theo dõi học sinh có cải thiện sau khi luyện với 1 đoạn giảng cụ thể
không (re-test), ưu tiên dần nội dung thực sự hiệu quả. Biến hệ thống thành "học máy
liên tục cải thiện" thay vì retrieval tĩnh — nhưng chỉ làm nếu 5 mục trên đã chạy ổn.

> ⚠️ **Cần bạn xác nhận:** phạm vi này (Tiếng Anh, K-12 toàn trường, CV + placement
> test + 4 kỹ năng) rộng hơn nhiều so với demo Toán 6–7/1 mạch kiến thức đã chốt trước
> đó trong `docs/PROJECT_DESCRIPTION.md` và `docs/timeline.md`. Với 48 giờ, nên **giữ
> kiến trúc tổng quát này nhưng thu hẹp demo thật** (vd: 1 khối lớp, bỏ qua chấm nói/ASR,
> CV parsing đơn giản hoá thành form có cấu trúc thay vì tự do) — tương tự cách đã thu
> hẹp mạch Toán trước đây. Cần cập nhật lại `PROJECT_DESCRIPTION.md` mục 4 và
> `timeline.md` (phần việc của Ngọc/Hiếu) nếu đây là hướng chính thức thay Toán.

### Ở cấp tool (cho Hiếu/Quyết triển khai)

| Tool | Input | Output |
|---|---|---|
| `diagnose_gap` | `student_id`; danh sách `(question_id, answer, đúng/sai)` của bài kiểm tra chẩn đoán; đồ thị tri thức | Danh sách gap đã xếp hạng: `(skill_id, tên kỹ năng, độ tin cậy, khối lớp gốc)` + câu giải thích ("Em sai vì hổng quy đồng phân số từ lớp 5") |
| `generate_practice_path` | `student_id`; danh sách gap (từ `diagnose_gap`); ngân hàng câu hỏi đã gắn nhãn kỹ năng | Danh sách bài tập theo thứ tự: `(question_id, skill_id, độ khó)`, sắp từ gap sâu nhất lên |
| `teacher_dashboard_query` | `class_id`; danh sách `(student_id, gap_map)` của cả lớp | Heatmap `skill_id → % học sinh hổng`; nhóm học sinh theo gap tương đồng; bảng xếp hạng ưu tiên `(student_id, priority_score)`; cảnh báo lỗ hổng diện rộng |
| `parent_dashboard_query` | `student_id` (1 con, không phải cả lớp); lịch sử mastery probability theo thời gian; `parent_id` để xác thực quyền xem | Tiến độ theo thời gian dạng đơn giản (vd biểu đồ tăng trưởng, không phải bảng số); 1 gợi ý hành động cụ thể tại nhà; cờ cảnh báo nếu kẹt >N ngày ở cùng 1 skill — **không trả về dữ liệu học sinh khác** (khác `teacher_dashboard_query` về phạm vi truy cập) |

## Bot hỏi-đáp cho học sinh & giáo viên

Bổ sung: một bot hội thoại để học sinh/giáo viên **hỏi trực tiếp bằng ngôn ngữ tự
nhiên** thay vì chỉ nhìn dashboard tĩnh — "tại sao em sai câu này?", "em nên học gì tiếp
theo?", "học sinh nào lớp tôi cần giúp nhất tuần này?".

**Đây chính là vai trò của khung kỹ thuật đã dựng sẵn từ đầu** — Gateway + Planner Agent
+ Tool Registry (`agent/`, `tools/`, `gateway/`) — chưa dùng tới từ khi pivot sang bài
toán chẩn đoán. Bot không phải component mới, mà là **giao diện hội thoại đặt trên cùng
4 tool đã có** (`diagnose_gap`, `generate_practice_path`, `teacher_dashboard_query`,
`parent_dashboard_query`):

1. Người dùng hỏi bằng tiếng Việt tự nhiên.
2. Planner Agent (LLM) hiểu câu hỏi → chọn đúng tool cần gọi → gọi tool lấy dữ liệu
   thật (đã tính bằng BKT, không phải LLM tự nhớ/đoán).
3. LLM chỉ diễn giải **kết quả tool trả về** thành câu trả lời — đúng vai trò biên đã
   thiết kế ở trên, không phải nguồn trả lời.
4. **Nếu câu hỏi không map được vào tool nào** (không đủ dữ liệu để trả lời), bot phải
   trả lời "chưa có đủ thông tin để trả lời câu này" — **không được bịa**. Đây là ranh
   giới quan trọng nhất cho tiêu chí An toàn AI, Grounding & Độ tin cậy.

**Access control theo vai trò** (bắt buộc, không phải tuỳ chọn):
- Bot cho học sinh: chỉ gọi tool với `student_id` = chính học sinh đang chat — không
  bao giờ trả lời câu hỏi về học sinh khác, kể cả khi được hỏi trực tiếp.
- Bot cho giáo viên: chỉ gọi tool với `class_id` thuộc lớp giáo viên đó phụ trách.
- Nguyên tắc giống hệt `parent_dashboard_query` đã thiết kế — mở rộng thêm 1 lớp kiểm
  tra quyền ở tầng Planner Agent trước khi gọi tool, không tin tưởng input từ prompt.

**Lưu ý về ràng buộc offline:** bot cần gọi LLM realtime nên **không chạy offline** như
phần chẩn đoán/luyện tập cốt lõi — đây là lớp tính năng "khi có mạng", không phải phần
bắt buộc phải hoạt động ở vùng mất kết nối. Nên nói rõ ranh giới này khi pitch để không
mâu thuẫn với cam kết offline-first.

### Dữ liệu nền (chuẩn bị trước, input tĩnh)

- **Đồ thị tri thức:** node = kỹ năng (mã bài học GDPT 2018 + tên), edge = quan hệ tiên
  quyết (kỹ năng A cần trước kỹ năng B).
- **Ngân hàng câu hỏi:** `(question_id, skill_id, nội dung, đáp án đúng, độ khó, nguồn)`
  — nguồn ưu tiên số hóa từ giáo viên giỏi, bổ sung bằng AI soạn khi thiếu.

## MVP 48 giờ

**Phải có (đây là phần tạo khác biệt, ưu tiên số 1):** đồ thị tri thức rút gọn (1 môn, 2
khối liền kề) + **engine BKT thật** (cập nhật mastery probability + lan truyền ngược qua
đồ thị) + bài kiểm tra chẩn đoán ngắn + dashboard giáo viên cơ bản (danh sách học sinh +
gap + nhóm). BKT là phần bắt buộc — bỏ phần này thì hệ thống quay lại thành "app chấm
đúng/sai + LLM" như mọi đội khác.

**Nên có (rẻ, tận dụng lại dữ liệu trên):** dashboard phụ huynh — chỉ là 1 view khác của
cùng `gap_map` đã tính cho `teacher_dashboard_query`, lọc còn 1 học sinh + đổi tông ngôn
ngữ qua LLM. Không cần thêm logic chẩn đoán mới, chi phí thấp so với giá trị demo (3
dashboard cho 3 đối tượng là điểm cộng UX rõ rệt).

**Có thể bỏ nếu thiếu giờ (theo thứ tự cắt giảm):** content bandit (stretch, không phải
MVP) → adaptive testing/CAT (có thể dùng bộ đề cố định thay thế, chỉ nói hướng mở rộng
trong pitch) → CV parsing tự do (dùng form có cấu trúc thay vì LLM trích xuất) → chấm
nói/ASR → đồng bộ offline đầy đủ (demo local-only, nêu hướng mở rộng) → nhiều môn học.

## Business case

Người trả tiền tiềm năng: Sở/Phòng GD&ĐT (chương trình hỗ trợ vùng khó khăn), trường học
(gói theo lớp/giáo viên), hoặc tổ chức giáo dục phi lợi nhuận tài trợ. Pilot đầu tiên:
1 lớp thật ở vùng khó khăn, đo mức độ thu hẹp khoảng cách qua bài kiểm tra trước/sau.

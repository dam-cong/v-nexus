# Kế hoạch triển khai — Phase 1 (BKT engine + chẩn đoán + dashboard giáo viên/phụ huynh)

Kế hoạch cho **Hiếu (AI)** và **Quyết (Dev)** bắt tay code ngay. Xem bối cảnh đầy đủ ở
[docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md) và
[docs/PROJECT_DESCRIPTION.md](PROJECT_DESCRIPTION.md).

## Bối cảnh

Khung scaffold hiện tại (`gateway/`, `agent/`, `tools/`, `domain/`, `db/`,
`frontend/streamlit_app.py`) được dựng generic từ trước khi có đề bài thật — vẫn đang
dùng `SMEInnovationAdapter` placeholder với 1 tool echo, **chưa có logic gia sư thích
ứng nào**. Đây là kế hoạch thay placeholder đó bằng hệ thống thật.

Cốt lõi khác biệt (đã chốt ở tài liệu phân tích): chẩn đoán nguyên nhân gốc chạy trên
**Bayesian Knowledge Tracing (BKT) tường minh trên đồ thị tiên quyết** — không phải LLM
đoán. LLM chỉ giữ 3 vai trò biên (trích xuất, chấm chủ quan, diễn giải ngôn ngữ tự
nhiên).

**2 quyết định đã chốt:**
- **Frontend giữ Streamlit cho bản demo**; PWA offline thật là roadmap sau, không phải
  Phase 1. Backend là REST/JSON thuần nên frontend nào gọi cũng được, không cần đổi khi
  quyết định frontend thay đổi sau.
- **Phạm vi chỉ Phase 1 MVP**: BKT engine + đồ thị tri thức + bài kiểm tra chẩn đoán +
  dashboard giáo viên + dashboard phụ huynh. Gamification, chấm phát âm/ASR, dashboard
  nhà trường, AI soạn nhận xét, CAT/adaptive testing, bot hỏi-đáp — **hoãn lại**, có ghi
  chú chỗ nối vào sau nhưng không code trong phase này.

### Định hướng thiết kế UI (tham khảo, chưa chốt style/thư viện)

Bạn đã chia sẻ 2 ảnh tham khảo: dashboard kiểu Shadcn "Academy" (thẻ chào mừng + minh
họa, progress bar lộ trình học, leaderboard, stat card, donut chart — tối giản đen
trắng + cam/xanh) và template "Akademi" (thanh top tím/indigo, hàng stat-icon nhiều màu,
biểu đồ xu hướng line+bar, lịch, bảng dữ liệu có avatar + badge trạng thái, sidebar hoạt
động). Không đổi quyết định stack ở trên — chỉ ghi lại **pattern** nên áp dụng khi làm
UI thật (Streamlit custom CSS hoặc PWA sau này):

- **Dashboard giáo viên** → hàng stat-icon (sĩ số lớp, mastery trung bình, số học sinh
  cần chú ý) + heatmap dạng lưới màu/bar-chart (skill × % hổng) + bảng xếp hạng ưu tiên
  (avatar, tên học sinh, skill gốc, số ngày kẹt, badge trạng thái) — giống pattern
  "Teacher Details" ở ảnh Akademi.
- **Dashboard phụ huynh** → biểu đồ đường tiến độ theo thời gian của 1 con (giống
  "School Performance") + 1 thẻ gợi ý nổi bật (giống thẻ chào mừng) — **không phải bảng
  dữ liệu** (không so sánh chéo học sinh, đúng thiết kế privacy đã chốt).
- **Giao diện học sinh** → progress bar theo từng kỹ năng (giống "Learning Path"), không
  hiển thị con số xác suất thô.

Chưa chốt màu sắc/thư viện cụ thể — quyết định lại khi chốt Streamlit-vs-PWA.

## Cách triển khai

Build từ dưới lên: dữ liệu đồ thị tĩnh → schema DB → BKT thuần (test được độc lập) →
lớp lưu trữ mastery → tools → domain adapter → REST routes → tests. Mọi tool chấm điểm
**ở server**, không tin `is_correct` từ LLM/client. `parent_dashboard_query` tự kiểm tra
`student.parent_id == parent_id` ngay trong hàm — không dựa vào prompt.

### 1. Đồ thị tri thức — `domain/data/knowledge_graph.json` (mới)

DAG 8 kỹ năng, Tiếng Anh lớp 3 Unit 5, 4 tầng sâu để truy gốc có ý nghĩa:

| code | tên | loại | tiên quyết của |
|---|---|---|---|
| `TA3.PRE.PHONICS01` | Nhận biết & phát âm bảng chữ cái | phonics | → VOCAB_TOYS |
| `TA3.PRE.NUM0110` | Đếm số 1–10 | vocab | → GRAM_HOWMANY |
| `TA3.PRE.NOUN_PLURAL` | Quy tắc số nhiều (-s/-es) | grammar | → VOCAB_TOYS_PLURAL, GRAM_HOWMANY |
| `TA3.U5.VOCAB_TOYS` | Từ vựng Toys (ball, doll, kite...) | vocab | → VOCAB_TOYS_PLURAL |
| `TA3.U5.VOCAB_TOYS_PLURAL` | Số nhiều Toys (balls, dolls...) | vocab | → GRAM_HOWMANY |
| `TA3.U5.GRAM_HOWMANY` | "How many + plural noun + are there?" | grammar | → LISTEN, SPEAK |
| `TA3.U5.LISTEN_HOWMANY` | Nghe hiểu hỏi-đáp số lượng | listening | (leaf) |
| `TA3.U5.SPEAK_HOWMANY` | Hỏi-đáp số lượng (text dialogue, chưa ASR) | speaking | (leaf) |

Mã kỹ năng là placeholder — Ngọc (BA)/Dũng (cố vấn) cần đối chiếu GDPT 2018 thật trước
demo; sửa JSON không cần sửa code. Mỗi skill có tham số BKT mặc định:
`p_init=0.4, p_transit=0.1, p_slip=0.1, p_guess=0.2`.

Thêm `domain/data/question_bank.json` — ~15–20 câu hỏi gắn nhãn skill, độ khó 1–5,
`question_type` ∈ {mcq, fill_blank, listening, dialogue}.

### 2. Schema DB — `db/models.py` (mở rộng, giữ `ChatLog` cũ)

Bảng mới: `Skill`, `SkillPrerequisite`, `Question`, `Teacher`, `ClassRoom`, `Parent`,
`Student` (FK class_room, FK parent nullable), `StudentResponse` (log tương tác:
student/question/skill FK, `is_correct`, `session_type` diagnostic|practice,
`p_mastery_before/after`, timestamp), `StudentSkillMastery` (cache trạng thái hiện tại:
student/skill FK unique, `p_mastery`, `attempts`, `correct_count`, `stuck_since`
nullable — set khi mastery lần đầu tụt dưới ngưỡng, xóa khi hồi phục, dùng cho cờ "kẹt >
N ngày" ở dashboard phụ huynh).

`StudentResponse` phục vụ cả replay BKT lẫn "tiến độ theo thời gian"; `StudentSkillMastery`
là cache đọc nhanh. Thêm `db/seed.py` — loader idempotent (upsert theo `code`): JSON → DB
+ 1 lớp/giáo viên/học sinh mẫu.

### 3. BKT engine — `domain/bkt.py` (thuần, không DB/async — lõi test được độc lập)

Công thức Corbett & Anderson chuẩn, `bayes_update(p_prior, is_correct, p_slip, p_guess,
p_transit) -> float`:

```
p_evidence = đúng: (p_prior·(1-p_slip)) / (p_prior·(1-p_slip) + (1-p_prior)·p_guess)
             sai:  (p_prior·p_slip)     / (p_prior·p_slip     + (1-p_prior)·(1-p_guess))
p_posterior = p_evidence + (1 - p_evidence) · p_transit
```

Lan truyền ngược (`propagate_to_prerequisites`) là heuristic giải thích được, không phải
mạng Bayes đầy đủ (chủ động thu gọn phạm vi cho 48h): chỉ kích hoạt sau ≥2 lần thử trên 1
skill có `p_mastery < 0.5`, áp update kiểu "như thể sai" lên từng tiên quyết, nhân hệ số
`evidence_strength × 0.6^depth`, giới hạn depth 3, trả về `trace` dạng
`{skill_id, from, to, reason_skill, depth}` — chính `trace` này là câu giải thích "Em sai
vì hổng X" in ra được, không phải LLM đoán. `find_root_gaps` trả về skill hổng sâu nhất
mà tiên quyết của nó không hổng (frontier của subgraph đang fail).

Module đi kèm: `domain/knowledge_graph.py` (load JSON + `prerequisites_of`/
`dependents_of`/`depth`, kiểm tra acyclic), `domain/mastery_store.py` (wrapper DB gọi
vào `bkt.py`, đọc/ghi `StudentSkillMastery`/`StudentResponse`),
`domain/practice_selector.py` (logic sắp xếp `generate_practice_path`),
`domain/dashboard_queries.py` (heatmap/gom nhóm/xếp ưu tiên giáo viên + timeline/cờ kẹt
phụ huynh).

### 4. Tools — `tools/adaptive_tutor_tools.py` (mới)

4 `Tool` instance (theo dataclass ở `tools/base.py`), mỗi tool tự mở `AsyncSession`
riêng (registry chỉ truyền JSON args từ LLM, không có điểm inject session):

- **`diagnose_gap`** — chấm câu trả lời ở server theo `Question.correct_answer`, chạy
  `bayes_update` + lan truyền có điều kiện cho từng câu, lưu DB, trả gap đã xếp hạng kèm
  giải thích từ propagation trace.
- **`generate_practice_path`** — đi từ gap gốc sâu nhất lên qua `dependents_of`, lấy câu
  hỏi theo skill sắp theo độ khó, giới hạn N câu.
- **`teacher_dashboard_query`** — heatmap (`skill_code → % học sinh dưới ngưỡng`), gom
  nhóm học sinh theo root-gap chung, xếp ưu tiên, cảnh báo lớp (≥40% hổng 1 skill).
- **`parent_dashboard_query`** — **kiểm tra `student.parent_id == parent_id` trước
  tiên**, trả access-denied không kèm dữ liệu nếu sai; dựng timeline tiến độ + cờ kẹt +
  1 gợi ý hoạt động tại nhà theo template cố định (tra bảng theo skill_type yếu nhất,
  không gọi LLM — giữ dashboard này rẻ, đúng tinh thần "LLM diễn giải chỉ là lớp online
  cộng thêm" đã ghi trong tài liệu phân tích).

### 5. `domain/adaptive_tutor_adapter.py` (mới, thay `sme_innovation_adapter.py`)

Implement `DomainAdapter`: `tools()` trả về 4 tool trên; `system_prompt()` nêu rõ quy
tắc grounding (chỉ trả lời từ kết quả tool, nói "chưa có đủ thông tin" nếu tool không
đủ dữ liệu — không tự bịa gap) và quy tắc truy cập (chỉ truy vấn đúng id người đang hỏi).

**Lưu ý, chủ động hoãn, chưa giải quyết ở đây**: `gateway/app/routes/chat.py` dựng 1
`PlannerAgent` chung cho cả process, chưa gắn identity theo từng request — nên access
control ở tầng prompt cho *bot/chat* chưa phải rào chắn bảo mật thật. Chấp nhận hoãn vì
bề mặt sản phẩm thật của Phase 1 là REST dashboard bên dưới, vốn đã enforce access
control bằng code, độc lập với LLM.

### 6. Gateway REST routes (routers mới trong `gateway/app/routes/`)

`diagnostic.py` (`GET /diagnostic/questions`, `POST /diagnostic/submit-answer`,
`POST /diagnostic/complete`), `practice.py` (`GET /practice/path`,
`POST /practice/submit-answer`), `teacher.py` (`GET /teacher/dashboard/{class_id}`),
`parent.py` (`GET /parent/dashboard/{student_id}?parent_id=...`) — JSON thuần qua
Pydantic, đăng ký ở `gateway/app/main.py`. `gateway/app/routes/chat.py` trỏ sang
`AdaptiveTutorAdapter` thay vì `SMEInnovationAdapter`.

### Chỗ nối cho phần hoãn lại (không code phase này)

- **CAT/adaptive testing**: thay bộ câu hỏi cố định ở `/diagnostic/questions` bằng chọn
  câu tiếp theo theo entropy trong `practice_selector.py`.
- **Chấm phát âm/ASR**: thêm nhánh chấm cho `question_type=speaking` gọi ASR thay vì so
  khớp chính xác; skill `SPEAK_HOWMANY` đã có sẵn trong đồ thị.
- **Gamification, dashboard nhà trường, AI soạn nhận xét, bot hỏi-đáp**: cộng thêm — bot
  tái dùng `PlannerAgent`/`ToolRegistry` sẵn có (đã thiết kế ở mục "Bot hỏi-đáp" trong
  tài liệu phân tích); các phần còn lại là bảng/tool mới đặt trên cùng schema
  `Student`/`ClassRoom`/`StudentSkillMastery`.

## Danh sách file

- `domain/data/knowledge_graph.json`, `domain/data/question_bank.json` — dữ liệu mới
- `db/models.py` — thêm 8 bảng mới nêu trên
- `db/seed.py` — loader idempotent mới
- `domain/knowledge_graph.py`, `domain/bkt.py`, `domain/mastery_store.py`,
  `domain/practice_selector.py`, `domain/dashboard_queries.py` — mới, theo đúng thứ tự
  phụ thuộc này
- `tools/adaptive_tutor_tools.py` — mới, gắn 4 tool
- `domain/adaptive_tutor_adapter.py` — mới, thay `domain/sme_innovation_adapter.py`
- `gateway/app/routes/diagnostic.py`, `practice.py`, `teacher.py`, `parent.py` — mới
- `gateway/app/routes/chat.py`, `gateway/app/main.py` — sửa để gắn adapter/router mới

## Kiểm thử

- `pytest tests/test_bkt.py` — test toán thuần: trả lời đúng tăng mastery, sai giảm
  mastery, giá trị luôn trong [0,1], 10 lần đúng liên tiếp hội tụ về gần mastered, 1 lần
  sai KHÔNG lan truyền (attempts < 2), 3 lần sai liên tiếp CÓ lan truyền tới tiên quyết,
  lan truyền giảm dần theo depth, và `find_root_gaps` trên chuỗi 3 node đồ chơi trả về
  tổ tiên hổng sâu nhất, không phải leaf.
- `pytest tests/test_knowledge_graph.py` — đồ thị load đúng số node/edge kỳ vọng,
  `prerequisites_of` trả đúng cha, loader từ chối cycle.
- `pytest tests/test_dashboard_endpoints.py` (FastAPI `TestClient`, theo pattern
  `tests/test_gateway_health.py` sẵn có) — dashboard phụ huynh từ chối `parent_id` sai,
  không lộ dữ liệu; dashboard giáo viên heatmap/xếp hạng khớp fixture đã seed;
  submit-answer chẩn đoán end-to-end cập nhật đúng mastery trong DB.
- Thủ công: `docker compose up --build`, chạy `db/seed.py` trong container gateway, gọi
  `POST /diagnostic/submit-answer` vài lần cho 1 học sinh mẫu với câu trả lời sai cố ý ở
  `LISTEN_HOWMANY`, xác nhận qua `GET /teacher/dashboard/{class_id}` rằng mastery của
  `GRAM_HOWMANY`/`NOUN_PLURAL` cũng tụt theo (lan truyền hoạt động) và trace giải thích
  đọc mạch lạc bằng tiếng Việt.

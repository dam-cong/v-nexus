# Plan chi tiết — Adaptive Tutoring (V-Nexus, VAIC 2026)

> Kế thừa toàn bộ cấu trúc Phase/File của plan gốc (giữ nguyên các quyết định kỹ thuật đã đúng), bổ sung: mốc giờ cụ thể theo khung 48h, thứ tự phụ thuộc rõ ràng, xử lý lỗi/fallback, đồng bộ docs, và checklist AI_LOG song song.

## 0. Việc làm NGAY, trước Phase 1 (không tính vào 48h kỹ thuật)

- [ ] **Xác nhận đề bài chính thức BTC công bố 11:00 17/7 đúng là Adaptive Tutoring/giáo dục.**
- [ ] Cập nhật `README.md` (mục chủ đề) và `docs/PROJECT_DESCRIPTION.md` (mục 1: Tên dự án & chủ đề) — đổi từ "SME innovation" sang chủ đề thật, để hồ sơ nộp khớp sản phẩm.
- [ ] Điền bảng Team trong `docs/PROJECT_DESCRIPTION.md` mục 9 (tên, vai trò, phụ trách) — cần cho tính hợp lệ đội thi.
- [ ] Phân công người phụ trách `ai/knowledge_graph.json` (cần người hiểu chương trình môn học, không nhất thiết là Dev).

---

## 1. Nguyên tắc xuyên suốt (giữ nguyên từ plan gốc, nhấn mạnh lại)

- **Lõi AI khác biệt = BKT Engine (Bayesian, không phải LLM)** — đây là điểm phân biệt #1 với các đội khác, ưu tiên tuyệt đối, làm trước mọi thứ.
- **Chỉ 1 Planner Agent** — mọi tool mới là hàm thuần/engine, không tạo agent thứ 2.
- **Chỉ thay `domain/`** khi nối vào hệ thống — không sửa `agent/`, `tools/registry.py`, `gateway/app/main.py`, `mcp_server/` (trừ `chat.py` đổi adapter, đã nằm trong kế hoạch).
- **Ghi `docs/AI_LOG.md` ngay sau mỗi file được AI tạo/sửa** — không dồn cuối. Checklist AI_LOG được nhắc lại ở cuối mỗi Phase bên dưới.
- **Grounding**: mọi câu trả lời quan trọng phải dựa vào tool/DB, không để LLM tự bịa số liệu mastery/gap.

---

## 2. Cấu trúc file (giữ nguyên từ plan gốc)

```
ai/
├── __init__.py
├── knowledge_graph.py        # KnowledgeGraph class
├── bkt_engine.py              # BKTEngine class
├── input_extractor.py         # LLM input layer (stretch)
├── output_interpreter.py      # LLM output layer
├── adaptive_test.py           # CAT engine (stretch)
├── knowledge_graph.json       # Dữ liệu đồ thị mẫu
└── prompts/
    ├── system.md
    ├── diagnose_explain.md
    ├── parent_explain.md
    └── teacher_explain.md

tools/
├── diagnose_gap.py
├── generate_practice_path.py
├── teacher_dashboard_query.py
├── parent_dashboard_query.py
└── question_bank.py

domain/
└── adaptive_tutor_adapter.py  # thay sme_innovation_adapter.py

db/
├── models.py                  # bổ sung Student, Skill, StudentSkillMastery, Answer, Question, Class, Parent
└── seed_data.py               # NEW

gateway/app/routes/
├── chat.py                    # sửa: đổi adapter, thêm role vào ChatRequest
└── diagnose.py                # NEW (stretch)

tests/
├── test_bkt_engine.py
├── test_tools.py
└── test_integration.py        # NEW
```

---

## 3. Phase chi tiết

### Phase 1 — Knowledge Graph + BKT Engine (lõi AI, KHÔNG phải LLM)

| # | File | Mô tả | Phụ thuộc |
|---|---|---|---|
| 1.0 | `ai/knowledge_graph.json` | Đồ thị mẫu 20–30 node (VD: Phân số → Phương trình, Toán 6–7), có mã GDPT 2018. **Làm trước mọi code**, để có dữ liệu test ngay. | Không phụ thuộc gì |
| 1.1 | `ai/knowledge_graph.py` | `KnowledgeGraph`: load JSON/YAML. Methods: `get_prerequisites(skill_id)`, `get_dependents(skill_id)`, `traverse_up(skill_id)`. **Fallback bắt buộc**: nếu `skill_id` không tồn tại trong graph → raise `SkillNotFoundError` rõ ràng, không fail âm thầm. | 1.0 |
| 1.2 | `ai/bkt_engine.py` | `BKTEngine`: `update(student_id, skill_id, correct) -> mastery_prob`; `diagnose_root_cause(student_id, wrong_skill_id) -> list[GapResult]` (lan truyền ngược qua graph). **Fallback bắt buộc**: nếu không có prior (học sinh mới) → dùng prior mặc định có ghi log rõ "đang dùng giá trị mặc định", không trả `None`/crash. | 1.1 |
| 1.3 | `tests/test_bkt_engine.py` | Test: cập nhật mastery đúng công thức, lan truyền ngược đúng, và **test case lỗi**: skill không tồn tại, học sinh chưa có dữ liệu. | 1.1, 1.2 |

**Checklist cuối Phase 1:**
- [ ] Ghi vào `AI_LOG.md`: 4 dòng tương ứng 1.0–1.3, có ghi rõ nếu sửa lại đề xuất AI.
- [ ] Chạy `pytest tests/test_bkt_engine.py` pass 100%.

---

### Phase 2 — 4 Tools (nối vào Tool Registry)

| # | File | Mô tả | Phụ thuộc |
|---|---|---|---|
| 2.1 | `tools/diagnose_gap.py` | **Tool quan trọng nhất.** Input: `student_id, answers[]`. Gọi `BKTEngine.diagnose_root_cause()`. Output: `list[(skill_id, name, confidence, grade, explanation)]`. **Fallback bắt buộc**: nếu `answers[]` rỗng hoặc BKT không tìm ra gap → trả message rõ ràng ("chưa đủ dữ liệu để chẩn đoán"), không để LLM tự suy diễn thay. | Phase 1 |
| 2.2 | `tools/question_bank.py` | `QuestionBank`: `get_by_skill(skill_id, difficulty) -> list[Question]`. **Nguồn dữ liệu câu hỏi**: (a) ưu tiên seed tay 30–50 câu cho các skill trong `knowledge_graph.json` (đủ demo); (b) nếu còn giờ, dùng LLM sinh thêm câu hỏi theo skill + độ khó (ghi rõ đây cũng là 1 điểm AI-native, gộp cùng Phase 4). Làm **trước** 2.3 vì 2.3 phụ thuộc nó. | Phase 1 |
| 2.3 | `tools/generate_practice_path.py` | Input: `student_id, gaps[]`. Chọn câu hỏi theo skill gap, độ khó tăng dần. Output: `[(question_id, skill_id, difficulty)]`. **Fallback**: nếu `QuestionBank` không có câu hỏi cho skill gap → fallback sang skill tiên quyết gần nhất (dùng `get_prerequisites`), không trả rỗng. | 2.2 |
| 2.4 | `tools/teacher_dashboard_query.py` | Input: `class_id`. Output: heatmap `skill_id → % học sinh hổng`, nhóm học sinh theo gap (clustering đơn giản), xếp hạng ưu tiên theo depth+impact, cảnh báo lỗ hổng diện rộng (`>N%`). **Access control**: chỉ trả data của `class_id` được truyền, không leak lớp khác. | Phase 1, 5.1 |
| 2.5 | `tools/parent_dashboard_query.py` | Input: `student_id, parent_id`. Output: tiến độ theo thời gian + gợi ý hành động tại nhà. **Access control bắt buộc**: verify `parent_id` có quyền với `student_id` trước khi trả data — nếu không khớp, trả lỗi quyền truy cập rõ ràng, không trả rỗng (tránh nhầm "không có dữ liệu"). | Phase 1, 5.1 |
| 2.6 | `tests/test_tools.py` | Test input/output đúng format + **test riêng cho từng fallback case** ở trên (không có gap, sai quyền, câu hỏi thiếu). | 2.1–2.5 |

**Checklist cuối Phase 2:**
- [ ] Ghi `AI_LOG.md` cho từng file.
- [ ] Test access-control (2.4, 2.5) pass — đây là bằng chứng trực tiếp cho tiêu chí Grounding & Độ tin cậy (15đ).

---

### Phase 3 — Domain Adapter (nối LLM vào tools)

| # | File | Mô tả | Phụ thuộc |
|---|---|---|---|
| 3.1 | `domain/adaptive_tutor_adapter.py` | Implement `DomainAdapter`: `system_prompt()` + `tools()` trả về `[diagnose_gap, generate_practice_path, teacher_dashboard_query, parent_dashboard_query]`. System prompt: (a) vai trò gia sư thích ứng; (b) **chỉ được dùng tool để trả lời, không tự bịa số liệu mastery/gap**; (c) hướng dẫn xử lý khi tool trả lỗi (xin lỗi + gợi ý bước tiếp theo, không im lặng). | Phase 2 |
| 3.2 | `domain/prompts/*.md` | Tách `system.md`, `diagnose_explain.md`, `parent_explain.md`, `teacher_explain.md` — dễ tinh chỉnh không cần sửa code. | 3.1 |
| 3.3 | `gateway/app/routes/chat.py` | Sửa: đổi `SMEInnovationAdapter` → `AdaptiveTutorAdapter`. Thêm field `role: Literal["student","teacher","parent"]` vào `ChatRequest`, truyền role này để domain adapter chọn đúng tool/tông giọng. **Fallback**: nếu `role` không hợp lệ → HTTP 422 rõ ràng, không mặc định âm thầm về "student". | 3.1 |

**Checklist cuối Phase 3:**
- [ ] Chạy `docker compose up --build` — kiểm tra end-to-end: hỏi → BKT chẩn đoán → LLM diễn giải chạy được qua `/chat`.
- [ ] Ghi `AI_LOG.md`, đối chiếu với `git log`.

**→ Đây là mốc "Ưu tiên 1 hoàn tất" — hệ thống chạy được happy path chính.**

---

### Phase 4 — Input/Output LLM Layers

| # | File | Mô tả | Phụ thuộc |
|---|---|---|---|
| 4.1 | `ai/output_interpreter.py` | LLM diễn giải mastery probabilities + gap graph → câu giải thích tự nhiên. 2 tông: giáo viên (thuật ngữ, heatmap) vs phụ huynh (đơn giản, hành động cụ thể tại nhà). Làm **trước** 4.2/4.3 vì tác động trực tiếp UX demo. | Phase 3 |
| 4.2 | `ai/input_extractor.py` (stretch) | LLM trích xuất có cấu trúc: Curriculum PDF → skill graph JSON; CV học sinh → structured profile. Dùng Anthropic tool-use để enforce format JSON. **Không phụ thuộc vào việc này để demo chạy được** — `knowledge_graph.json` viết tay (1.0) là phương án chính, đây chỉ là bonus. | Phase 1 |
| 4.3 | `ai/adaptive_test.py` (stretch) | CAT: sau mỗi câu, chọn câu tiếp theo nhắm skill có entropy cao nhất trong mastery hiện tại. Đo lường "giảm X% số câu so với đề cố định". | Phase 1, 2.2 |

**Checklist cuối Phase 4:**
- [ ] Ghi `AI_LOG.md`, đặc biệt lưu prompt đã dùng để sinh `output_interpreter.py` (yêu cầu riêng theo `AI_LOG.md` template khi thay đổi Domain Adapter/prompt).

---

### Phase 5 — Integration + DB Schema

| # | File | Mô tả | Phụ thuộc |
|---|---|---|---|
| 5.1 | `db/models.py` | Bổ sung: `Student, Skill, StudentSkillMastery, Answer, Question, Class, Parent`. Làm **song song** với Phase 2, không chờ — 2.4/2.5 cần các model này. | Không phụ thuộc code khác, chỉ cần schema đã chốt từ 1.0 |
| 5.2 | `db/seed_data.py` | Script: `knowledge_graph.json` → DB, import question bank mẫu (từ 2.2). | 5.1, 1.0, 2.2 |
| 5.3 | `gateway/app/routes/diagnose.py` (stretch) | Endpoint `POST /diagnose` — học sinh nộp bài test → gap analysis trực tiếp, không qua chat (dùng cho luồng UI riêng nếu Design cần). | Phase 2 |
| 5.4 | `tests/test_integration.py` | Test end-to-end: placement test → BKT diagnose → generate practice path, chạy trên DB thật (không mock). | Toàn bộ Phase 1–3, 5.1–5.2 |

**Checklist cuối Phase 5:**
- [ ] Ghi `AI_LOG.md`.
- [ ] Chạy lại toàn bộ `pytest` — không có test fail trước khi chuyển sang giai đoạn deploy.

---

## 4. Timeline gắn mốc giờ cụ thể (khung 48h: 17–19/7)

| Giờ | Việc | Ghi chú |
|---|---|---|
| 0–3 | Mục 0 (xác nhận đề bài, sync docs) + 1.0 (knowledge_graph.json) | Người hiểu nội dung môn học làm 1.0 song song với Dev đọc lại repo |
| 3–8 | 1.1 → 1.2 → 1.3 | **Không bỏ qua**, đây là lõi khác biệt của sản phẩm |
| 8–14 | 2.2 (question_bank) → 2.1 (diagnose_gap) → 3.1 → 3.2 → 3.3 | Chạy `docker compose up --build` ngay cuối mốc này để bắt lỗi hạ tầng sớm |
| 14–20 | 2.3, 2.4, 2.5 + 5.1 (song song) | Access-control test bắt buộc trước khi qua mốc tiếp theo |
| 20–26 | 4.1 (output_interpreter) + 5.2 (seed_data) + 2.6/5.4 (test) | |
| 26–32 | Buffer + stretch nếu còn giờ: 4.2, 4.3, 5.3 | Không bắt đầu stretch nếu Phase 1–3 chưa test pass |
| 32–44 | Deploy live URL, quay demo ≤5 phút, hoàn thiện `PROJECT_DESCRIPTION.md`/README, slide | Dừng code tính năng mới |
| 44–48 | Kiểm tra 5 hạng mục nộp bài, repo public, URL còn sống | |

---

## 5. Rủi ro đã khắc phục so với plan gốc

| Rủi ro ở plan cũ | Cách khắc phục trong plan này |
|---|---|
| Không có mốc giờ cụ thể | Bảng Timeline mục 4 |
| Thiếu xử lý lỗi/fallback | Ghi rõ fallback bắt buộc trong từng dòng Phase 1, 2, 3 |
| Nguồn câu hỏi (question bank) chưa rõ | Mục 2.2 nêu rõ seed tay trước, LLM sinh thêm là bonus |
| Chưa gắn AI_LOG song song | Checklist AI_LOG ở cuối mỗi Phase |
| Chưa rõ thứ tự phụ thuộc giữa file | Cột "Phụ thuộc" trong mọi bảng Phase |
| Docs (README/PROJECT_DESCRIPTION) có thể lệch chủ đề | Mục 0 — việc đầu tiên trước khi code |
| Không rõ ai đo lường được tiêu chí Grounding (15đ) | Access-control test (2.4, 2.5) gắn cụ thể vào tiêu chí này |

---

## 6. Nếu chỉ còn rất ít thời gian (worst case)

Tối thiểu để có sản phẩm chạy được và giữ đúng "AI-native, có lõi khác biệt":

1. `ai/knowledge_graph.json` (1.0)
2. `ai/knowledge_graph.py` + `ai/bkt_engine.py` (1.1, 1.2) — **không được bỏ**
3. `tools/diagnose_gap.py` (2.1)
4. `domain/adaptive_tutor_adapter.py` + sửa `chat.py` (3.1, 3.3)

Bốn mục này là ranh giới tối thiểu giữa "sản phẩm AI-native thật" và "chatbot LLM thông thường".
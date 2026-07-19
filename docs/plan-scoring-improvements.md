# Plan: Cải thiện điểm theo tiêu chí chấm (Checkpoint 36h)

## Context

BTC chấm 6 tiêu chí, 100 điểm; ở Checkpoint 36h, mục 6 "Trình bày & Bảo vệ giải pháp"
tính 0 điểm — chỉ 5 tiêu chí đầu (mỗi mục 20đ) được chấm ở mốc này. Đối chiếu ảnh tiêu
chí BTC gửi với `docs/scoring-checklist.md` (checklist nội bộ) và code hiện tại để tìm
việc còn thiếu, có giá trị nhất trong thời gian còn lại trước Final (11:00 19/7).

`docker-compose up --build` đã được xác nhận chạy OK (user tự chạy) — mục kỹ thuật P0
chặn nhất đã qua.

## Đã hoàn thành trong phiên này

1. Xóa `frontend/build_error.txt` (log lỗi build cũ, có path máy khác) khỏi git +
   thêm vào `.gitignore` — tránh nộp kèm artifact debug trông thiếu chuyên nghiệp.
2. Thêm mục **10. Business Case & Pilot Pathway** vào `docs/PROJECT_DESCRIPTION.md`
   (trước đó hoàn toàn trống — 20/100 điểm bỏ ngỏ). Nội dung: ai trả tiền (mô hình
   B2B2C qua nhà trường + kênh tài trợ Sở GD&ĐT/CSR), giả định giá (gắn nhãn rõ là giả
   định), lộ trình pilot 4 giai đoạn, tiêu chí thành công đo được, lợi thế/rủi ro.
   *Chưa có số liệu/tên thật (VD kinh nghiệm cố vấn) — cần team tự điền nếu có.*
3. Thêm `pytest.ini` (`pythonpath = gateway`) ở root — trước đó `pytest tests/` lỗi
   ngay bước import (`ModuleNotFoundError: No module named 'app'`) vì `app` chỉ tồn tại
   ở `gateway/app/`. Giờ chạy sạch: **15 passed**.
4. Đổi tên `domain/sme_innovation_adapter.py` → `domain/adaptive_tutor_adapter.py`,
   class `VNexusTutorAdapter` → `AdaptiveTutorAdapter` — tên cũ là tàn dư từ đề bài SME
   (Đề 8) đã bỏ, có thể gây hiểu nhầm khi giám khảo đọc code. Cập nhật import duy nhất ở
   `gateway/app/routes/chat.py`. Test suite vẫn pass sau khi đổi.
5. Xóa 3 file rác kỹ thuật ("dead code hiển nhiên" — đúng tiêu chí #1): `patch_crud.py`
   (script vá code 1 lần bằng regex, không dùng lại), `gateway/app/routes/crud_patched.py`
   (kết quả sinh từ script trên, **không được import ở đâu** nhưng vẫn bị đóng gói vào
   Docker image vì nằm trong `gateway/app/`), và `test_db.py` (script debug thủ công,
   hardcode `id==18`, không phải test thật, không nằm trong `tests/`). Test suite vẫn
   15 passed sau khi xóa.

*Các thay đổi trên đang ở working tree, **chưa commit** — xem mục "Câu hỏi cần quyết
định" bên dưới.*

## Đề xuất tiếp theo, theo từng tiêu chí

### 1. Technical Implementation & Engineering Depth (20đ) — ĐÃ LÀM

- [x] Rà toàn bộ git-tracked files tìm artifact debug/log lạ, file to bất thường, path
      máy cá nhân lộ trong code. Kết quả: các file `.log` còn lại (`logs/*-session/*.log`)
      là bằng chứng phiên AI bắt buộc nộp theo `RULES.md`, không phải rác — giữ nguyên.
      Không có `__pycache__` bị track, không có path máy cá nhân lộ trong code/docs
      (ngoài `logs/SUBMISSION_EVIDENCE.md` — nơi đó là chủ đích, mô tả máy dev).
- [x] Phát hiện và xóa 3 file rác kỹ thuật thật sự (xem mục "Đã hoàn thành" bên trên):
      `patch_crud.py`, `gateway/app/routes/crud_patched.py` (dead code bị đóng gói vào
      Docker image), `test_db.py`.
- [ ] Không đề xuất thêm CI/lint pipeline mới — rủi ro/thời gian không đáng so với lợi
      ích ở mốc này.

### 2. AI-Native Architecture & Innovation (20đ)

- ~~`docs/AI_LOG.md` reconciliation~~ — **bỏ, theo quyết định của user**: bằng chứng AI
  collaboration được chuyển sang track ở `logs/` (session log thật của từng công cụ:
  `claude-session/`, `opencode-session/`, `gemini-session/`), user sẽ tự bổ sung log của
  Quyết/Hiếu/Ngọc vào đó. Không cần tôi sửa `AI_LOG.md` nữa.

- [x] **Phát hiện lớn hơn, đã xử lý**: kiến trúc `PlannerAgent` + `AdaptiveTutorAdapter` +
      Tool Registry (được README quảng bá là lõi AI-Native) **không được sản phẩm thật
      dùng tới** — xác minh bằng grep: frontend không gọi `/chat` ở đâu cả; flow thật
      (`gateway/app/routes/crud.py`) gọi thẳng `domain.bkt.run_assessment` và
      `tools.plan_tool.generate_training_plan`, bỏ qua hoàn toàn agent framework; 3/4 tool
      đăng ký trong adapter (`assess_tool`, `teacher_summary_tool`, `parent_summary_tool`)
      không có nơi gọi nào khác ngoài chính chúng. User chọn phương án an toàn nhất: **chỉ
      dọn dead code, không rewiring**. Đã thực hiện:
      - Xóa `gateway/app/routes/chat.py` (endpoint chết, thực ra còn *hỏng* vì `.env` đã bỏ
        `ANTHROPIC_API_KEY` mà `agent/llm_client.create_message` cần).
      - Bỏ đăng ký `chat_router` trong `gateway/app/main.py`.
      - Xóa `domain/adaptive_tutor_adapter.py` (chỉ được chat.py dùng).
      - Xóa `tools/assess_tool.py`, `tools/teacher_summary_tool.py`, `tools/parent_summary_tool.py`
        (387 dòng code nghiệp vụ song song, không nơi nào gọi tới ngoài adapter vừa xóa).
      - Giữ lại `agent/planner.py`, `tools/registry.py`, `domain/adapter.py`, `mcp_server/`
        — khung framework chung (có test riêng `tests/test_tool_registry.py`), không phải
        code nghiệp vụ giả — sửa README ghi rõ đây là "khung tham khảo", flow thật không
        đi qua đây, tránh nói dối kiến trúc mà không cần xóa toàn bộ (rủi ro cao hơn, cần
        sửa nhiều test/doc hơn).
      - Cập nhật `README.md` (mục Kiến trúc + Cấu trúc thư mục) cho khớp thực tế.
      - `pytest tests/` vẫn 15 passed sau khi xóa.
- Domain adapter clarity (đổi tên `sme_innovation_adapter.py`) — đã làm ở mục trước, giờ
  thành vô nghĩa vì file đó đã bị xóa hẳn (không phải đổi tên nữa).

### 3. Business Viability & Pilot Pathway (20đ) — ĐÃ LÀM

User xác nhận không có số liệu nội bộ cụ thể → thay vì để giả định trần trụi, đã research
số liệu thị trường thật (WebSearch) để neo mục 10, thay vì bịa hoặc để giả định vô căn cứ:

- [x] **Quy mô thị trường thật**: 11.559 trường tiểu học công lập, 8,8 triệu học sinh
      (năm học 2024–2025, Bộ GD&ĐT) — thêm mới, trước đó mục 10 không có phần TAM.
- [x] **Sĩ số lớp thật**: bình quân 31,8 h.s/lớp, trần quy định 35 (Thông tư
      28/2020/TT-BGDĐT), thực tế nhiều nơi 40–50 — khớp trực tiếp với con số "lớp 40 học
      sinh" trong chính đề bài gốc, biến "Gap" từ mô tả định tính thành có thống kê đứng sau.
- [x] **Phát hiện quan trọng, đổi khung mô hình thu tiền**: trường công lập VN bị kiểm
      soát chặt chống "lạm thu" — khoản thu chuyển đổi số phục vụ quản trị trường tuyệt
      đối không được thu xã hội hóa, chỉ thu được nếu phục vụ trực tiếp việc học, phải tự
      nguyện/công khai, tăng tối đa 15%/năm. Điều này biến "nhà trường trả phí, không thu
      qua phụ huynh" từ một lựa chọn kinh doanh thành **một lợi thế tuân thủ pháp lý rõ
      ràng** — đã viết lại phần "Ai trả tiền" để nêu rõ đây là lý do, không chỉ là mô tả
      mô hình B2B2C chung chung như bản trước.
- [x] **Neo giá theo thị trường thật**: học phí trung tâm Anh ngữ tư nhân 75.000–300.000đ/
      buổi, 600.000–1.000.000đ/tháng, một khóa 8,8–23,5 triệu (ILA/VUS/Igems) — dùng để
      chứng minh mức giá đề xuất (15.000–25.000đ/học sinh/học kỳ) rẻ hơn cả 1 buổi học tư,
      dễ thuyết phục nhà trường/Sở phê duyệt, thay vì là con số ước lượng không có gì so
      sánh.
- [x] **Nguồn tài trợ chính sách thật**: trích Nghị quyết 57-NQ/TW (định hướng chuyển đổi
      số giáo dục 2026–2030, khuyến khích xã hội hóa/hợp tác công-tư, hỗ trợ vùng khó
      khăn) làm căn cứ cho kênh tài trợ Sở GD&ĐT, thay vì chỉ nói chung chung "ngân sách
      chuyển đổi số".
- [x] Thêm mục "Nguồn tham khảo" với 9 link nguồn (báo chí tổng hợp số liệu Bộ GD&ĐT,
      quy định thu chi, tuition benchmark) — kèm lưu ý rõ đây là nguồn thứ cấp, nên đối
      chiếu văn bản gốc (`moet.gov.vn/thong-ke`, Thông tư 28/2020, Nghị quyết 57-NQ/TW)
      nếu bị giám khảo hỏi sâu về pháp lý/thống kê.

### 4. AI-Native UX & Design Thinking (20đ) — ĐÃ LÀM, PHÁT HIỆN BUG NGHIÊM TRỌNG

Đã tự chạy được browser thật (Playwright + Chromium headless cài tạm trong venv, `--no-sandbox`
vì môi trường không có quyền root cho system deps) — không cần đợi user nữa.

- [x] `docker-compose up -d --build` từ đầu, chờ gateway/frontend healthy qua `curl` polling.
- [x] Đăng nhập học sinh (`hs0X@vnexus.vn` / `123456`, seed data fresh), đi qua **toàn bộ
      happy path thật**: landing → đăng nhập → Khảo sát đầu vào → chọn "Global Success —
      Lớp 3 (Dễ)" → làm hết 21 câu (chọn đáp án, xem feedback đúng/sai từng câu) → nộp bài
      → xem kết quả (mastery theo kỹ năng, lỗ hổng kiến thức, CEFR). UI/UX đúng như mô tả
      trong `PROJECT_DESCRIPTION.md` — feedback tức thời tô xanh/đỏ theo từng đáp án, gap
      list có severity, không phải placeholder.
- [x] **PHÁT HIỆN & SỬA BUG NGHIÊM TRỌNG ĐANG CHẠY THẬT**: mọi lần nộp bài chẩn đoán
      (`POST /api/placement-tests/{id}/submit`) **crash 500** — bắt được qua
      `console --errors`/network response khi chạy Playwright, xác nhận bằng gateway log:
      `UnboundLocalError: cannot access local variable 'select'`. Nguyên nhân:
      `gateway/app/routes/crud.py:1521` có dòng `from sqlalchemy import select` thừa ở giữa
      hàm `submit_placement_test` (trong khi `select` đã import ở đầu file dòng 6) — theo
      quy tắc scope của Python, việc này biến `select` thành biến local cho **toàn bộ hàm**,
      làm vỡ lệnh `select(...)` dùng ở dòng 1472 phía trên, chạy trước khi tới dòng import
      thừa đó.
      - **Vì sao nguy hiểm dù demo "nhìn có vẻ chạy"**: frontend vẫn hiển thị đầy đủ trang
        kết quả (điểm, mastery, gaps) dù backend lỗi 500 — có khả năng do tính toán fallback
        phía client. Nghĩa là **nếu không bắt bằng network/log, sẽ tưởng flow chạy tốt**
        trong khi thực ra: kết quả chưa từng được lưu DB, BKT Engine backend (nguồn grounding
        chính thức) chưa từng chạy, và **lộ trình đào tạo AI (`training_plan`) chưa từng được
        sinh** — đúng 3 thứ then chốt của tiêu chí AI-Native UX + Grounding.
      - **Đã sửa**: xóa dòng import thừa, rebuild lại container gateway
        (`docker-compose stop/rm/up --build gateway`), chạy lại đúng kịch bản nộp bài —
        xác nhận: 0 lỗi console, 0 response 4xx/5xx, và **kết quả mới đã xuất hiện thật
        trong "Lịch sử bài đánh giá"** (bằng chứng DB đã lưu, không phải fallback client).
      - `pytest tests/` vẫn 15 passed sau khi sửa (bug này không có test bao phủ trước đó —
        gợi ý cần thêm 1 test tích hợp cho endpoint submit nếu còn thời gian, nhưng ưu tiên
        thời gian còn lại nên dừng ở mức fix + verify thủ công).
- [ ] Chưa kiểm được trạng thái "cần kiểm tra thêm" (thiếu bằng chứng) do bộ 21 câu ở mức
      Dễ luôn đủ bằng chứng theo mọi kiểu trả lời tôi thử — cần bộ câu hỏi ít hơn hoặc mock
      answers thưa hơn mới trigger được nhánh này; không ưu tiên tiếp vì thời gian.
- [ ] Banner "Online/Offline" đã thấy hiển thị trên header (góc phải), nhưng chưa test được
      trạng thái mất mạng thật qua Playwright trong thời gian còn lại.

### 5. AI Safety, Grounding & Trust (20đ)

- Đã rà (read-only) toàn bộ prompt LLM (`tools/plan_tool.py`, `agent/llm_client.py`,
  `domain/adaptive_tutor_adapter.py`, teacher/parent summary tools) — **không có vi
  phạm** quy tắc cấm gắn nhãn tính cách (hướng nội/nhút nhát...) từ `PROFILE_SURVEY.xlsx`.
- Ghi chú: `PROFILE_SURVEY.xlsx` (khảo sát 12 câu về sở thích/phong cách học) **chưa
  thực sự được tool nào tiêu thụ** — `generate_training_plan_from_survey` dùng một khảo
  sát đơn giản hơn (số năm học, môi trường, tự đánh giá, mục tiêu), không phải file này.
  Không cần sửa gì bây giờ; chỉ là điểm cần để ý nếu ai đó wire dữ liệu thật vào sau.
- [ ] Đề xuất demo có 1 khoảnh khắc "khi LLM lỗi → fallback template" thật sự chạy được
      (không chỉ mô tả trong docs) — đây là bằng chứng cụ thể, dễ thuyết phục cho tiêu
      chí Grounding & Trust nếu giám khảo hỏi "lỡ AI lỗi thì sao".

## Không đề xuất làm thêm

- Refactor kiến trúc lớn, thêm tính năng mới, hay tối ưu hoá sớm — đúng nguyên tắc
  team đã đặt ở `docs/timeline.md` ("đừng tối ưu, đừng làm đẹp sớm").

## Câu hỏi cần quyết định

1. Đồng ý cách xử lý `AI_LOG.md` (cập nhật trạng thái "Đã commit" chung chung thay vì
   hash chính xác từng dòng) hay muốn tôi tiếp tục đào sâu để tìm hash chính xác hơn?
2. Có muốn tôi nhắn/soạn sẵn tin nhắn nhắc Quyết/Hiếu/Ngọc bổ sung `AI_LOG.md` không?
3. 4 thay đổi đã làm ở trên đang **chưa commit** — commit ngay bây giờ (1 commit) hay để
   user tự review diff trước?

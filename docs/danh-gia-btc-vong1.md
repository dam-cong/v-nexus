# Đánh giá BTC VAIC 2026 (Vòng 1) & Phân tích cải tiến

> Tài liệu lưu lại nguyên văn đánh giá của Ban Tổ Chức (nhận qua email ngày 2026-07-23) và
> phân tích đối chiếu với hiện trạng thực tế của codebase, kèm đề xuất cải tiến ưu tiên cho
> vòng tiếp theo. Đây là tài liệu phân tích/khuyến nghị — **không phải** thay đổi code.

## 1. Kết quả đánh giá gốc

**Tổng điểm:** 61.2/100 (điểm trung bình cộng của 3 checkpoints)
**Thứ hạng:** 104

| Tiêu chí (khớp `docs/scoring-checklist.md`) | Điểm |
|---|---|
| Technical Implementation & Engineering Depth | 12/20 |
| AI-Native Architecture & Innovation | 11/20 |
| Business Viability & Pilot Pathway | 13/20 |
| AI-Native UX & Design Thinking | 10/15 |
| **AI Safety, Grounding & Trust** | **7/15** ⚠️ thấp nhất |
| **Presentation, Demo & Defensibility** | **5/10** ⚠️ thấp nhất |

**Điểm mạnh BTC ghi nhận:**
- AI-driven root-cause analysis, map lỗi sai với kỹ năng tiên quyết còn thiếu
- Lộ trình học cá nhân hoá, tránh học lại nội dung đã thành thạo
- Dashboard giáo viên với class heat-map và AI-suggested comments
- Gamification (coins/XP/badges) và ghi nhận toàn trường
- Thiết kế offline-first cho môi trường băng thông thấp

**Điểm cần cải thiện BTC nêu:**
1. Chưa có chi tiết cụ thể về training data, model validation, hoặc accuracy metrics
2. Tiềm ẩn vấn đề privacy và data-governance cho dữ liệu học tập của học sinh
3. Chưa rõ cơ chế offline sync hoạt động ra sao và tần suất cập nhật nội dung

## 2. Đối chiếu với hiện trạng codebase & đề xuất cải tiến

### 2.1. Training data / model validation / accuracy metrics

**Hiện trạng thực tế:**
- `domain/bkt.py` dùng tham số Bayesian Knowledge Tracing **cố định**
  (`PRIOR=0.3, TRANSIT=0.3, GUESS=0.2, SLIP=0.1`), không hiệu chỉnh từ dữ liệu thật — comment
  trong code tự thừa nhận: *"vì bản demo không có đủ dữ liệu"*.
- Không có eval harness nào; `tests/test_bkt.py` chỉ có unit test với case tự tạo (synthetic),
  không phải dữ liệu học sinh thật.
- `docs/ai-danh-gia.md` §6 từng đề xuất dùng dataset công khai (ASSISTments, EdNet) để test
  nội bộ nhưng chưa bao giờ triển khai.
- `domain/knowledge_graph.py` là đồ thị kỹ năng tiên quyết soạn thủ công (16 node, tiếng Anh
  lớp 3-4), không phải học từ dữ liệu.

**Đề xuất:** Bổ sung mục "Model & Validation" vào `docs/PROJECT_DESCRIPTION.md`:
- Trình bày rõ đây là lựa chọn thiết kế có chủ đích: BKT tường minh/explainable-by-design thay
  vì mô hình black-box, giúp giáo viên/phụ huynh tin tưởng và audit được.
- Thừa nhận thẳng thắn số liệu demo hiện tại **chưa được kiểm định** trên dữ liệu thật quy mô
  lớn (đừng để giám khảo tự phát hiện qua code — nên chủ động nói trước).
- Đề xuất lộ trình validation cụ thể: backtest tham số BKT trên dữ liệu ASSISTments/EdNet công
  khai, sau đó calibrate lại trên dữ liệu pilot thật; định nghĩa rõ "accuracy" nghĩa là gì cho
  hệ thống này (vd: độ chính xác dự đoán mastery so với kết quả bài kiểm tra thật).

### 2.2. Privacy & data-governance

**Hiện trạng thực tế:**
- `db/models.py`: toàn bộ PII (tên, email, số điện thoại phụ huynh, điểm số, nhận xét giáo
  viên) lưu **plaintext**, không mã hoá field-level, không ẩn danh hoá.
- `gateway/app/main.py:28`: CORS mở toàn bộ `allow_origins=["*"]`.
- Không tìm thấy consent flow, không có endpoint export/xoá dữ liệu, không có audit log ở bất
  kỳ đâu trong `gateway/app` hoặc `db/`.
- Điểm sáng: `docs/v-nexus-core-flows.drawio.xml` có node thiết kế `f515_privacy` ("Chặn
  drill-down cá nhân") — cho thấy vấn đề đã được nghĩ tới ở giai đoạn thiết kế, nhưng chưa
  được hiện thực hoá hay tài liệu hoá thành chính sách.

**Đề xuất:** Viết một mục data-governance ngắn gọn (trong `PROJECT_DESCRIPTION.md` hoặc file
riêng), nêu:
- Hiện trạng (thẳng thắn, không né tránh) và roadmap: mã hoá dữ liệu nhạy cảm khi lưu, giới
  hạn CORS theo domain thật, phân quyền truy cập theo hàng dữ liệu (giáo viên/phụ huynh chỉ
  xem được học sinh của mình), chính sách lưu trữ/xoá dữ liệu.
- Trích dẫn node `f515_privacy` trong sơ đồ flow như bằng chứng vấn đề đã được cân nhắc từ đầu.

### 2.3. Offline sync

**Hiện trạng thực tế** (`docs/plan-offline-mode.md`, `frontend/src/offline/db.js`, `sync.js`):
- Nội dung offline chỉ được seed **một lần** lúc container frontend khởi động
  (`export-offline-data.cjs` qua `start-offline.sh`), không có cơ chế re-export định kỳ khi
  container đang chạy → nội dung có thể "cũ" cho tới lần deploy/restart kế tiếp.
- Đồng bộ kết quả bài làm offline (`pendingResults`) chỉ chạy phản ứng theo event `online` của
  trình duyệt, không có polling/background retry định kỳ.
- Không có conflict resolution — được ghi rõ là **ngoài phạm vi** ở
  `docs/plan-offline-mode.md` (dòng ~218: "Đồng bộ hai chiều an toàn (xung đột, retry phức
  tạp)" chưa làm).
- Engine chấm điểm (BKT) đã được port sang JS (`frontend/src/offline/bkt.js`) nên hoạt động
  hoàn toàn offline, không cần mạng.

**Đề xuất:** Viết rõ trong tài liệu sản phẩm (không cần sửa code): tần suất cập nhật thực tế
là "mỗi lần deploy/restart", giới hạn hiện tại là đồng bộ một chiều khi có mạng trở lại (chưa
xử lý xung đột hai chiều), và đây là quyết định phạm vi có chủ đích cho bản demo — kèm hướng
mở rộng (re-sync định kỳ, conflict resolution) cho bản production.

### 2.4. AI Safety, Grounding & Trust (7/15 — thấp nhất)

Theo `docs/scoring-checklist.md`, tiêu chí này yêu cầu: "Câu trả lời quan trọng được grounding
qua tool/DB, không để LLM tự bịa" và "Có xử lý khi tool lỗi hoặc dữ liệu thiếu".

**Hiện trạng thực tế:** `tools/plan_tool.py` có hàm `_post_validate()` nhưng hiện là **no-op**
— chỉ kiểm tra tên kỹ năng có xuất hiện trong output, không thực sự chặn hay log khi LLM sinh
nội dung không được grounding.

**Đề xuất:** Ghi nhận đây là giới hạn đã biết trong tài liệu, kèm kế hoạch khắc phục cụ thể
(việc sửa code này để lại cho công việc sau, ngoài phạm vi tài liệu này) — vd: `_post_validate`
cần thực sự reject/fallback khi phát hiện nội dung không grounded, và log lại các lần fallback
để theo dõi tỉ lệ.

### 2.5. Presentation, Demo & Defensibility (5/10 — thấp nhất)

**Hiện trạng thực tế:** Khảo sát repo không tìm thấy file slide (.pptx/.pdf) hay video demo,
trong khi `docs/RULES.md` yêu cầu rõ phải nộp slide thuyết trình + video demo ≤5 phút như một
phần hồ sơ dự thi.

**Đề xuất:** Đây nhiều khả năng là điểm dễ cải thiện nhất vì đang **thiếu hẳn** tài liệu, chứ
không phải vấn đề chất lượng — ưu tiên hoàn thiện slide (kiến trúc, vấn đề, giải pháp, business
case) và quay video demo, đồng thời chuẩn bị trước câu trả lời cho đúng 3 điểm yếu BTC đã nêu
để chủ động "phòng thủ" trong Q&A vòng 3.

## 3. Danh sách ưu tiên hành động

| # | Hành động | Tiêu chí liên quan | Vì sao ưu tiên |
|---|---|---|---|
| 1 | Hoàn thiện slide thuyết trình + video demo ≤5 phút | Presentation (5/10) | Đang thiếu hẳn, không phải vấn đề chất lượng — dễ ăn điểm nhất |
| 2 | Bổ sung mục Model & Validation vào `PROJECT_DESCRIPTION.md` | AI Safety (7/15), Defensibility | Biến "chưa biết" thành "đây là kế hoạch rõ ràng" |
| 3 | Viết mục data-governance/privacy (hiện trạng + roadmap) | AI Safety, Business Viability | Giám khảo đã chỉ đích danh; hiện chưa có tài liệu nào |
| 4 | Viết rõ giới hạn & tần suất offline sync trong tài liệu | Technical Implementation | Trả lời trực tiếp câu hỏi BTC nêu |
| 5 | (Việc code, để sau) Sửa `_post_validate()` thành kiểm tra thật | AI Safety (7/15) | Gap cụ thể, có thể nâng điểm tiêu chí thấp nhất |

## 4. Dự trù chi phí triển khai — hoàn thiện giải pháp

> Mục này trả lời câu hỏi "cần bao nhiêu để đưa sản phẩm từ MVP hackathon 48h lên trạng thái
> hoàn thiện, sẵn sàng pilot thật" — tức **chi phí xây dựng/phát triển (một lần)**, khác với
> chi phí vận hành hạ tầng khi đã chạy pilot (xem mục 4.5). Số liệu là **ước tính minh họa**
> theo mặt bằng giá nhân sự IT/edtech phổ biến tại Việt Nam — cần điều chỉnh theo năng lực
> thật của đội và mức lương/rate cụ thể trước khi chốt ngân sách.

### 4.1. Phạm vi còn thiếu so với "giải pháp hoàn thiện"

Đối chiếu MVP hiện tại với mục "Hướng mở rộng" (`docs/PROJECT_DESCRIPTION.md` mục 12) và các
gap đã nêu ở mục 2 tài liệu này:

| Hạng mục | Hiện trạng MVP | Việc cần làm để hoàn thiện |
|---|---|---|
| Knowledge Graph & ngân hàng câu hỏi | 1 mạch kỹ năng, lớp 3–4, môn Tiếng Anh (16 skill node) | Mở rộng toàn bộ khối lớp 1–5, đủ mạch kỹ năng môn Tiếng Anh theo GDPT 2018; xa hơn là môn học khác |
| Model validation | Tham số BKT cố định, chưa hiệu chỉnh từ dữ liệu thật, không có eval harness | Xây eval harness, backtest trên dataset công khai (ASSISTments/EdNet), calibrate lại từ dữ liệu pilot thật |
| AI Safety / grounding | `_post_validate()` trong `tools/plan_tool.py` là no-op | Hiện thực kiểm tra grounding thật (reject/fallback + log khi output không grounded) |
| Privacy / data-governance | Dữ liệu PII lưu plaintext, CORS mở `*`, không có consent/audit/retention | Mã hoá dữ liệu nhạy cảm, giới hạn CORS, phân quyền theo hàng dữ liệu, consent flow, audit log, viết chính sách retention |
| Offline sync | Seed 1 lần lúc khởi động container, sync 1 chiều khi có mạng, không xử lý xung đột | Re-sync định kỳ, conflict resolution 2 chiều, giám sát tình trạng đồng bộ |
| Dashboard phụ huynh | Chưa có | Xây mới, kèm cơ chế ủy quyền/bảo vệ dữ liệu (`docs/PROJECT_DESCRIPTION.md` mục 12) |
| Kiểm duyệt nội dung trong app | Duyệt ngoài app, nạp thủ công | Xây workflow duyệt Knowledge Graph/câu hỏi ngay trong app |
| QA / kiểm thử | Unit test synthetic, chưa test với người dùng thật | Test với học sinh/giáo viên thật ở quy mô pilot, sửa lỗi phát sinh |
| Presentation | Chưa có slide/demo video trong repo | Hoàn thiện slide + video (việc nhỏ, không tính vào chi phí phát triển) |

### 4.2. Đội ngũ cần thiết & thời gian

Team hackathon hiện tại (`docs/timeline.md`): PM, BA, 1 Dev, 1 AI, 1 Cố vấn — đủ cho MVP 48h
nhưng cần bổ sung năng lực để hoàn thiện phạm vi ở mục 4.1 trong khoảng **3–4 tháng**:

| Vai trò | Việc chính | Ước tính effort |
|---|---|---|
| Backend developer | Privacy/security hardening, offline sync 2 chiều, dashboard phụ huynh | 3–4 người-tháng |
| Frontend developer | Dashboard phụ huynh, hoàn thiện PWA offline, workflow duyệt nội dung trong app | 3–4 người-tháng |
| AI/ML engineer | Eval harness, calibrate BKT, fix `_post_validate`, mở rộng thuật toán truy gốc | 2–3 người-tháng |
| Giáo viên/chuyên gia sư phạm (bán thời gian) | Biên soạn + kiểm duyệt Knowledge Graph/ngân hàng câu hỏi mở rộng | 2–3 người-tháng quy đổi |
| QA/Tester | Kiểm thử end-to-end, kiểm thử với người dùng thật trong pilot | 1–2 người-tháng |
| PM/BA (duy trì từ team gốc) | Điều phối, quản lý phạm vi, làm việc với trường/Sở GD&ĐT | Xuyên suốt, bán thời gian |
| Tư vấn bảo mật (theo đợt, không cần full-time) | 1 đợt rà soát/audit trước khi nhận dữ liệu học sinh thật | 1 đợt ngắn (vài ngày) |

### 4.3. Ước tính chi phí (nếu cần thuê/trả công đầy đủ)

| Vai trò | Rate ước tính (VNĐ/tháng) | Effort | Thành tiền (ước tính) |
|---|---|---|---|
| Backend developer | 15–25 triệu | 3–4 tháng | 45–100 triệu |
| Frontend developer | 15–25 triệu | 3–4 tháng | 45–100 triệu |
| AI/ML engineer | 20–35 triệu | 2–3 tháng | 40–105 triệu |
| Giáo viên/chuyên gia nội dung | quy đổi 5–15 triệu/mạch kỹ năng | vài mạch kỹ năng | 20–60 triệu |
| QA/Tester | 10–15 triệu | 1–2 tháng | 10–30 triệu |
| Tư vấn bảo mật (1 đợt) | trọn gói | 1 đợt | 10–20 triệu |
| **Tổng ước tính** | | **~3–4 tháng** | **~170–415 triệu đồng** |

> Đây là kịch bản "thuê đầy đủ nhân sự mới". Nếu đội hackathon hiện tại (Hiến/Ngọc/Quyết/
> Hiếu) tự làm tiếp như một dự án khởi nghiệp — không trả lương thị trường mà góp công theo
> hình thức founder/equity — **chi phí tiền mặt thực tế thấp hơn nhiều**, chủ yếu còn lại là:
> chi phí nội dung sư phạm nếu cần mời giáo viên ngoài đội biên soạn (~20–60 triệu), 1 đợt tư
> vấn bảo mật độc lập trước khi nhận dữ liệu học sinh thật (~10–20 triệu), và thời gian/công
> sức của chính team (không phát sinh chi phí tiền mặt nhưng cần tính vào kế hoạch thời gian).

### 4.4. Việc cần làm để chốt số chính xác

1. Team tự chốt: phần nào tự làm (founder time, chi phí ~0 tiền mặt), phần nào cần thuê ngoài
   (nhất là nội dung sư phạm và tư vấn bảo mật — hai việc cần chuyên môn ngoài năng lực Dev/AI
   hiện có).
2. Lấy báo giá thật cho tư vấn bảo mật/privacy audit từ 1–2 đơn vị trong nước.
3. Xác nhận với giáo viên/chuyên gia cụ thể chi phí biên soạn nội dung theo mạch kỹ năng/khối
   lớp muốn mở rộng.
4. Đối chiếu tổng chi phí hoàn thiện này với doanh thu dự kiến (6–15 triệu đồng/học kỳ/trường,
   `docs/PROJECT_DESCRIPTION.md` mục 10) để ước tính thời gian hoàn vốn khi mở rộng nhiều trường.

### 4.5. Chi phí vận hành khi đã pilot thật (tham khảo thêm)

Sau khi hoàn thiện, chi phí **vận hành hàng tháng/học kỳ** (khác với chi phí xây dựng ở trên)
ở quy mô pilot 1 trường (~100–160 học sinh) ước tính:

| Khoản mục | Ước tính |
|---|---|
| Hạ tầng server (VPS chạy 4 service Docker hiện tại) | ~800.000–2.000.000đ/tháng |
| LLM API runtime (FPT AI Inference, chỉ gọi ở tầng sinh lộ trình/nhận xét, không phải mỗi câu hỏi) | ~vài trăm nghìn – 1,5 triệu đồng/học kỳ (giả định 150 HS × 6 lượt/học kỳ × ~3.000 token; **chưa có bảng giá chính thức từ FPT AI Inference trong repo, cần liên hệ trực tiếp để chốt số**) |
| Vận hành/hỗ trợ giáo viên | ~0đ nếu team tự làm; ~3–5 triệu/tháng nếu thuê 1 người bán thời gian |

Khi mở rộng sang cụm trường/huyện (Giai đoạn 2, `docs/PROJECT_DESCRIPTION.md` mục 10), các
khoản này tăng tuyến tính theo số học sinh, và nên có thêm 1 đợt audit bảo mật độc lập
(~10–20 triệu đồng) trước khi tiếp nhận dữ liệu học sinh quy mô lớn hơn.

## Nguồn

- Email đánh giá BTC VAIC 2026, nhận 2026-07-23.
- Khảo sát codebase repo `v-nexus` (agent Explore, 2026-07-23): cấu trúc dự án, implementation
  AI/BKT, privacy/offline-sync.

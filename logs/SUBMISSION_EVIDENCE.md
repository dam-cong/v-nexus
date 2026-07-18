# Tài liệu chứng minh sử dụng AI (VAIC 2026)

Theo quy định BTC: *"For desktop tools, include session files such as ~/.claude/projects/<project>, ~/.codex/sessions/, or equivalent folders, plus screenshots."*

Công cụ AI sử dụng: **OpenCode** (desktop agent) + **Claude Code** (CLI).

## 1. Session files (bằng chứng phiên làm việc)

| File / Folder | Mô tả |
|---|---|
| `opencode-session/vinc-opencode-2026-07-17.log` | **Session file ngày 17/07/2026** — transcript hội thoại OpenCode lọc riêng cho ngày này (950 KB, 4950 dòng, 14:07→22:05). Đây là tệp tương đương `~/.claude/projects/<project>` cho ngày thi. |
| `claude-session/vinc-claude-2026-07-17.log` | **Session file Claude Code ngày 17/07/2026** (11:30→19:09 giờ VN, UTC+7) — ghép từ 4 phiên Claude Code CLI thật (`~/.claude/projects/-home-hiendc-Documents-VAIC-2026/{7a6e71a2,8f42751a,51386eef,227d4c5c}...jsonl`), mỗi phiên chỉ lấy phần dòng có timestamp thuộc đúng ngày 17/07 giờ VN (lọc theo timestamp gốc, không copy nguyên file) — nối bằng marker `SESSION LOG`/`CONTINUED SESSION LOG` giống quy ước ở file OpenCode. Nội dung: phân tích đề bài, mở rộng phạm vi Tiếng Anh + BKT, đọc docx v2.2 và đồng bộ "chức năng chính" giữa `docs/PROJECT_DESCRIPTION.md`/`docs/PLAN.md`/`docs/timeline.md`. Phần đuôi của phiên `8f42751a` rơi sau nửa đêm (giờ VN) thuộc ngày 18/07 nên **không** đưa vào file này — sẽ nằm trong file `vinc-claude-2026-07-18.log` khi ngày đó kết thúc. |
| `20260717.md` | Bản export nhật ký cộng tác theo ngày (trích từ `docs/ai_log.md`). |
| `../docs/ai_log.md` | Nhật ký cộng tác với AI (bắt buộc nộp cùng bài, xem `docs/RULES.md`). |

### Vị trí session gốc trên máy (equivalent folder)
```
C:\Users\Admin\.local\share\opencode\
├── log\opencode.log              <- transcript chính (dữ liệu 07-17 đã lọc vào opencode-2026-07-17.log)
├── storage\session_diff\         <- session diff JSON
├── tool-output\                  <- output của tool calls
└── snapshot\                      <- snapshot repo (không cần nộp)
```

## 2. Screenshots

BTC yêu cầu kèm ảnh chụp màn hình. Đã chạy `docker-compose up -d --build` và tự động lái
trình duyệt (Playwright headless Chromium) qua toàn bộ các màn hình dưới đây; ảnh nằm ở
`logs/screenshots/`:

- [x] Dashboard admin (`admin@vnexus.vn` / `123456`) → `01-admin-dashboard.png`
- [x] Menu "Người dùng" → sub-tab Học sinh (`02-users-hocsinh.png`) / Giáo viên (`02b-users-giaovien.png`)
- [x] Menu "Đánh giá" → sub-tab Khảo sát (`03a-assessment-khaosat.png`) / Kết quả (`03b-assessment-ketqua.png`) / Bài test (`03c-assessment-baitest.png`)
- [x] Modal sửa học sinh có field "Mật khẩu" (`04-student-edit-modal.png`) + nút 🔑 Reset mật khẩu và toast xác nhận (`04b-reset-password-result.png`)
- [x] Trang Khảo sát đầu vào của học sinh: landing (`05-survey-landing.png`) → chọn cấp độ (`06-survey-chon-capdo.png`) → hướng dẫn (`07-survey-huongdan.png`) → làm bài (`08-survey-lambai.png`) → soát lại (`09-survey-soatlai.png`, modal xác nhận `09b-survey-confirm-modal.png`) → kết quả (`10-survey-ketqua.png`)
- [ ] File `opencode-session/opencode.log` đang mở trong editor (chứng minh session file) — **cần chụp thủ công**, ngoài khả năng của trình duyệt tự động (đây là cửa sổ editor, không phải trang web).

⚠️ **Sai lệch phát hiện khi chạy thử — cần cập nhật thông tin trước khi nộp:**
- Tài khoản `hiendc@gmail.com` / `default123` nêu trong checklist gốc **không tồn tại**
  trong DB hiện tại (`Email hoặc mật khẩu không đúng`). Container `db` đã chạy liên tục
  từ phiên trước (không bị tạo lại bởi `docker-compose up --build`), nên dữ liệu seed
  thực tế trong volume khác với `db/seed.py` (đặt mật khẩu mặc định `123456`) — mật khẩu
  hạt giống thực tế trong volume này cũng không phải `123456` (thử `hs01@vnexus.vn` /
  `123456` cũng sai). Ảnh trên dùng `hs01@vnexus.vn` sau khi admin bấm reset mật khẩu về
  mặc định `88888888` (tính năng ở mục 4). Nếu nộp bài trên một máy chủ/volume Postgres
  **mới, sạch** (chạy đúng `db/seed.py`), thông tin đăng nhập sẽ theo đúng seed
  (`123456`) — cần xác minh lại trên môi trường nộp bài thật, đừng lấy nguyên ảnh/thông
  tin ở đây làm chuẩn nếu volume DB khác.
- Nút "🔑 Reset mật khẩu" không nằm trong modal sửa học sinh như checklist mô tả, mà là
  action riêng trên từng dòng bảng (cột "Thao tác") kèm `confirm()` của trình duyệt —
  đã chụp cả hai để bao quát đủ ý "field Mật khẩu" + "nút Reset".

## 3. Chat session links (online tools)

Dự án dùng tool desktop (OpenCode/Claude Code CLI) nên không có link chat online.
Nếu dùng thêm tool online nào, vui lòng bổ sung link tại đây:

- (trống)

## Ghi chú

- Toàn bộ code được sinh/sửa bởi AI (100% AI-native) — đối chiếu `docs/ai_log.md` với `git log`.
- Các phiên làm việc chính đã được ghi nhận trong `docs/ai_log.md` (Khảo sát đầu vào, sửa icon lucide, quản lý user/password, sắp xếp menu).

---

## 4. HƯỚNG DẪN TÁI HIỆN (Playbook cho dev khác)

Phần này hướng dẫn dev khác (hoặc chính bạn trên máy khác) tái hiện lại các tính năng đã làm,
dựa trên log phiên `opencode-session/vinc-opencode-2026-07-17.log` (chứa cả 2 thiết bị Windows + Linux).

### 4.1. Chuẩn bị & chạy dự án (bắt buộc)

```bash
# 1. Giải nén / clone source
unzip v-nexus.zip && cd v-nexus

# 2. Tạo thư mục data BẮT BUỘC (Dockerfile gateway có COPY docs/data/)
mkdir -p docs/data
# Copy 4 file JSON vào docs/data/:
#   - question-bank.json      (42 câu hỏi)
#   - placement-test.json     (14 câu bài test)
#   - survey-results.json     (5 kết quả BKT)
#   - knowledge-graph.json    (knowledge graph)
# Nếu thiếu -> build gateway sẽ lỗi: COPY docs/data/ ./docs/data/ failed

# 3. Tạo file .env từ mẫu
cp .env.example .env

# 4. Build & chạy toàn bộ (force recreate để lấy code mới)
docker-compose up -d --build --force-recreate

# 5. Kiểm tra
docker-compose ps
```

> ⚠️ **Lỗi thường gặp trên server:** `COPY docs/data/ ./docs/data/` lỗi vì thư mục không tồn tại.
> Fix: tạo `docs/data/` và copy 4 file JSON vào trước khi build.

**Truy cập:**
| Dịch vụ | URL |
|---|---|
| Frontend | http://localhost:8081 |
| Gateway API | http://localhost:8000 |
| MCP Server | http://localhost:8500 |
| Database (Postgres) | localhost:5434 |

**Đăng nhập admin:** `admin@vnexus.vn` / `123456`

### 4.2. Nguyên tắc quan trọng (tránh lỗi)

1. **Gateway & Frontend COPY code lúc build, KHÔNG mount volume.**
   → Mỗi khi sửa code PHẢI `docker-compose build <service>` rồi `up -d`.
   → Chỉ restart (`docker-compose restart`) là KHÔNG đủ — container vẫn chạy code cũ.
2. **Thứ tự build:** sửa code → `docker-compose build` → `docker-compose up -d`.
3. **Không xóa data để tạo mới.** Ưu tiên UPDATE (PUT) hoặc thêm mới (POST) thay vì drop DB.
4. **Auth path:** login ở `/api/auth/login` (không phải `/auth/login`).

### 4.3. Tính năng đã làm (checklist tái hiện)

| STT | Tính năng | File ảnh hưởng | Cách test |
|---|---|---|---|
| 1 | Sửa / xóa câu hỏi | `gateway/app/routes/crud.py` (PUT/DELETE `/api/questions/{id}`), `frontend/src/App.jsx` (modal sửa + nút Xóa) | Vào "Ngân hàng câu hỏi" → Sửa/Xóa |
| 2 | Sửa / xóa bài test | `crud.py` (PUT/DELETE `/api/placement-tests/{id}`) | Vào "Danh sách bài test" → Sửa/Xóa |
| 3 | Thêm/bớt câu hỏi trong bài test | `crud.py` (`PUT /api/placement-tests/{id}/questions` nhận `List[int]`), modal chọn câu hỏi trong detail view | Mở "Chi tiết" bài test → "+ Thêm câu hỏi" (checkbox) hoặc "Xóa" trên hàng |
| 4 | Redesign UI Kết quả kiểm tra | `frontend/src/App.jsx` (tab `test-results`) | Vào "Kết quả kiểm tra" → "Chi tiết" → xem 4 card + mastery bars + gaps + recommendations + bảng câu trả lời |

### 4.4. Các bước làm tính năng "Thêm/bớt câu hỏi trong bài test" (ví dụ chi tiết)

1. Backend đã có sẵn `PUT /api/placement-tests/{id}/questions` (nhận mảng question IDs, xóa link cũ, tạo link mới theo thứ tự).
2. Frontend:
   - Thêm state: `showAddQuestionModal`, `addQuestionSearch`, `addQuestionSkillFilter`, `addQuestionDiffFilter`.
   - Thêm handler `handleSaveTestQuestions(testId, ids)` gọi PUT trên.
   - Thêm handler `handleRemoveQuestionFromTest(testId, qid)` (lọc bớt 1 ID rồi gọi handler trên).
   - Trong detail view: nút "+ Thêm câu hỏi" mở modal; mỗi hàng có nút "Xóa".
   - Modal: bảng danh sách `questions` có checkbox, filter skill/difficulty/search, tick sẵn câu đã có, chọn → lưu ngay.

### 4.5. Các bước làm tính năng "Redesign UI Kết quả kiểm tra"

1. Thay `alert()` bằng state `selectedResult` + detail view.
2. Detail view gồm:
   - 4 thẻ tóm tắt (Điểm / Trình độ / Thời gian / Ngày thi) dùng gradient + border.
   - Cột trái: Mastery — progress bar từng skill, % probability, badge "Thành thạo/Đang học/Yếu".
   - Cột phải: Lỗ hổng (gaps) + Đề xuất (recommendations) — severity/priority badge.
   - Bảng câu trả lời: STT, Mã câu, Kỹ năng, Trả lời, Kết quả (✓/✗), Thời gian, Lỗi sai.
3. Thêm import icon `AlertTriangle`, `Lightbulb` từ `lucide-react`.
4. Rebuild frontend container.

### 4.6. Script tự động hóa setup

Đã có `setup.sh` ở root dự án:
```bash
chmod +x setup.sh && ./setup.sh
```
Script tự động: tạo `docs/data/`, kiểm tra file JSON, dừng container cũ, build + up, hiển thị status.

### 4.7. Xuất log phiên (cho nộp bài)

- Log gốc OpenCode: `C:\Users\Admin\.local\share\opencode\log\opencode.log`
- Đã lọc riêng cho ngày 17/07 → `opencode-session/vinc-opencode-2026-07-17.log`
- Khi làm trên thiết bị khác: **APPEND** (nối tiếp) vào file log cũ, KHÔNG ghi đè.
  Nguyên tắc: giữ data cũ, thêm phần "CONTINUED SESSION LOG - Device X" ở cuối.

#### Quy tắc đặt tên file session theo công cụ AI

Mỗi công cụ AI sinh ra một file session riêng, **không gộp chung** vào file của công cụ khác.
**`<dev>` là tên của người dev — mỗi dev TỰ NHẬP tên mình** (vd: `vinc`, `an`, `binh`...).

| Công cụ | Tên file session | Vị trí gốc trên máy |
|---|---|---|
| OpenCode | `opencode-session/<dev>-opencode-2026-07-17.log` | `C:\Users\Admin\.local\share\opencode\log\opencode.log` |
| Claude Code (CLI) | `claude-session/<dev>-claude-2026-07-17.log` | `~/.claude/projects/<project>/` hoặc `~/.claude.json` |
| Codex | `codex-session/<dev>-codex-2026-07-17.log` | `~/.codex/sessions/` |
| Gemini CLI | `gemini-session/<dev>-gemini-2026-07-17.log` | `~/.gemini/` |
| Copilot | `copilot-session/<dev>-copilot-2026-07-17.log` | theo IDE (`.vscode/` hoặc `~/.github/copilot`) |
| Công cụ khác | `<tool>-session/<dev>-<tool>-2026-07-17.log` | tương đương folder của tool đó |

**Quy tắc:**
1. Dev tự nhập `<dev>` = tên của mình (vd: `vinc`). Không dùng chung một tên.
2. Dùng tool nào → tạo/append file session của tool đó, không đè vào file của tool khác.
3. Format tên: `<dev>-<tên-tool>-YYYY-MM-DD.log`
4. Nếu cùng dev + cùng tool làm trên nhiều thiết bị → APPEND tiếp vào file cũ, giữ nguyên data.
5. Tất cả file session để trong `logs/<tool>-session/` tương ứng.
6. Cập nhật bảng mục 1 (Session files) ở trên mỗi khi có dev/tool mới tham gia.

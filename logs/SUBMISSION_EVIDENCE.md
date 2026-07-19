# Tài liệu chứng minh sử dụng AI (VAIC 2026)

Theo quy định BTC: *"For desktop tools, include session files such as ~/.claude/projects/<project>, ~/.codex/sessions/, or equivalent folders, plus screenshots."*

Công cụ AI sử dụng: **OpenCode** (desktop agent) + **Claude Code** (CLI) + **Gemini** (qua Google
Antigravity IDE, thư mục gốc `~/.gemini/antigravity/brain/<session-id>/`).

## 1. Session files (bằng chứng phiên làm việc)

| File / Folder | Mô tả |
|---|---|
| `opencode-session/vinc-opencode-2026-07-17.log` | **Session file ngày 17/07/2026** — transcript hội thoại OpenCode lọc riêng cho ngày này (950 KB, 4950 dòng, 14:07→22:05). Đây là tệp tương đương `~/.claude/projects/<project>` cho ngày thi. |
| `opencode-session/vinc-opencode-2026-07-18.log` | **Session file ngày 18/07/2026** — transcript OpenCode lọc riêng cho ngày này (379 KB, 1996 dòng, 00:16→23:52 UTC). Chứa: sửa lỗi Nộp bài + obfuscator TDZ, tối ưu luồng làm bài (tự chấm + auto-next 1s), nút Quay lại xem lại nhận xét, progressive loading `PlanBuildingProgress`, và khắc phục DB container chết. |
| `claude-session/vinc-claude-2026-07-17.log` | **Session file Claude Code ngày 17/07/2026** (11:30→19:09 giờ VN, UTC+7) — ghép từ 4 phiên Claude Code CLI thật (`~/.claude/projects/-home-hiendc-Documents-VAIC-2026/{7a6e71a2,8f42751a,51386eef,227d4c5c}...jsonl`), mỗi phiên chỉ lấy phần dòng có timestamp thuộc đúng ngày 17/07 giờ VN (lọc theo timestamp gốc, không copy nguyên file) — nối bằng marker `SESSION LOG`/`CONTINUED SESSION LOG` giống quy ước ở file OpenCode. Nội dung: phân tích đề bài, mở rộng phạm vi Tiếng Anh + BKT, đọc docx v2.2 và đồng bộ "chức năng chính" giữa `docs/PROJECT_DESCRIPTION.md`/`docs/PLAN.md`/`docs/timeline.md`. Phần đuôi của phiên `8f42751a` rơi sau nửa đêm (giờ VN) thuộc ngày 18/07 nên **không** đưa vào file này — đã tách sang `vinc-claude-2026-07-18.log` (xem dòng dưới). |
| `claude-session/vinc-claude-2026-07-18.log` | **Session file Claude Code ngày 18/07/2026** (06:48→23:59 giờ VN, UTC+7) — ghép từ 2 phiên: phần đuôi của `8f42751a-3a73-4d9d-ba51-2b3a4b8cc705` (278 dòng, rơi sau nửa đêm 17→18/07) + phần đầu của `47856fd0-1868-432a-9abd-eede7c9c772e` (1902 dòng, phiên chạy xuyên sang cả 19/07 nên chỉ lấy phần thuộc 18/07). Lọc theo mốc UTC `2026-07-17T17:00:00Z` → `2026-07-18T17:00:00Z` (tương ứng 00:00→24:00 giờ VN ngày 18/07), nối bằng marker `SESSION LOG`/`CONTINUED SESSION LOG` giống file ngày 17/07. Nội dung: migrate curriculum Academy Stars → Global Success, đổi tên thương hiệu V-Nexus School + logo, kế hoạch offline-mode, tạo/triển khai ngân hàng câu hỏi + 6 bộ đề khảo sát, sửa hàng loạt bug (survey submit crash, race condition nút Quay lại, DB schema drift is_roadmap_approved/primary_teacher_id/parent_id, Pydantic NULL-safety), viết `deploy.sh`. |
| `gemini-session/quyet-gemini-2026-07-17.log` | **Session file Gemini (Google Antigravity IDE) ngày 17/07/2026** (dev: `quyet`, ~11:34→17:48 giờ VN, UTC+7) — chuẩn hoá lại từ 2 file thô trong thư mục cũ `Gemini-session/` (tên gốc ghi nhầm tháng `17_6`, timestamp bên trong thực tế là 17/07): `quyet_file_logs_17_6_2026.txt` (3 dòng) nối với `quyet_file_logs_17_6_2026_v2.txt` (270 dòng) bằng marker `SESSION LOG`/`CONTINUED SESSION LOG`, đổi tên theo đúng chuẩn `<dev>-<tool>-YYYY-MM-DD.log` ở mục 4.7. Nội dung: đọc/phân tích dự án v-nexus, tạo `db.sql` + `connector.py` (kết nối PostgreSQL) + API CRUD ban đầu cho học sinh/giáo viên/xếp hạng/role/form khảo sát. |
| `gemini-session/quyet-gemini-2026-07-18.log` | **Session file Gemini (Google Antigravity IDE) ngày 18/07/2026** (dev: `quyet`) — đổi tên từ `quyet_log_18_7.md` (thư mục cũ `Gemini-session/`) theo đúng chuẩn đặt tên; đây là transcript markdown xuất trực tiếp từ IDE (không có timestamp nội bộ từng dòng nên không xác minh được khung giờ VN chính xác, tin theo tên file gốc `18_7`), nội dung giữ nguyên. Nội dung: dashboard học sinh dạng bento grid, tính điểm BKT ở backend, trang kết quả + theo dõi tiến độ, tích hợp routing/auto-redirect vào `App.jsx`. |
| `20260717.md` | Bản export nhật ký cộng tác theo ngày (trích từ `docs/ai_log.md`). |
| `20260718.md` | Bản export nhật ký cộng tác theo ngày 18/07/2026 — tóm tắt các đầu việc khảo sát đầu vào + progressive loading. |
| `../docs/ai_log.md` | Nhật ký cộng tác với AI (bắt buộc nộp cùng bài, xem `docs/RULES.md`). |

### Vị trí session gốc trên máy (equivalent folder)
```
C:\Users\Admin\.local\share\opencode\
├── log\opencode.log              <- transcript chính (dữ liệu 07-17 đã lọc vào opencode-2026-07-17.log)
├── storage\session_diff\         <- session diff JSON
├── tool-output\                  <- output của tool calls
└── snapshot\                      <- snapshot repo (không cần nộp)

~/.gemini/antigravity/brain/<session-id>/     <- máy dev "quyet" (Linux, /home/pytathon/...)
├── implementation_plan.md        <- kế hoạch AI tạo ra trước khi code
└── walkthrough.md                <- tóm tắt thay đổi sau khi hoàn thành
```

## 2. Screenshots

BTC yêu cầu kèm ảnh chụp màn hình. Bộ ảnh dưới đây **chụp lại ngày 19/07/2026** (Claude
Code + Playwright headless Chromium, chạy `--no-sandbox` trong môi trường không có
quyền root) trên `docker-compose up -d --build` **từ database sạch** (`down -v` rồi
`up` lại) — xác nhận login theo đúng seed mặc định (`db/seed.py`, mật khẩu `123456`)
hoạt động thật, không cần biết mật khẩu tùy chỉnh nào khác. Ảnh nằm ở `logs/screenshots/`:

- [x] Dashboard admin (`admin@vnexus.vn` / `123456`), layout đã sửa hết khoảng trống 2
      bên → `01-admin-dashboard.png`
- [x] Menu "Người dùng" → sub-tab Học sinh (`02-users-hocsinh.png`) / Giáo viên (`02b-users-giaovien.png`)
- [x] Menu "Đánh giá" → sub-tab Khảo sát (`03a-assessment-khaosat.png`) / Kết quả
      (`03b-assessment-ketqua.png`) / Bài test (`03c-assessment-baitest.png`) / chi tiết
      1 kết quả cụ thể (`03d-assessment-ketqua-chitiet.png`, xem kế hoạch AI dạng
      timeline, không còn là JSON thô)
- [x] Modal sửa học sinh có field "Mật khẩu" (`04-student-edit-modal.png`) + nút 🔑 Reset
      mật khẩu và toast xác nhận (`04b-reset-password-result.png`) — **giữ nguyên từ lần
      chụp 18/07**, tính năng chưa đổi nên không chụp lại.
- [x] **Mới — Cấu hình LLM đa nhà cung cấp** (`11-settings-modal-llm.png`): modal admin
      chọn Chế độ LLM, minh họa chọn "Google Gemini" tự điền gợi ý Base URL/Model —
      trước đây chỉ có FPT AI cứng, giờ chọn được cả Gemini/OpenAI mà vẫn tự cấu hình
      được (không hardcode).
- [x] Trang Khảo sát đầu vào của học sinh: landing (`05-survey-landing.png`) → chọn cấp
      độ (`06-survey-chon-capdo.png`, giữ nguyên 18/07) → hướng dẫn
      (`07-survey-huongdan.png`, giữ nguyên 18/07) → làm bài (`08-survey-lambai.png`) →
      soát lại (`09-survey-soatlai.png`, modal xác nhận `09b-survey-confirm-modal.png`,
      giữ nguyên 18/07) → kết quả (`10-survey-ketqua.png`)
- [x] **Mới — Lịch sử bài đánh giá** của học sinh: danh sách (`12-history-list.png`) →
      chi tiết 1 bài (`13-history-detail-chitiet.png`) — vừa sửa xong bug hiển thị kế
      hoạch AI dạng JSON thô + cột "Đáp án em chọn" bị trống, giờ hiện đúng.
- [ ] File `opencode-session/opencode.log` đang mở trong editor (chứng minh session file) — **cần chụp thủ công**, ngoài khả năng của trình duyệt tự động (đây là cửa sổ editor, không phải trang web).

⚠️ **Đã xác minh lại (19/07/2026), khác với ghi chú cũ ngày 18/07 ở trên:**
- Trên **database sạch** (`docker-compose down -v && up -d --build`), tài khoản seed mặc
  định hoạt động đúng như `db/seed.py`: `admin@vnexus.vn`/`hs0X@vnexus.vn`/
  `teacherX@vnexus.vn` đều dùng mật khẩu `123456`. Ghi chú cũ về `hiendc@gmail.com`/
  `default123` không tồn tại **chỉ đúng với volume DB cũ, đã qua nhiều lần seed/migrate
  chồng lên nhau** — trên môi trường nộp bài thật (deploy mới hoàn toàn), cứ dùng seed
  mặc định là chạy đúng, không cần trò reset mật khẩu thủ công như ghi chú cũ.
- Trong lúc làm việc hôm nay, **production thật (`v-nexus.editech.vn`) từng bị lỗi 500**
  ở `GET /api/test-results` do dữ liệu cũ có `user_id NULL` (5 dòng orphan từ migration
  `student_id → user_id` không khớp hết) — đã sửa (`TestResultResponse` chịu được NULL)
  và đã deploy lại. Nếu chụp ảnh trực tiếp trên server thật thay vì local, nhớ kiểm tra
  lại tab "Đánh giá > Kết quả" không còn lỗi 500 trước khi coi ảnh là bằng chứng cuối.

## 3. Chat session links (online tools)

Dự án dùng tool desktop (OpenCode/Claude Code CLI/Gemini qua Google Antigravity IDE) nên không có link chat online.
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

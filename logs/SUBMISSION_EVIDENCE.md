# Tài liệu chứng minh sử dụng AI (VAIC 2026)

Theo quy định BTC: *"For desktop tools, include session files such as ~/.claude/projects/<project>, ~/.codex/sessions/, or equivalent folders, plus screenshots."*

Công cụ AI sử dụng: **OpenCode** (desktop agent) + **Claude Code** (CLI).

## 1. Session files (bằng chứng phiên làm việc)

| File / Folder | Mô tả |
|---|---|
| `opencode-session/opencode-2026-07-17.log` | **Session file ngày 17/07/2026** — transcript hội thoại OpenCode lọc riêng cho ngày này (950 KB, 4950 dòng, 14:07→22:05). Đây là tệp tương đương `~/.claude/projects/<project>` cho ngày thi. |
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

## 2. Screenshots (cần bổ sung thủ công)

BTC yêu cầu kèm ảnh chụp màn hình. Vui lòng chụp và thêm vào thư mục này (`logs/screenshots/`):

- [ ] Màn hìnhDashboard admin (`admin@vnexus.vn` / `123456`)
- [ ] Menu "Người dùng" → sub-tab Học sinh / Giáo viên
- [ ] Menu "Đánh giá" → sub-tab Khảo sát / Kết quả / Bài test
- [ ] Modal sửa học sinh có field "Mật khẩu" + nút 🔑 Reset mật khẩu
- [ ] Trang Khảo sát đầu vào của học sinh (`hiendc@gmail.com` / `default123`): landing → chọn cấp độ → hướng dẫn → làm bài → soát lại → kết quả
- [ ] File `opencode-session/opencode.log` đang mở trong editor (chứng minh session file)

## 3. Chat session links (online tools)

Dự án dùng tool desktop (OpenCode/Claude Code CLI) nên không có link chat online.
Nếu dùng thêm tool online nào, vui lòng bổ sung link tại đây:

- (trống)

## Ghi chú

- Toàn bộ code được sinh/sửa bởi AI (100% AI-native) — đối chiếu `docs/ai_log.md` với `git log`.
- Các phiên làm việc chính đã được ghi nhận trong `docs/ai_log.md` (Khảo sát đầu vào, sửa icon lucide, quản lý user/password, sắp xếp menu).

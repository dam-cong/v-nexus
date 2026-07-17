# Nhật ký cộng tác với AI

Bắt buộc nộp cùng bài (xem thể lệ 2.2 — mục "Bài nộp"). Ghi lại **mọi** phiên làm việc
có AI tham gia tạo/sửa code, không chỉ những phiên "quan trọng". Đây là bằng chứng chính
cho tiêu chí *Kiến trúc AI-Native & Đổi mới sáng tạo* và cam kết 100% AI-native.

## Cách ghi

Mỗi dòng = một phiên trao đổi có kết quả cụ thể (không ghi tin nhắn chit-chat qua lại).

| Thời gian | Người | Công cụ AI | Yêu cầu gửi AI (tóm tắt) | Kết quả / Quyết định | Review bởi |
|---|---|---|---|---|---|
| 2026-07-16 15:09 | Hiến | Claude Code | Dựng khung kiến trúc V-Nexus (Gateway + Planner Agent + Tool Registry + MCP Server mẫu + PostgreSQL Connector + frontend chat + docs nộp bài khung) | Scaffold ban đầu, đã build/chạy thử `docker compose up` xác nhận healthy — commit `adf636c` | Hiến |
| 2026-07-16 15:36 | Hiến | Claude Code | Tổng hợp quy định BTC thành checklist tuân thủ (quy mô đội, deadline, cam kết AI-native, tiêu chí chấm điểm) | Tạo `docs/RULES.md` — commit `1adae23` | Hiến |
| 2026-07-17 11:37 | Hiến | Claude Code | Đọc & phân tích đề bài Vbee Đề 8 (slide/giáo án → video bài giảng) từ PDF BTC cung cấp | Tạo `docs/PHAN_TICH_DE_8.md` (<5000 ký tự theo yêu cầu) — commit `e9f867b` | Hiến |
| 2026-07-17 13:24 | Hiến | Claude Code | Đổi hướng sang đề bài Gia sư thích ứng thu hẹp khoảng cách năng lực (thay Đề 8) — phân tích yêu cầu, đổi tên dự án thành V-Nexus Tutor, phân bổ công việc theo 5 vai trò (PM/BA/Dev/AI/Cố vấn) | Tạo `docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md`, cập nhật README/PROJECT_DESCRIPTION/timeline, xóa tài liệu Đề 8 không còn dùng — commit `d94396f` | Hiến |
| 2026-07-17 14:28 | Hiến | Claude Code | Mở rộng phạm vi (môn Tiếng Anh, CV học viên, chương trình cấp 1-2-3), yêu cầu thiết kế cơ chế AI khác biệt (không chỉ "gọi LLM"), thêm dashboard phụ huynh và bot hỏi-đáp | Thiết kế Bayesian Knowledge Tracing + adaptive testing (CAT) + Bayesian prior/posterior fusion làm lõi chẩn đoán; LLM giới hạn ở vai trò trích xuất/chấm chủ quan/diễn giải; bot tái dùng khung Planner Agent + Tool Registry đã dựng sẵn — commit `f62b8e9` | Hiến |
| 2026-07-17 21:00 | Hiến | Claude Code | Tùy chỉnh UI bảng kết quả kiểm tra: thêm cột "Độ khó" (easy/medium/hard), giảm cột "Lỗi sai" còn 30%, thêm badge trạng thái mastery (Rất yếu/Yếu/Đang học/Khá/Thành thạo), sắp xếp gaps theo severity, thêm icon ⚠ cho starter level, highlight weak students trên dashboard | 7 cải thiện UI trên App.jsx + App.css — Chưa commit (đang phát triển) | Hiến |
| 2026-07-17 22:30 | Hiến | Claude Code | Responsive mobile cho toàn bộ UI: hamburger menu toggle sidebar (ẩn/hiện), off-canvas sidebar trên mobile, stacked grids (stats/charts/dashboard/detail), horizontal scroll tables, compact header/search/filter, stacked modals/forms | Thêm ~300 dòng responsive CSS media queries (≤768px, ≤480px), chuyển inline styles sang CSS classes (.detail-score-val, .detail-level-val, .modal-form-grid, .header-search-filter, .question-header-filters), rebuild Docker frontend — Chưa commit | Hiến |
| 2026-07-18 10:15 | Hiến | OpenCode | Xây dựng tính năng Khảo sát đầu vào cho học sinh: 6 màn hình (landing, chọn cấp độ, hướng dẫn, làm bài, soát lại, kết quả) dựa trên 7 file mockup HTML; Icon dùng Material Symbols Outlined | Tạo `StudentSurvey.jsx` (~840 dòng) + `StudentSurvey.css` (~1500 dòng); tích hợp vào App.jsx (sidebar học sinh, tab Khảo sát đầu vào); thêm backend `POST /api/placement-tests/{id}/submit` lưu kết quả + cập nhật ranking — Chưa commit | Hiến |
| 2026-07-18 11:20 | Hiến | OpenCode | Sửa lỗi icon Khảo sát không hiện (Material Symbols font từ Google Fonts CDN bị chặn trong container Docker) → chuyển toàn bộ 34 icon sang `lucide-react` (bundle local) | Thay `Icon` component dùng `lucide-react`, map tên icon cũ sang component tương đương; rebuild frontend container — Chưa commit | Hiến |
| 2026-07-18 14:05 | Hiến | OpenCode | Quản lý user cho admin: đổi/sửa mật khẩu | Backend: thêm `password` vào schema `StudentUpdate`/`TeacherUpdate`/`StudentCreate`/`TeacherCreate`; PUT `/students|teachers/{id}` hash password khi có; POST `/students|teachers/{id}/reset-password` reset về `default123` (admin-only). Frontend: thêm field "Mật khẩu" vào modal học sinh/giáo viên (để trống = giữ nguyên), nút 🔑 Reset mật khẩu có confirm trong bảng — Chưa commit | Hiến |
| 2026-07-18 15:40 | Hiến | OpenCode | Sắp xếp lại menu admin: gom 8 mục thành 5 mục theo mục đích | Sidebar admin: Dashboard, **Người dùng** (sub-tab Học sinh/Giáo viên), Bảng xếp hạng, **Đánh giá** (sub-tab Khảo sát/Kết quả/Bài test), Ngân hàng câu hỏi. Thêm state `userSubTab`/`assessmentSubTab`, sub-tab bar UI + CSS `.subtab-bar`/`.subtab-btn`. Sửa cả icon `auto_stories` (material-symbols) thành `Sparkles` (lucide) ở menu học sinh — Chưa commit | Hiến |

## Quy tắc

- Mỗi thành viên tự thêm dòng khi dùng AI để tạo/sửa code — không dồn lại ghi cuối ngày.
- Cột "Quyết định" ghi rõ nếu bạn **sửa lại** hoặc **từ chối** đề xuất của AI và vì sao —
  đây là phần giám khảo quan tâm nhất, không phải việc AI viết được gì.
- Khi thay Domain Adapter theo đề bài thật (xem `domain/adapter.py`), ghi lại prompt đã
  dùng để sinh phiên bản mới.
- Trước khi nộp bài: đối chiếu log này với `git log` — mọi commit có thay đổi code nên có
  ít nhất một dòng tương ứng ở đây.

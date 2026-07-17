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
| 2026-07-17 (chiều) | Hiến | Claude Code | Yêu cầu template auth có sẵn (tránh viết đăng nhập/phân quyền từ đầu); triển khai Phase 1 theo `docs/KE_HOACH_TRIEN_KHAI.md`: đồ thị tri thức + BKT engine + 4 tool + Domain Adapter + REST routes | Chọn `fastapi-users` (JWT + role student/teacher/parent). Code: `domain/bkt.py`, `domain/knowledge_graph.py`, `domain/mastery_store.py`, `domain/practice_selector.py`, `domain/dashboard_queries.py`, `domain/adaptive_tutor_adapter.py` (thay `sme_innovation_adapter.py` — đã xóa vì không còn dùng), `gateway/app/auth.py`, 4 route mới, `db/seed.py`. **Tự phát hiện & sửa 1 bug thật qua test**: thuật toán lan truyền ngược ban đầu tính lại `evidence_strength` từ mastery đã bị hạ của nút trung gian → compounding kép khiến tổ tiên xa bị hạ mạnh hơn tổ tiên gần, ngược với thiết kế "suy giảm theo depth". Sửa: truyền 1 `evidence_strength` gốc xuyên suốt đệ quy, chỉ nhân `0.6^depth`. 20/20 test pass; xác minh thủ công qua `docker compose up` + `db/seed.py`: đăng ký/đăng nhập, chẩn đoán 3 câu sai liên tiếp → lan truyền đúng qua 3 tầng đồ thị, dashboard giáo viên/phụ huynh trả đúng dữ liệu, phụ huynh bị 403 khi cố xem học sinh khác. | Hiến |

## Quy tắc

- Mỗi thành viên tự thêm dòng khi dùng AI để tạo/sửa code — không dồn lại ghi cuối ngày.
- Cột "Quyết định" ghi rõ nếu bạn **sửa lại** hoặc **từ chối** đề xuất của AI và vì sao —
  đây là phần giám khảo quan tâm nhất, không phải việc AI viết được gì.
- Khi thay Domain Adapter theo đề bài thật (xem `domain/adapter.py`), ghi lại prompt đã
  dùng để sinh phiên bản mới.
- Trước khi nộp bài: đối chiếu log này với `git log` — mọi commit có thay đổi code nên có
  ít nhất một dòng tương ứng ở đây.

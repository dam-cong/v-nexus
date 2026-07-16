# Timeline 48 giờ — V-Nexus (17–19/7/2026)

Dựa trên tài liệu "Việc phải làm ngay (70% thời gian)". Nguyên tắc xuyên suốt:
**đừng tối ưu, đừng làm đẹp, đừng thêm agent thứ hai** — chỉ cần chạy được đến khi có
đề bài thật, rồi dồn lực vào Domain Adapter.

## Trước giờ G (đến 11:00 17/7)

- [x] Dựng bộ khung V-Nexus (6–8 giờ) — **đã xong trong repo này**: FastAPI Gateway,
      Planner Agent, Tool Registry, MCP Server mẫu, PostgreSQL Connector, frontend chat.
- [ ] `docker compose up --build` chạy được end-to-end trên máy mỗi thành viên.
- [ ] Chốt tên đội, xác nhận thành viên trước 11:00 (thể lệ mục "Chốt đội").

## Giờ 0–8 (nhận đề bài → giải pháp thô)

| Vai trò | Việc chính |
|---|---|
| Dev (AI) | Đọc đề bài, viết `domain/<ten_de_bai>_adapter.py` thay `SMEInnovationAdapter`, nối tool thật vào Tool Registry / MCP Server |
| Dev (hạ tầng) | Cập nhật schema `db/models.py` theo dữ liệu đề bài, seed dữ liệu mẫu |
| Design | Wireframe luồng chat chính, xác định 1 happy path duy nhất để demo |
| Business | Viết phần Vấn đề / Người dùng / Business case trong `docs/PROJECT_DESCRIPTION.md` |

## Giờ 8–32 (xây & mentoring)

- Dev: hoàn thiện luồng chính, KHÔNG thêm tính năng phụ.
- AI: tinh chỉnh system prompt + tool description để giảm ảo giác (đối chiếu tiêu chí
  "An toàn AI, Grounding & Độ tin cậy").
- Business/Design: chuẩn bị outline slide (`docs/pitch-outline.md` — tạo khi cần), thu
  thập feedback mentor, điều chỉnh hướng nếu mentor chỉ ra sai lệch.
- Cả đội: mỗi thành viên tự ghi `docs/AI_LOG.md` khi dùng AI — đừng dồn lại cuối.

## Giờ 32–44 (hoàn thiện & đóng gói)

- Deploy live URL (Docker Compose lên VPS/cloud, hoặc dịch vụ PaaS).
- Quay demo video ≤ 5 phút.
- Hoàn thiện `docs/PROJECT_DESCRIPTION.md`, README, slide thuyết trình.
- Tự chấm điểm chéo theo `docs/scoring-checklist.md`.

## Giờ 44–48 (nộp bài)

- Nộp đủ 5 hạng mục: Presentation slides, Demo video (≤5 phút), GitHub repo (public),
  Live deployed URL, Project description.
- Kiểm tra repo public, URL live còn chạy, video xem được không cần quyền riêng tư.

# Kế hoạch: Đổi tên hiển thị dự án — "V-Nexus (Tutor)" → "V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform"

> Tài liệu kế hoạch kỹ thuật cho dev thực hiện. Chưa có code nào được thay đổi tại thời điểm viết
> (2026-07-18). Người viết plan không tự triển khai.

## Phạm vi (đã chốt với team)

**Chỉ đổi tên hiển thị** (title trang, header/logo UI, tiêu đề tài liệu markdown). **Không đụng**
định danh hạ tầng kỹ thuật:
- docker-compose (DB name/credentials `vnexus`, tên container/volume)
- git remote (`github-vnexus`, `dam-cong/v-nexus`)
- tên thư mục repo `v-nexus/`
- class Python `VNexusTutorAdapter` (`domain/sme_innovation_adapter.py`)
- localStorage key `vnexus_token`/`vnexus_user`, custom event `vnexus:refresh-roadmap`
  (`frontend/src/api.js`, `StudentRoadmap.jsx`)
- domain email demo `@vnexus.vn` (tài khoản mẫu trong `db/seed.py`, `docs/data/survey-results.json`)
- FastAPI app title trong `gateway/app/main.py` (chỉ hiện ở Swagger UI `/docs`, coi là bán-hạ-tầng)

Lý do giới hạn phạm vi: đổi các định danh trên cần deploy lại, đổi credentials DB đang chạy, có
thể ảnh hưởng git remote/push — rủi ro cao và không cần thiết cho mục tiêu rebrand hiển thị.

## Quy ước đặt tên

- **Tên đầy đủ** `"V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform"` — dùng ở các điểm chạm
  đầu tiên/quan trọng: title `README.md`, title `docs/PROJECT_DESCRIPTION.md`, `<title>` trang web
  (`frontend/index.html`), màn hình đăng nhập (`Login.jsx`).
- **Tên ngắn** `"V-NEXUS SCHOOL"` — dùng ở nơi lặp lại nhiều/không gian hẹp: header/footer app
  (`App.jsx`), tiêu đề các file docs khác, mockup thiết kế. Header app hiện khá hẹp về layout nên
  bắt buộc dùng tên ngắn ở đó, không dùng tên đầy đủ.

## Danh sách vị trí cần sửa (đã khảo sát, chưa sửa)

**Frontend (React):**
- `frontend/index.html:9` — `<title>V-Nexus Tutor - Gia sư thích ứng</title>` → tên đầy đủ
- `frontend/src/pages/Login.jsx:57` — logo/heading "V-Nexus Tutor" → tên đầy đủ (giữ nguyên các
  email demo hiển thị bên dưới — đó là dữ liệu tài khoản, không phải branding, nằm ngoài phạm vi)
- `frontend/src/StudentSurvey.jsx:285` — `<h2>Cùng V-Nexus Tutor khám phá trình độ Tiếng Anh của
  em!</h2>` → tên ngắn
- `frontend/src/App.jsx:682,789` — header/footer "V-Nexus Tutor" → tên ngắn

**Mockup thiết kế tĩnh (giám khảo có thể xem):**
- `docs/danh-gia/code-01.html` .. `code-07.html` — 5/7 file có tên: trong `<title>` (code-03.html,
  code-05.html) hoặc trong nội dung (code-01.html, code-04.html) → thay theo quy ước trên

**Tài liệu markdown (title/heading):**
- `README.md` — dòng 1 (title chính), 45, 83-84, 128 (nhắc lại trong nội dung)
- `docs/PROJECT_DESCRIPTION.md` — dòng 1, 7, 16, 100, 106, 157
- `docs/PLAN.md` — dòng 1 (`# V-Nexus Tutor — Kế hoạch triển khai nghiệp vụ`)
- `docs/timeline.md` — dòng 1
- `docs/ai-danh-gia.md` — dòng 1
- `docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md` — dòng 53
- `docs/AI_LOG.md` — dòng 13, 16
- `docs/danh-gia/DESIGN.md` — dòng 2 (`name: V-Nexus Tutor Design System`)
- `docs/RULES.md` — dòng 56

**Bỏ qua (không phải branding, là tham chiếu file thật trên đĩa):** mọi chỗ chỉ nhắc tên file
`docs/V-Nexus_Content_Workbook_1.xlsx` (VD trong `docs/plan-migration-global-success.md`) — đây là
tên file, không phải tên hiển thị dự án, không đổi.

## Việc cần làm
1. Sửa các vị trí hiển thị ở trên theo đúng quy ước tên đầy đủ/tên ngắn.
2. Ở `README.md` và `docs/PROJECT_DESCRIPTION.md`, chèn tagline "AI-powered Adaptive Learning
   Platform" rõ ràng ít nhất 1 lần ở đầu tài liệu — không cần lặp lại toàn văn ở mọi heading phụ
   bên trong, chỉ cần title chính đầy đủ.
3. Với các file mockup tĩnh (`docs/danh-gia/code-*.html`), chỉ sửa `<title>` và các đoạn text hiển
   thị trực tiếp, không cần sửa comment/class name nội bộ trong các file đó.

## Kiểm tra sau khi triển khai
- Chạy `npm run dev` trong `frontend/`, mở app: xác nhận tab trình duyệt hiện tên đầy đủ, màn hình
  đăng nhập hiện tên đầy đủ, header trong app (sau khi đăng nhập) hiện tên ngắn không vỡ layout.
- Xem lại `README.md` và `docs/PROJECT_DESCRIPTION.md` từ đầu — tên mới phải nhất quán, không còn
  sót "V-Nexus Tutor" ở các heading chính.
- Grep lại toàn repo (loại trừ venv/node_modules/dist) tìm "V-Nexus Tutor" để xác nhận không sót vị
  trí hiển thị nào ngoài danh sách trên.

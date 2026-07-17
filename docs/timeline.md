# Timeline & phân bổ công việc — V-Nexus Tutor (17–19/7/2026)

## Team

| Tên | Vai trò |
|---|---|
| Hiến | PM |
| Ngọc | BA |
| Quyết | Dev |
| Hiếu | AI |
| Dũng | Cố vấn |

⚠️ **Kiểm tra thể lệ:** đội 2–6 thành viên, tất cả phải **đã xác nhận** (xem
`docs/RULES.md` mục 1). Nếu Dũng chỉ là cố vấn không đăng ký thi (khác mentor do BTC bố
trí tại Genius Station), **không đưa tên vào slide/credit như thành viên đội thi** —
chỉ ghi nhận nội bộ. Nếu Dũng thi cùng đội, cần xác nhận như 4 người còn lại trước
11:00 17/7.

## Mốc nộp bài bắt buộc (không gia hạn)

| Mốc | Hạn | Nội dung |
|---|---|---|
| Checkpoint 1 | 11:00 Thứ Bảy 18/7 | Tên dự án + mô tả |
| Checkpoint 2 | 23:00 Thứ Bảy 18/7 | Live URL + GitHub repo |
| Final | 11:00 Chủ Nhật 19/7 | Đủ 5 hạng mục: slide, demo video ≤5', repo public, URL live, project description |

## ⚠️ Việc chặn đầu tiên — quyết định kiến trúc

Mô tả giải pháp đã chốt (`docs/PROJECT_DESCRIPTION.md` mục 4) cam kết **PWA, chẩn đoán
chạy on-device/offline**. Khung kỹ thuật hiện tại (`gateway/`, `agent/`, `frontend/`
Streamlit) được dựng cho kiến trúc chat qua cloud LLM — **không khớp** cam kết PWA
offline-first.

**Hiến + Quyết phải quyết định ngay** (trước khi AI/Dev bắt đầu code phần khác):
- Giữ Streamlit + backend cloud, bỏ cam kết "offline hoàn toàn" trong mô tả (nói rõ
  trong pitch là hướng mở rộng), **hoặc**
- Build PWA thật (frontend offline-capable, IndexedDB/local storage, sync khi có mạng)
  — đúng cam kết nhưng tốn thời gian dựng lại frontend từ đầu.

Quyết định này quyết định toàn bộ phần việc của Quyết và Hiếu bên dưới — làm trong
1–2 giờ đầu, không để trôi sang ngày 2.

## Phân bổ công việc theo từng người

### Hiến — PM
- Chốt kiến trúc cùng Quyết (việc chặn đầu tiên ở trên).
- Theo dõi 3 mốc nộp bài, không để trôi deadline — đặc biệt Checkpoint 2 (23:00 T7) vì
  không gia hạn.
- Enforce `docs/AI_LOG.md`: nhắc cả team ghi log liên tục, không dồn cuối.
- Trước Final: chạy checklist `docs/scoring-checklist.md` + `docs/RULES.md`, đảm bảo
  repo public, URL live còn chạy tại thời điểm nộp.
- Điều phối lịch ngủ/nghỉ luân phiên trong 48h, tránh cả team kiệt sức cùng lúc trước
  Demo Day.

### Ngọc — BA
- Chốt phạm vi demo cụ thể: rà soát/bổ sung danh sách kỹ năng theo từng Unit trong mạch
  **Từ vựng theo chủ đề → Mẫu câu cơ bản → Đọc hiểu đoạn ngắn, Tiếng Anh lớp 3–4 (GDPT
  2018, bám cấu trúc SGK Global Success)** — đối chiếu với đồ thị kỹ năng đã có
  (`skill_graph_seed.json`) để đảm bảo đủ quan hệ tiên quyết xuyên khối lớp 3–4 cho
  Hiếu dựng thuật toán truy gốc.
- Soạn 5–10 câu hỏi mẫu cho mỗi kỹ năng (dữ liệu mock, không dùng dữ liệu học sinh thật
  — đúng ràng buộc `docs/RULES.md` mục dữ liệu).
- Viết/hoàn thiện mục 6 (Business case & Pilot) trong `PROJECT_DESCRIPTION.md` — khai
  thác chi tiết founder trung tâm đào tạo 12 năm đã có ở mục 9.
- Chuẩn bị nội dung pitch deck (vấn đề → giải pháp → demo → business case) và câu trả
  lời dự kiến cho Q&A 2 phút ở Vòng 3.
- Định nghĩa 2–3 persona học sinh mẫu (khác trình độ) để Dev/AI test luồng chẩn đoán.

### Quyết — Dev
- Sau khi chốt kiến trúc cùng Hiến: dựng frontend (PWA hoặc giữ Streamlit tuỳ quyết
  định), local storage/sync nếu chọn hướng offline.
- Cập nhật `db/models.py` theo schema thật: học sinh, kết quả bài làm, gap đã chẩn đoán.
- Dashboard giáo viên: heatmap kỹ năng theo lớp, nhóm học sinh cùng gap, xếp hạng ưu
  tiên, cảnh báo lỗ hổng diện rộng — map vào tool `teacher_dashboard_query` (xem
  `docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md`).
- Deploy live URL sớm (trước Checkpoint 2, 23:00 T7) — không để dồn sát Final.
- `docker compose up --build` chạy được end-to-end trên máy mọi thành viên.

### Hiếu — AI
- Dựng đồ thị tri thức tiên quyết (knowledge graph) cho phạm vi Ngọc chốt — node = kỹ
  năng, edge = quan hệ tiên quyết, gắn mã bài học GDPT 2018.
- Thiết kế thuật toán truy gốc (root-cause traversal): từ câu sai → suy ngược đồ thị →
  xác định kỹ năng nền còn thiếu, minh bạch/giải thích được (không hộp đen) — đúng cam
  kết "điểm khác biệt #1" trong mô tả giải pháp.
- Tool `generate_practice_path`: sinh lộ trình luyện tập từ gap sâu nhất đi lên.
- Pipeline số hóa nội dung giáo viên giỏi: trích xuất + gắn nhãn kỹ năng cho bài giảng
  mẫu (mock trong phạm vi demo).
- Viết `domain/adaptive_tutor_adapter.py` implement `DomainAdapter`, thay
  `domain/sme_innovation_adapter.py` — nối tool vào Tool Registry.
- Tinh chỉnh prompt để giảm ảo giác, đối chiếu tiêu chí "An toàn AI, Grounding & Độ tin
  cậy" — chẩn đoán phải dựa đồ thị + dữ liệu, không để LLM tự suy đoán gap.

### Dũng — Cố vấn
- Review kiến trúc + phạm vi demo ngay sau quyết định chặn đầu tiên (giờ 2–3) — góp ý
  tính khả thi trong quỹ thời gian còn lại.
- Kiểm tra tính sư phạm của đồ thị tri thức và câu hỏi mẫu (Ngọc + Hiếu dựng) — đây là
  rủi ro dễ sai nhất vì cần chuyên môn giáo dục thật.
- Nghe thử pitch trước Final, phản biện như giám khảo Vòng 3 (Q&A 2 phút).

## Nguyên tắc xuyên suốt

- Đừng tối ưu, đừng làm đẹp sớm — ưu tiên 1 mạch kiến thức chạy trọn vẹn end-to-end
  (chẩn đoán → lộ trình → dashboard) hơn là nhiều mạch dở dang.
- Mỗi người tự ghi `docs/AI_LOG.md` khi dùng AI, ngay lúc làm — không dồn cuối giờ.
- Checkpoint 2 (23:00 T7, URL+repo) là mốc thực tế quan trọng nhất để né rủi ro — nếu
  trễ, không còn cơ hội sửa trước Final.

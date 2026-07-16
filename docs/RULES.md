# Quy định BTC — VAIC 2026 (tránh vi phạm)

Tổng hợp từ thể lệ chính thức BTC gửi. Đây là checklist "được làm / không được làm" —
đọc trước khi code, không phải đọc sau khi nộp bài.

## 1. Điều kiện đội thi

- **Quy mô đội:** 2–6 thành viên. Không thêm người sau khi chốt đội.
- **Chốt đội:** xác nhận tên đội + danh sách thành viên **trước 11:00, 17/7/2026**.
  Đăng ký/xét duyệt/thẩm định — **không tự động nhận**.
- **Điều kiện tham gia:** chỉ hacker **đã được xác nhận** mới được tính hợp lệ. Người
  chưa xác nhận không được tính vào đội, không được xuất hiện trong bài nộp/slide.

⚠️ Vi phạm thường gặp: thêm thành viên "hỗ trợ" không đăng ký/không xác nhận vào slide
hoặc credit — coi như gian lận thành phần đội.

## 2. Thời gian & địa điểm

- 48 giờ, **17–19/7/2026**, tại FPT Tower, Cầu Giấy, Hà Nội.
- Đề bài chính thức công bố **11:00, 17/7/2026** — trước đó chỉ được chuẩn bị hạ tầng
  chung (khung kỹ thuật), **không được biết trước và code sẵn theo 1 đề bài cụ thể**.

## 3. Cam kết 100% AI-native — ĐÂY LÀ QUY TẮC CỐT LÕI

- **Toàn bộ mã nguồn phải do AI tạo mới.** Thư viện có sẵn (pip, npm...) được phép dùng
  bình thường — quy định chỉ áp dụng cho code do đội viết/sinh ra.
- Sản phẩm phải **AI-first ngay từ đầu** — AI là lõi sản phẩm, không phải tính năng gắn
  thêm vào một app CRUD thông thường.
- Tính AI-native được chấm qua **2 kênh bắt buộc**:
  1. Hệ thống chấm điểm AI (Vòng 1 — AI sơ loại)
  2. **Nhật ký cộng tác với AI** (`docs/AI_LOG.md`) — do người chấm đọc trực tiếp

⚠️ Vi phạm thường gặp:
- Tự tay viết code rồi mới nhờ AI "gia công" câu chữ — không tính là AI-native thật.
- Không ghi `docs/AI_LOG.md` đều đặn, dồn lại viết bù cuối giờ — log không khớp với
  `git log` thực tế sẽ bị nghi ngờ.
- Gắn AI vào như một tính năng phụ (vd. chatbot hỏi-đáp cạnh 1 app CRUD bình thường)
  thay vì để AI dẫn dắt luồng chính của sản phẩm.

## 4. Ràng buộc kiến trúc (theo tài liệu kỹ thuật BTC/mentor cung cấp)

- Chỉ dùng **1 Planner Agent** — không tạo thêm agent thứ hai, thứ ba (multi-agent).
- **Đừng tối ưu, đừng làm đẹp** trong giai đoạn dựng khung — ưu tiên chạy được trước đề
  bài công bố, dồn lực tối ưu sau khi có đề bài thật.
- Khi có đề bài chính thức: **chỉ thay `domain/`** (Domain Adapter) — không đổi Gateway,
  Planner Agent, Tool Registry, MCP Server. Xem [README](../README.md#kiến-trúc).

## 5. Bài nộp bắt buộc (nộp thiếu = không được chấm)

5 hạng mục, tất cả bắt buộc:

- [ ] **Presentation slides**
- [ ] **Demo video** — tối đa **≤ 5 phút**, quá giờ có thể bị trừ điểm hoặc từ chối
- [ ] **GitHub repository** — bắt buộc **public**, giám khảo không có quyền truy cập
      riêng tư sẽ không xem được → vào ngày nộp phải tự kiểm tra lại repo có public
      không (repo hiện tại: `dam-cong/v-nexus`)
- [ ] **Live deployed URL** — phải **còn chạy** tại thời điểm chấm, không chỉ chạy lúc
      quay demo rồi tắt server
- [ ] **Project description** (`docs/PROJECT_DESCRIPTION.md`)

⚠️ Vi phạm thường gặp: để repo ở chế độ private quên đổi public; tắt server/máy chủ sau
khi quay xong demo khiến URL live chết lúc giám khảo bấm vào.

## 6. Quy trình 3 vòng chấm

| Vòng | Nội dung | Ai vào vòng |
|---|---|---|
| 1 | AI sơ loại | Tất cả các đội |
| 2 | Giám khảo chuyên môn đánh giá | Top 30–40 đội |
| 3 | Demo Day — pitch trực tiếp 4 phút + 2 phút Q&A | Top 10 đội |

⚠️ Chuẩn bị: pitch **đúng 4 phút**, không tự ý kéo dài; chuẩn bị tinh thần trả lời Q&A
trực tiếp trước giám khảo, không phải chỉ nộp video là xong.

## 7. Tiêu chí chấm điểm (100 điểm) — xem chi tiết tự chấm ở `docs/scoring-checklist.md`

Chất lượng triển khai kỹ thuật (20) · Kiến trúc AI-Native & Đổi mới sáng tạo (20) ·
Tính khả thi kinh doanh & Lộ trình Pilot (20) · UX AI-Native & Tư duy thiết kế (15) ·
An toàn AI, Grounding & Độ tin cậy (15) · Trình bày & Bảo vệ giải pháp (10)

## 8. Chọn đề bài

- Chỉ chọn **01 trong 08 chủ đề** công bố lúc 11:00, 17/7. Đội này đã đăng ký hướng
  **Đổi mới sáng tạo & Năng suất doanh nghiệp vừa và nhỏ (SME)** — chờ đề bài cụ thể để
  cập nhật `domain/` và `docs/PROJECT_DESCRIPTION.md`.
- Không được đổi sang chủ đề khác sau khi đã chọn và bắt đầu phát triển (thể lệ không
  đề cập cho đổi chủ đề giữa chừng — mặc định là chọn 1 lần).

## Checklist nhanh trước khi nộp

- [ ] Đội đủ 2–6 thành viên, tất cả đã xác nhận, chốt trước 11:00 17/7
- [ ] `docs/AI_LOG.md` được cập nhật liên tục suốt 48 giờ, khớp `git log`
- [ ] Chỉ 1 Planner Agent trong kiến trúc
- [ ] Repo GitHub đã chuyển **public**
- [ ] Live URL còn chạy tại thời điểm nộp (kiểm tra lại ngay trước hạn chót)
- [ ] Demo video ≤ 5 phút
- [ ] Đủ cả 5 hạng mục nộp bài
- [ ] Đã chuẩn bị pitch 4 phút + sẵn sàng Q&A 2 phút cho Vòng 3

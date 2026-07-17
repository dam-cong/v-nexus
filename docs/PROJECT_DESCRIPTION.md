# Project Description — V-Nexus Tutor

Bắt buộc nộp cùng bài (thể lệ 2.2). Điền đủ trước hạn chốt đội / nộp bài.

## 1. Tên dự án & chủ đề

- **Tên:** V-Nexus Tutor
- **Tagline:** "Mỗi học sinh một lộ trình, mỗi giáo viên một trợ lý" / "Close every
  learning gap, one root cause at a time" _(đề xuất, có thể đổi)_
- **Chủ đề (đề bài):** Gia sư thích ứng thu hẹp khoảng cách năng lực trong lớp học
  (Giáo dục phổ thông — Adaptive Learning). Xem phân tích chi tiết ở
  [docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md).
  _(Đề 8 — Vbee lecture video — không còn theo đuổi, xem
  [docs/PHAN_TICH_DE_8.md](PHAN_TICH_DE_8.md).)_

## 2. Vấn đề

Học sinh ở vùng sâu vùng xa thường không được tiếp cận giáo viên giỏi — chất lượng giảng
dạy phụ thuộc hoàn toàn vào giáo viên tại chỗ, trong khi 1 giáo viên phải dạy lớp đông
với học sinh có nền tảng rất khác nhau. Hệ quả: học sinh yếu bị bỏ lại, học sinh giỏi bị
kìm hãm, khoảng cách chất lượng giáo dục thành thị–nông thôn ngày càng xa. Các app học
tập hiện có giải quyết sai vấn đề: đẩy nội dung theo thứ tự cố định, không chẩn đoán
đúng lỗ hổng, và không tận dụng được nguồn giáo viên giỏi sẵn có ở nơi khác.

AI-native là cách tiếp cận đúng vì: (1) chẩn đoán lỗ hổng cá nhân hóa theo thời gian
thực là bài toán suy luận mà rule cứng không đủ linh hoạt để bao quát mọi trường hợp;
(2) số hóa & tái sử dụng bài giảng giáo viên giỏi cần AI để trích xuất nội dung, gắn
nhãn đúng kỹ năng, và ghép nối với lỗ hổng của từng học sinh — việc này không thể làm
thủ công ở quy mô lớn.

## 3. Người dùng mục tiêu

- **Học sinh phổ thông vùng sâu vùng xa** — nền tảng không đồng đều, thiếu tiếp cận
  giáo viên giỏi, cần lộ trình học cá nhân hóa thay vì học theo thứ tự cố định.
- **Giáo viên vùng khó khăn** — dạy lớp đông, không đủ thời gian/chuyên môn kèm riêng
  từng học sinh; cần công cụ vừa chẩn đoán vừa cung cấp sẵn nội dung chất lượng cao để
  dạy lại đúng chỗ hổng.
- **(Gián tiếp) Giáo viên giỏi ở đô thị/trường điểm** — nguồn cung cấp bài giảng được số
  hóa, mở rộng phạm vi ảnh hưởng vượt ra ngoài lớp học của chính họ.

## 4. Giải pháp

**Chúng tôi đang xây dựng cái gì?**

V-Nexus Tutor là hệ thống gia sư thích ứng giải đúng bài toán nhức nhối nhất của lớp học
Việt Nam: một giáo viên, 40 học sinh, 40 nền tảng khác nhau. Thay vì đẩy bài học theo
thứ tự cố định như các app hiện có, V-Nexus Tutor chẩn đoán nguyên nhân gốc của từng lỗ
hổng kiến thức và đưa giáo viên trở lại trung tâm của quá trình dạy học.

Hệ thống vận hành trên ba tầng:

1. **Chẩn đoán truy gốc.** Kiến thức được mô hình hóa thành đồ thị tiên quyết bám sát
   Chương trình GDPT 2018. Khi học sinh sai một câu Toán 7, hệ thống không dừng ở "sai"
   — nó truy ngược đồ thị, hỏi thăm dò các kỹ năng nền, và tìm ra tầng sâu nhất còn
   vững: "Em sai bài phương trình vì hổng quy đồng phân số từ lớp 5." Kết quả là bản đồ
   lỗ hổng trực quan của từng em.
2. **Lộ trình luyện tập cá nhân hóa.** Từ bản đồ lỗ hổng, hệ thống dựng con đường luyện
   tập riêng cho từng học sinh — lấp từ lỗ hổng sâu nhất đi lên, đúng thứ tự kiến thức
   phụ thuộc nhau, thay vì luyện lại tràn lan.
3. **Bảng điều khiển giáo viên.** Heatmap toàn lớp theo từng kỹ năng; tự động gom nhóm
   học sinh có cùng lỗ hổng để phụ đạo theo nhóm; xếp hạng "cần giúp trước" dựa trên độ
   sâu và mức ảnh hưởng của lỗ hổng; cảnh báo khi một kỹ năng bị hổng trên diện rộng để
   giáo viên dạy lại cả lớp.

**Hoạt động offline hoàn toàn:** V-Nexus Tutor là PWA — ngân hàng câu hỏi và bộ máy
chẩn đoán chạy ngay trên thiết bị học sinh, đồng bộ về máy chủ khi có mạng. Trường vùng
khó khăn với đường truyền chập chờn vẫn dùng trọn vẹn.

**Phạm vi demo:** mạch Phân số → Phương trình, Toán lớp 6–7 theo GDPT 2018, với kiến
trúc đồ thị mở rộng được sang mọi mạch kiến thức và môn học.

**Dành cho ai?**

Giáo viên và học sinh phổ thông Việt Nam, đặc biệt ở vùng khó khăn — nơi một giáo viên
gánh lớp 40 em với nền tảng chênh lệch lớn, em yếu bị bỏ lại, em giỏi bị kìm chân.
V-Nexus Tutor không thay giáo viên; nó làm phần việc giáo viên không thể làm thủ công
với 40 em cùng lúc — chẩn đoán từng em — rồi trao lại cho giáo viên quyền quyết định dạy
ai, dạy gì, khi nào.

Trong team có nhà sáng lập một trung tâm đào tạo hoạt động từ 2014: bài toán lớp học
trình độ không đồng đều là thứ chúng tôi đối mặt hàng tuần suốt 12 năm, không phải giả
định trên giấy.

**Điểm khác biệt là gì?**

1. **Chẩn đoán nguyên nhân gốc, không chỉ chấm đúng/sai.** Bộ máy truy ngược đồ thị tiên
   quyết do team tự thiết kế — minh bạch, giải thích được từng kết luận, không phải hộp
   đen.
2. **Giáo viên là trung tâm, không phải người đứng ngoài.** Dashboard gom nhóm, xếp ưu
   tiên và phát hiện lỗ hổng toàn lớp — biến dữ liệu thành hành động sư phạm cụ thể
   trong tiết học tiếp theo.
3. **Offline-first thực sự.** Chẩn đoán và luyện tập chạy trọn vẹn không cần mạng —
   thiết kế cho đúng nơi cần nó nhất.
4. **Bám chuẩn GDPT 2018 từ gốc.** Mỗi kỹ năng trong đồ thị gắn mã bài học chính thức —
   nhà trường tích hợp được ngay, không cần "dịch" sang chương trình Việt Nam.

_Luồng sử dụng chính (happy path): xem
[docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md#giải-pháp-đề-xuất)._

## 5. Kiến trúc

```
Frontend (chat) → FastAPI Gateway → Planner Agent (LLM + Tool Registry)
                                          ├─ Tool: MCP Server mẫu
                                          └─ Tool: (đề bài thật sẽ thêm)
                        Gateway → PostgreSQL (log hội thoại, dữ liệu nghiệp vụ)
```

Domain Adapter (`domain/`) là lớp duy nhất chứa prompt + tool đặc thù đề bài — xem
[README](../README.md#kiến-trúc) để biết cách thay khi có đề bài thật.

## 6. Tính khả thi kinh doanh & Lộ trình Pilot

_Mô hình vận hành/kinh doanh nếu triển khai thật, ai trả tiền/tài trợ, bước pilot đầu
tiên sau cuộc thi._

## 7. An toàn AI, Grounding & Độ tin cậy

_Cách hạn chế ảo giác (grounding qua tool/DB thay vì để LLM tự bịa), giới hạn phạm vi
trả lời, xử lý khi tool lỗi hoặc dữ liệu thiếu._

## 8. Tech stack

- Backend: FastAPI (Gateway), Planner Agent gọi Anthropic Claude
- Tool integration: MCP (Model Context Protocol), Tool Registry nội bộ
- Database: PostgreSQL (SQLAlchemy async)
- Frontend: Streamlit (chat UI)
- Hạ tầng: Docker Compose

## 9. Team

| Tên | Vai trò | Phụ trách |
|---|---|---|
| Hiến | PM | Timeline, mốc nộp bài, AI_LOG, checklist tuân thủ thể lệ |
| Ngọc | BA | Phạm vi demo, dữ liệu mock, business case/pilot, pitch deck, Q&A |
| Quyết | Dev | Kiến trúc (PWA/backend), dashboard giáo viên, deploy live URL |
| Hiếu | AI | Đồ thị tri thức, thuật toán chẩn đoán gốc, sinh lộ trình luyện tập, Domain Adapter |
| Dũng | Cố vấn | Review kiến trúc & tính sư phạm, phản biện pitch trước Demo Day |

_Ghi chú credibility: trong team có nhà sáng lập một trung tâm đào tạo hoạt động từ_
_2014 — bài toán lớp học trình độ không đồng đều là vấn đề thực tế đối mặt hàng tuần_
_suốt 12 năm, không phải giả định trên giấy. Nên nhấn mạnh chi tiết này khi pitch._

⚠️ _Xác nhận thể lệ: đội 2–6 thành viên, tất cả phải đã đăng ký/xác nhận trước 11:00_
_17/7 (`docs/RULES.md` mục 1). Nếu Dũng là cố vấn cá nhân (không phải mentor do BTC bố_
_trí), cần xác nhận rõ có tính là thành viên thi chính thức hay không trước khi đưa vào_
_slide/credit — xem chi tiết phân công ở_ `docs/timeline.md`.

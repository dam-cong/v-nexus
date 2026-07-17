# Project Description — V-Nexus Tutor

Bắt buộc nộp cùng bài (thể lệ 2.2). Điền đủ trước hạn chốt đội / nộp bài.

## 1. Tên dự án & chủ đề

- **Tên:** V-Nexus Tutor
- **Tagline:** "V-Nexus Tutor — Mỗi em một lộ trình, cả trường cùng tiến bộ."
- **Chủ đề (đề bài):** Gia sư thích ứng thu hẹp khoảng cách năng lực trong lớp học —
  nền tảng học Tiếng Anh thích ứng cho trường K12, bắt đầu từ lớp 3–4 theo GDPT 2018.
  Xem phân tích chi tiết ở
  [docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md).

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
- **Phụ huynh** — muốn biết con đang ở đâu và giúp được gì tại nhà, nhưng không có
  chuyên môn sư phạm để tự đánh giá; cần thông tin đơn giản, không thuật ngữ kỹ thuật,
  và gợi ý hành động cụ thể thay vì chỉ điểm số.
- **Nhà trường (khách hàng tổ chức)** — cấp tài khoản cho giáo viên/học sinh, cần bảng
  điều khiển tổng quan theo khối/lớp để phát hiện sớm học sinh cần hỗ trợ và dữ liệu
  phục vụ vinh danh/khen thưởng — đây là đối tượng ra quyết định mua/triển khai, khác
  với giáo viên/học sinh là người dùng hàng ngày.

## 4. Giải pháp

**Chúng tôi đang xây dựng cái gì?**

V-Nexus Tutor là nền tảng học tiếng Anh thích ứng dành cho nhà trường K12, bắt đầu từ
lớp 3–4 theo Chương trình GDPT 2018. Nhà trường cấp tài khoản cho giáo viên và học
sinh; hệ thống khép kín toàn bộ vòng học với AI ở mọi điểm chạm: đánh giá đầu vào →
chẩn đoán lỗ hổng → lộ trình cá nhân → luyện tập → kiểm tra → nhận xét → báo cáo.

**Với học sinh:** bài đánh giá đầu vào thích ứng không chỉ chấm đúng/sai mà truy ra
nguyên nhân gốc — "em chưa nói được hội thoại Unit 5 vì hổng mẫu câu 'How many' và
thiếu từ vựng chủ đề Toys" — rồi dựng lộ trình lấp đúng lỗ hổng đó. Trẻ luyện từ vựng,
phát âm, mẫu câu và hội thoại với phản hồi AI tức thì: thu âm giọng đọc, hệ thống chấm
từng từ và tô màu chỗ cần sửa. Toàn bộ được thiết kế cho trẻ 8–9 tuổi: hướng dẫn bằng
giọng nói, hình ảnh lớn, thao tác chạm đơn giản — và học được cả khi không có mạng.

**Động lực học** được nuôi bằng hệ thống coin – huy hiệu – xếp hạng: làm đúng, phát âm
chuẩn, chăm luyện tập đều sinh coin và điểm kinh nghiệm; xếp hạng theo lớp/trường theo
tuần, tháng, học kỳ; nhà trường vinh danh và học sinh đổi coin lấy quà tại gian hàng của
trường — biến phần thưởng ảo thành ghi nhận thật.

**Với giáo viên:** dashboard heatmap toàn lớp theo từng kỹ năng, tự động gom nhóm học
sinh có cùng lỗ hổng kèm gợi ý hoạt động phụ đạo cho từng nhóm, và AI soạn nhận xét cá
nhân hóa cho từng em — phần việc tốn hàng giờ mỗi kỳ nay còn vài phút duyệt và chỉnh.

**Với nhà trường:** bảng điều khiển tổng quan theo khối/lớp, phát hiện sớm học sinh cần
hỗ trợ, và dữ liệu vinh danh - khen thưởng kịp thời.

Mỗi học sinh có hồ sơ học tập trọn vẹn: xuất phát từ đâu, đang ở đâu, tiến bộ thế nào —
minh bạch với chính em, giáo viên và phụ huynh.

**Dành cho ai?**

Các trường tiểu học Việt Nam — nơi một giáo viên tiếng Anh dạy hàng trăm học sinh với
nền tảng chênh lệch lớn, đặc biệt ở vùng khó khăn nơi đường truyền không ổn định.
V-Nexus Tutor không thay giáo viên: nó làm phần việc không thể làm thủ công — chẩn đoán
và theo dõi từng em — rồi trao lại cho giáo viên và nhà trường quyền quyết định sư phạm.

Trong team có nhà sáng lập một trung tâm đào tạo hoạt động từ 2014: bài toán lớp học
trình độ không đồng đều là thứ chúng tôi đối mặt hàng tuần suốt 12 năm, không phải giả
định trên giấy.

**Điểm khác biệt là gì?**

1. **Chẩn đoán nguyên nhân gốc bằng đồ thị kiến thức tự thiết kế bám GDPT 2018** —
   minh bạch, giải thích được, không đẩy bài theo thứ tự cố định như các app hiện có.
2. **Vòng khép kín ba vai trò học sinh – giáo viên – nhà trường trong một hệ thống**,
   với AI phục vụ cả ba thay vì chỉ học sinh.
3. **Offline-first cho đúng nơi cần nhất** — luyện tập và chẩn đoán chạy trên thiết bị,
   đồng bộ khi có mạng.
4. **Động lực học gắn với ghi nhận thật** — coin, huy hiệu, xếp hạng kết nối với vinh
   danh và phần quà của chính nhà trường, thiết kế từ kinh nghiệm 12 năm giữ chân trẻ
   nhỏ với tiếng Anh.

_Cơ chế kỹ thuật đứng sau "chẩn đoán nguyên nhân gốc" (Bayesian Knowledge Tracing,
kiểm tra thích ứng CAT, LLM giới hạn ở vai trò biên) — dùng khi giám khảo hỏi xoáy kỹ
thuật ở Vòng 3 — xem
[docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md#áp-dụng-ai-vào-từng-bước--và-vì-sao-không-chỉ-là-gọi-llm)._

**Tagline:** V-Nexus Tutor — Mỗi em một lộ trình, cả trường cùng tiến bộ.

## 5. Kiến trúc

Hai phần tách biệt, khác ràng buộc mạng:

**(a) Lõi offline-first** (chẩn đoán + luyện tập — bắt buộc chạy được không cần mạng):
PWA trên thiết bị học sinh, ngân hàng câu hỏi + engine BKT chạy local (IndexedDB/SQLite),
đồng bộ server khi có mạng.

**(b) Bot hỏi-đáp** (tính năng online — tái sử dụng khung Gateway/Planner Agent đã dựng
sẵn từ đầu dự án):

```
Frontend (chat) → FastAPI Gateway → Planner Agent (LLM + Tool Registry)
                                          ├─ Tool: diagnose_gap
                                          ├─ Tool: generate_practice_path
                                          ├─ Tool: teacher_dashboard_query
                                          └─ Tool: parent_dashboard_query
                        Gateway → PostgreSQL (log hội thoại, dữ liệu nghiệp vụ)
```

LLM trong Planner Agent chỉ chọn tool + diễn giải kết quả, không tự chẩn đoán (chẩn đoán
thật nằm trong BKT ở phần (a)). Access control theo `student_id`/`class_id` thực thi ở
tầng Planner Agent trước khi gọi tool — xem chi tiết ở
[docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](PHAN_TICH_DE_ADAPTIVE_TUTORING.md#bot-hỏi-đáp-cho-học-sinh--giáo-viên).

Domain Adapter (`domain/`) là lớp duy nhất chứa prompt + tool đặc thù đề bài — xem
[README](../README.md#kiến-trúc).

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

# Phân tích đề bài: Gia sư thích ứng thu hẹp khoảng cách năng lực trong lớp học

**Nhóm bài toán:** Giáo dục phổ thông — Adaptive Learning

> Đây là đề bài **thay thế** cho Đề 8 (Vbee — slide/giáo án thành video bài giảng).
> `docs/PHAN_TICH_DE_8.md` được giữ lại làm tài liệu tham khảo, không còn là đề đang
> theo đuổi.

## Đề bài (tóm tắt)

Vấn đề cấp bách nhất của giáo dục phổ thông Việt Nam không phải thiếu nội dung — mà là
**khoảng cách năng lực trong cùng một lớp học**, đặc biệt ở vùng khó khăn nơi 1 giáo
viên phải dạy lớp 40 học sinh với nền tảng rất khác nhau. Học sinh yếu bị bỏ lại phía
sau; học sinh giỏi bị kìm hãm. Các app học tập hiện có chỉ đẩy bài học theo thứ tự cố
định, không thực sự thích ứng, và bỏ qua vai trò giáo viên.

## Yêu cầu

- Chẩn đoán **tận gốc lỗ hổng kiến thức** của từng học sinh (vd: sai Toán lớp 7 vì hổng
  phân số từ lớp 5) — không chỉ chấm đúng/sai.
- Sinh **lộ trình luyện tập cá nhân hóa** nhắm đúng lỗ hổng đó.
- **Bắt buộc có dashboard giáo viên**: tự động nhóm học sinh theo nhu cầu, gợi ý ưu tiên
  hỗ trợ ai trước, phát hiện lỗ hổng chung của cả lớp để dạy lại.
- **Ràng buộc:** chạy được offline/mạng yếu; nội dung bám Chương trình GDPT 2018.

## Điểm khác với app học tập hiện có

Không "học theo thứ tự cố định" mà **chẩn đoán nguyên nhân gốc** xuyên suốt các
lớp/khối trước, và **giữ giáo viên làm trung tâm quyết định** — AI hỗ trợ ra quyết định,
không thay thế giáo viên.

## Thách thức kỹ thuật cốt lõi

1. **Sơ đồ tri thức tiên quyết** — mô hình hoá quan hệ phụ thuộc kỹ năng xuyên các
   lớp/khối theo GDPT 2018. Khó nhất, cần dựng trước (dù rút gọn 1 môn, 2–3 khối cho
   demo) để chẩn đoán có ý nghĩa.
2. **Chẩn đoán nguyên nhân gốc** — mỗi câu hỏi gắn nhãn kỹ năng tiên quyết; khi sai, suy
   ra kỹ năng thiếu có xác suất cao nhất (rule-based/Bayesian đơn giản). LLM có thể hỗ
   trợ sinh giải thích, nhưng chẩn đoán lõi nên dựa trên sơ đồ + dữ liệu, tránh để LLM
   suy đoán tự do.
3. **Sinh lộ trình luyện tập** — chọn/sinh bài tập nhắm đúng kỹ năng thiếu, độ khó tăng
   dần, không ngẫu nhiên.
4. **Dashboard giáo viên** — nhóm học sinh theo gap tương đồng, xếp ưu tiên theo mức độ
   nghiêm trọng, phát hiện lỗi lặp lại ở tỷ lệ % học sinh cao trong lớp.
5. **Offline/mạng yếu** — ràng buộc khó nhất với kiến trúc dựa LLM cloud. Hướng xử lý:
   tách **soạn nội dung** (LLM, có mạng, làm trước, cache sẵn) khỏi **chấm & chẩn đoán
   lúc học** (chạy local, rule-based, không cần gọi LLM realtime); lưu local-first
   (SQLite/IndexedDB), đồng bộ khi có mạng.

## Giải pháp đề xuất

**Kiến trúc:** vẫn map vào khung V-Nexus, nhưng vai trò LLM chuyển từ "runtime mọi
request" sang "soạn nội dung trước + hỗ trợ phân tích", do ràng buộc offline. Domain
Adapter mới: `domain/adaptive_tutor_adapter.py`.

- **Tool `diagnose_gap`**: nhận kết quả bài làm + sơ đồ tri thức → trả kỹ năng tiên
  quyết nghi ngờ là nguyên nhân gốc.
- **Tool `generate_practice_path`**: sinh danh sách bài tập nhắm đúng gap (ngân hàng câu
  hỏi soạn sẵn bằng LLM offline-batch, gắn nhãn kỹ năng, cache local).
- **Tool `teacher_dashboard_query`**: tổng hợp gap theo lớp — nhóm học sinh, xếp ưu
  tiên, phát hiện lỗ hổng chung.
- **Dữ liệu:** sơ đồ tri thức GDPT 2018 rút gọn (1 môn, 2–3 khối) + ngân hàng câu hỏi
  gắn nhãn kỹ năng.

**Nguồn nội dung — số hóa bài giảng giáo viên giỏi:** thay vì để LLM tự sinh nội dung
giảng dạy chung chung, ngân hàng học liệu ưu tiên **số hóa bài giảng thật của giáo viên
giỏi** (video/transcript có sẵn hoặc thu thập trong phạm vi demo) → LLM trích xuất, gắn
nhãn theo đúng kỹ năng trong sơ đồ tri thức → khi hệ thống chẩn đoán ra gap, ưu tiên gợi
ý đúng đoạn giảng của giáo viên giỏi khớp kỹ năng đó, thay vì bài tập tự sinh không có
ngữ cảnh sư phạm. Đây là cách đưa chất lượng giảng dạy đô thị/trường điểm tới học sinh
và giáo viên vùng sâu vùng xa — nơi thiếu giáo viên giỏi tại chỗ.

**Luồng chính (happy path):**
1. Học sinh làm bài kiểm tra chẩn đoán ngắn.
2. Hệ thống (local) đối chiếu sơ đồ tri thức → xác định gap gốc.
3. Sinh lộ trình luyện tập nhắm đúng gap, độ khó tăng dần.
4. Học sinh luyện tập offline; dữ liệu đồng bộ khi có mạng.
5. Giáo viên xem dashboard: nhóm học sinh theo gap, gợi ý ưu tiên, cảnh báo lỗ hổng
   chung của lớp.

## MVP 48 giờ

**Phải có:** sơ đồ tri thức rút gọn (1 môn, ví dụ Toán, 2 khối liền kề) + bài kiểm tra
chẩn đoán ngắn + suy luận gap rule-based đơn giản + dashboard giáo viên cơ bản (danh
sách học sinh + gap + nhóm).

**Có thể bỏ:** cá nhân hóa độ khó nâng cao, đồng bộ offline đầy đủ (demo có thể
local-only, nêu rõ hướng mở rộng trong pitch), nhiều môn học.

## Business case

Người trả tiền tiềm năng: Sở/Phòng GD&ĐT (chương trình hỗ trợ vùng khó khăn), trường học
(gói theo lớp/giáo viên), hoặc tổ chức giáo dục phi lợi nhuận tài trợ. Pilot đầu tiên:
1 lớp thật ở vùng khó khăn, đo mức độ thu hẹp khoảng cách qua bài kiểm tra trước/sau.

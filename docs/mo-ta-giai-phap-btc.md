# Mô tả giải pháp — V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform

## Bản gửi BTC (≤5000 ký tự, dán trực tiếp — không dùng markdown)

**Độ dài: 3.935 ký tự (đếm theo character) / giới hạn 5.000 ký tự** — còn dư ~1.065 ký tự. Nếu
form BTC đếm theo byte UTF-8 thay vì ký tự thì khối này ~5.120 byte (nhỉnh hơn 5.000 một chút do
dấu tiếng Việt chiếm nhiều byte hơn) — nói với mình nếu cần cắt thêm cho chắc, còn nếu là giới hạn
ký tự thông thường (khả năng cao) thì dùng thẳng được. Cấu trúc: "VẤN ĐỀ" mở đầu, 3 câu hỏi
Xây gì/Cho ai/Khác biệt gì, và mục 4 mới thêm — "HƯỚNG MỞ RỘNG SAU MVP" (AI Chatbot + AI hỗ trợ
giáo viên lên bài giảng, theo yêu cầu mới nhất). Copy nguyên khối bên dưới:

```text
V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform

"Mỗi học sinh một lộ trình, mỗi giáo viên một trợ lý."

VẤN ĐỀ

Trong một lớp học 40 học sinh, các em học cùng một bài nhưng nền tảng rất khác nhau. Điểm số hay nhãn đúng/sai không chỉ ra được nguyên nhân của khoảng cách đó. Giáo viên không đủ thời gian truy ngược kiến thức nền cho từng em trong khi vẫn phải giữ tiến độ chung của lớp — đặc biệt khó khăn ở các trường nông thôn, vùng xa nơi nguồn lực và đường truyền hạn chế.

1. BẠN ĐANG XÂY DỰNG CÁI GÌ

V-NEXUS SCHOOL là nền tảng học tập thích ứng dùng AI cho trường K12 Việt Nam. Vòng lặp hỗ trợ học tập: học sinh làm bài chẩn đoán, hệ thống truy ngược kiến thức tiên quyết để tìm nguyên nhân gốc rễ của lỗ hổng (không chỉ chấm đúng/sai), tạo lộ trình cá nhân hóa lấp đúng lỗ hổng theo thứ tự phụ thuộc, học sinh luyện tập (từ vựng, mẫu câu, chấm phát âm), hệ thống đánh giá lại và điều chỉnh. Song song, AI hỗ trợ giáo viên: dashboard heatmap lớp, gợi ý nhóm học sinh theo nhu cầu, xếp ưu tiên hỗ trợ, soạn sẵn nhận xét học sinh định kỳ (giáo viên duyệt trước khi gửi). Học sinh được tạo động lực bằng coin, XP, huy hiệu, phối hợp với vinh danh cấp trường. Hoạt động luyện tập cốt lõi chạy được cả khi mất mạng.

2. DÀNH CHO AI

Trường K12 trên toàn Việt Nam, ưu tiên trường nông thôn, vùng xa có hạ tầng mạng hạn chế. Bốn nhóm dùng: học sinh (demo lớp 3-4, Tiếng Anh); giáo viên quản lý lớp đông, nhận gợi ý có bằng chứng và duyệt nhận xét AI; Ban giám hiệu xem tổng quan khối lớp và vinh danh; quản trị viên quản lý chương trình, kỹ năng, ngân hàng câu hỏi.

3. ĐIỂM KHÁC BIỆT — NHỮNG GÌ CHÚNG TÔI MUỐN BAN GIÁM KHẢO CHÚ Ý

- Kiến trúc AI minh bạch, không phải "LLM wrapper": lõi chẩn đoán và xếp lộ trình dùng thuật toán tự thiết kế — Bayesian Knowledge Tracing kết hợp truy gốc trên đồ thị kiến thức tiên quyết và topological sort. Mọi kết luận truy được về bằng chứng cụ thể, giải thích được với giáo viên và BGK, không phải một hộp đen.

- Giải quyết đúng bài toán offline của giáo dục vùng khó: nội dung giải thích, ví dụ, phản hồi lỗi được AI sinh sẵn trước khi học sinh luyện tập, nên phần lõi học tập chạy được gần như hoàn toàn khi mất mạng — đây là thiết kế cốt lõi ngay từ đầu, không phải tính năng phụ thêm sau.

- Chẩn đoán truy gốc thay vì chấm điểm: hệ thống tìm đúng kỹ năng nền gây ra lỗi (ví dụ: lỗi đọc hiểu lớp 4 do hổng từ vựng lớp 3), thay vì chỉ báo đúng/sai — xử lý đúng nguyên nhân, không bắt học sinh học lại nội dung đã giỏi.

- AI hỗ trợ, con người quyết định: mọi đề xuất AI (nhận xét học sinh, nhóm, ưu tiên hỗ trợ) đều qua giáo viên duyệt trước khi có hiệu lực — an toàn cho môi trường giáo dục, AI không tự quyết định thay giáo viên.

- Không chỉ là công cụ chấm bài: gắn với động lực học (coin, XP, huy hiệu) và cơ chế vinh danh cấp trường, hướng tới duy trì thói quen học lâu dài, không dừng ở một bài kiểm tra.

- Nhắm đúng đối tượng cần nhất: ưu tiên thiết kế cho trường nông thôn, vùng xa — nơi khoảng cách năng lực trong lớp lớn nhất và ít được các sản phẩm edtech hiện có phục vụ.

4. HƯỚNG MỞ RỘNG SAU MVP

- AI Chatbot: hội thoại đóng vai theo tình huống bài học để học sinh luyện phản xạ (ràng buộc trong vốn từ vựng, mẫu câu đã học), và chatbot hỏi-đáp cho giáo viên/phụ huynh tra cứu nhanh tiến độ học sinh trong phạm vi được phép.

- AI hỗ trợ giáo viên lên bài giảng: dựa trên kỹ năng yếu phổ biến của lớp, AI soạn sẵn gợi ý giáo án và hoạt động dạy lại phù hợp; giáo viên chỉnh sửa và duyệt trước khi dùng, giảm thời gian chuẩn bị bài, đặc biệt cho giáo viên ở vùng thiếu nhân lực.

- Mở rộng Knowledge Graph và ngân hàng câu hỏi sang nhiều môn học, khối lớp khác ngoài Tiếng Anh lớp 3-4 hiện đang demo.

- Dashboard phụ huynh và đánh giá kỹ năng nói toàn diện hơn (hội thoại tự do, ngữ điệu), placement test đủ 4 kỹ năng nghe-nói-đọc-viết.

Đây là hướng phát triển sau khi MVP được thí điểm và kiểm chứng hiệu quả thực tế, không phải cam kết có sẵn trong bản demo hackathon.
```

---

## Bản đầy đủ có định dạng (tham khảo, không dùng để dán vào form giới hạn ký tự)

## 1. Bạn đang xây dựng cái gì?

V-NEXUS SCHOOL là nền tảng học tập thích ứng dùng AI dành cho các trường học K12 tại Việt Nam.
Hệ thống vận hành một vòng lặp hỗ trợ học tập liên tục: học sinh làm bài chẩn đoán → hệ thống
truy ngược kiến thức tiên quyết để tìm ra **nguyên nhân gốc rễ** của lỗ hổng (không chỉ chấm
đúng/sai) → tạo lộ trình luyện tập cá nhân hóa lấp đúng lỗ hổng theo thứ tự phụ thuộc → học sinh
luyện tập (từ vựng, mẫu câu, chấm phát âm) → hệ thống đánh giá lại và điều chỉnh lộ trình. Song
song, AI hỗ trợ giáo viên bằng dashboard heatmap lớp, gợi ý nhóm học sinh theo nhu cầu, xếp ưu
tiên hỗ trợ, và soạn sẵn nhận xét học sinh định kỳ để giáo viên chỉ cần duyệt/chỉnh sửa trước khi
gửi. Học sinh được tạo động lực bằng coin – XP – huy hiệu, phối hợp với công cụ vinh danh của nhà
trường. Các hoạt động luyện tập cốt lõi được thiết kế chạy được cả khi mạng yếu hoặc mất mạng.

## 2. Dành cho ai?

Sản phẩm dành cho các trường K12 trên toàn lãnh thổ Việt Nam, đặc biệt ưu tiên **trường ở nông
thôn, vùng xa** — nơi chênh lệch nền tảng học tập giữa các học sinh trong cùng lớp lớn, hạ tầng
mạng không ổn định và giáo viên phải quản lý lớp đông với nguồn lực hạn chế. Bốn nhóm người dùng
chính: **học sinh** (demo ở lớp 3–4, môn Tiếng Anh) làm bài và luyện tập theo lộ trình riêng;
**giáo viên** theo dõi cả lớp, nhận gợi ý hỗ trợ có bằng chứng và duyệt nhận xét AI; **Ban giám
hiệu** xem tổng quan khối/lớp và tổ chức vinh danh khen thưởng; **quản trị viên nội dung** quản lý
chương trình, kỹ năng và ngân hàng câu hỏi.

## 3. Điểm khác biệt là gì?

- **Chẩn đoán truy gốc, không chỉ chấm điểm:** hệ thống dùng đồ thị kiến thức tiên quyết
  (Knowledge Graph) để truy ngược từ lỗi biểu hiện về đúng kỹ năng nền gây ra lỗi, thay vì chỉ ghi
  nhận đúng/sai hay điểm số tổng.
- **Offline-first cho phần lõi luyện tập:** nội dung giải thích, ví dụ và phản hồi theo từng dạng
  lỗi được AI sinh sẵn **trước khi** học sinh luyện tập (không phải gọi AI theo thời gian thực),
  nên học sinh vẫn học được và nhận phản hồi thông minh ngay cả khi mất mạng hoàn toàn.
- **Thuật toán minh bạch, giải thích được:** phần lõi chẩn đoán và xếp lộ trình dùng Bayesian
  Knowledge Tracing kết hợp truy gốc trên đồ thị và topological sort — không phải một lớp AI
  "hộp đen" bọc ngoài mà giáo viên/BGK không thể kiểm chứng được vì sao hệ thống kết luận như vậy.
- **AI hỗ trợ, giáo viên quyết định:** mọi đề xuất của AI (nhận xét học sinh, nhóm, mức ưu tiên hỗ
  trợ) đều cần giáo viên duyệt hoặc điều chỉnh trước khi có hiệu lực — AI không tự thay giáo viên
  đưa ra quyết định sư phạm cuối cùng.
- **Gắn với động lực học và vinh danh ở cấp trường:** hệ thống không dừng ở chấm bài mà phối hợp
  với cơ chế coin – XP – huy hiệu và bảng vinh danh của nhà trường để duy trì động lực học lâu dài.

---
*Trích từ `docs/PROJECT_DESCRIPTION.md` (mục 1 và mục 3) — xem tài liệu đó để có đặc tả đầy đủ các
luồng chức năng, ranh giới vai trò AI và phạm vi MVP.*

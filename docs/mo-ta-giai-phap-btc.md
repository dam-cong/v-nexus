# Mô tả giải pháp — V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform

## Bản gửi BTC (≤5000 ký tự, dán trực tiếp — không dùng markdown)

**Độ dài: 3.170 ký tự / giới hạn 5.000 ký tự** (còn dư ~1.800 ký tự). Copy nguyên khối bên dưới,
không cần chỉnh sửa gì thêm:

```text
V-NEXUS SCHOOL: AI-powered Adaptive Learning Platform

"Mỗi học sinh một lộ trình, mỗi giáo viên một trợ lý."

Trong một lớp học 40 học sinh, các em có thể học cùng một bài nhưng có nền tảng rất khác nhau. Điểm số hay nhãn đúng/sai không chỉ ra được nguyên nhân của khoảng cách đó, và giáo viên khó có thời gian truy ngược kiến thức nền cho từng em trong khi vẫn phải bảo đảm tiến độ chung của lớp.

1. Bạn đang xây dựng cái gì?

V-NEXUS SCHOOL là nền tảng học tập thích ứng dùng AI dành cho các trường học K12 tại Việt Nam. Hệ thống vận hành một vòng lặp hỗ trợ học tập liên tục: học sinh làm bài chẩn đoán, hệ thống truy ngược kiến thức tiên quyết để tìm ra nguyên nhân gốc rễ của lỗ hổng (không chỉ chấm đúng/sai), tạo lộ trình luyện tập cá nhân hóa lấp đúng lỗ hổng theo thứ tự phụ thuộc, học sinh luyện tập (từ vựng, mẫu câu, chấm phát âm), rồi hệ thống đánh giá lại và điều chỉnh lộ trình. Song song, AI hỗ trợ giáo viên bằng dashboard heatmap lớp, gợi ý nhóm học sinh theo nhu cầu, xếp ưu tiên hỗ trợ, và soạn sẵn nhận xét học sinh định kỳ để giáo viên chỉ cần duyệt và chỉnh sửa trước khi gửi. Học sinh được tạo động lực bằng coin, XP và huy hiệu, phối hợp với công cụ vinh danh của nhà trường. Các hoạt động luyện tập cốt lõi được thiết kế chạy được cả khi mạng yếu hoặc mất mạng — phù hợp với điều kiện hạ tầng ở nhiều trường Việt Nam.

2. Dành cho ai?

Sản phẩm dành cho các trường K12 trên toàn lãnh thổ Việt Nam, đặc biệt ưu tiên trường ở nông thôn, vùng xa — nơi chênh lệch nền tảng học tập giữa các học sinh trong cùng lớp lớn, hạ tầng mạng không ổn định và giáo viên phải quản lý lớp đông với nguồn lực hạn chế. Bốn nhóm người dùng chính: học sinh (demo ở lớp 3-4, môn Tiếng Anh, có thể mở rộng sang môn học và khối lớp khác) làm bài và luyện tập theo lộ trình riêng; giáo viên theo dõi cả lớp, nhận gợi ý hỗ trợ có bằng chứng và duyệt nhận xét AI; Ban giám hiệu xem tổng quan khối lớp và tổ chức vinh danh khen thưởng; quản trị viên nội dung quản lý chương trình, kỹ năng và ngân hàng câu hỏi.

3. Điểm khác biệt là gì?

Chẩn đoán truy gốc, không chỉ chấm điểm: hệ thống dùng đồ thị kiến thức tiên quyết để truy ngược từ lỗi biểu hiện về đúng kỹ năng nền gây ra lỗi, thay vì chỉ ghi nhận đúng/sai hay điểm số tổng.

Offline-first cho phần lõi luyện tập: nội dung giải thích, ví dụ và phản hồi theo từng dạng lỗi được AI sinh sẵn trước khi học sinh luyện tập, nên học sinh vẫn học được và nhận phản hồi thông minh ngay cả khi mất mạng hoàn toàn.

Thuật toán minh bạch, giải thích được: phần lõi chẩn đoán và xếp lộ trình dùng Bayesian Knowledge Tracing kết hợp truy gốc trên đồ thị và topological sort, không phải một lớp AI hộp đen bọc ngoài mà không ai kiểm chứng được vì sao hệ thống kết luận như vậy.

AI hỗ trợ, giáo viên quyết định: mọi đề xuất của AI (nhận xét học sinh, nhóm, mức ưu tiên hỗ trợ) đều cần giáo viên duyệt hoặc điều chỉnh trước khi có hiệu lực — AI không tự thay giáo viên đưa ra quyết định sư phạm cuối cùng.

Gắn với động lực học và vinh danh ở cấp trường: hệ thống không dừng ở chấm bài mà phối hợp với cơ chế coin, XP, huy hiệu và bảng vinh danh của nhà trường để duy trì động lực học lâu dài, không chỉ dừng ở một bài kiểm tra.
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

# Phân tích chi tiết: Cách triển khai phần AI — V-NEXUS SCHOOL Adaptive Learning Platform

> Tài liệu dành cho nhóm trưởng — mô tả kiến trúc AI, thuật toán cốt lõi, cách nối vào codebase hiện có, model/thư viện sử dụng, nguồn dữ liệu, và cách xử lý rủi ro. (Bản không chứa code — phần triển khai kỹ thuật sẽ do Dev AI viết trực tiếp trong repo.)

---

## 1. Tổng quan: AI trong project gồm 3 tầng

**Tầng 1 — LLM Input Layer**: trích xuất dữ liệu có cấu trúc từ tài liệu đầu vào (chương trình học dạng PDF, hồ sơ học sinh dạng văn bản tự do).

**Tầng 2 — BKT Engine + Knowledge Graph (lõi AI chính)**: một mô hình xác suất — không phải LLM — theo dõi mức độ thành thạo từng kỹ năng của học sinh và truy ngược tìm gốc rễ lỗ hổng kiến thức. Đây là phần minh bạch, có thể giải thích và kiểm chứng được, khác hẳn cách tiếp cận "hỏi LLM cho ra câu trả lời".

**Tầng 3 — LLM Output Layer + Planner Agent**: diễn giải kết quả từ Tầng 2 thành câu trả lời tự nhiên, điều chỉnh theo vai trò người nghe (học sinh, giáo viên, phụ huynh).

Ba tầng này hoạt động nối tiếp: dữ liệu đầu vào → BKT Engine tính toán → LLM diễn giải kết quả. LLM không bao giờ tự quyết định học sinh yếu ở đâu; nó chỉ được phép thuật lại những gì Tầng 2 đã tính ra.

**Nguyên tắc quan trọng nhất cần nhóm trưởng nắm**: nếu bỏ Tầng 2 và để LLM tự "đoán" học sinh yếu ở đâu dựa trên cảm tính, sản phẩm sẽ không khác gì một chatbot thông thường — mất toàn bộ giá trị "AI-native, minh bạch" mà giám khảo đánh giá cao. Tầng 2 phải làm trước tiên và làm chắc chắn nhất trong toàn bộ kế hoạch.

---

## 2. Tầng 2 — BKT Engine (làm trước tiên, quan trọng nhất)

### 2.1. Ý tưởng thuật toán

Bayesian Knowledge Tracing gán cho mỗi kỹ năng của mỗi học sinh một **xác suất đã thành thạo**. Xác suất này được cập nhật liên tục mỗi khi học sinh trả lời một câu hỏi, dựa trên 4 tham số cố định:

- **Xác suất đã biết trước khi học** (prior): mức độ khả năng học sinh đã nắm được kỹ năng này trước khi bắt đầu luyện tập.
- **Xác suất học được sau mỗi lượt luyện** (transit): mỗi lần làm bài, dù đúng hay sai, khả năng học sinh tiến bộ thêm một chút.
- **Xác suất đoán đúng dù chưa biết** (guess): học sinh có thể trả lời đúng nhờ may mắn dù thực chất chưa nắm vững kỹ năng.
- **Xác suất làm sai dù đã biết** (slip): học sinh có thể sai vì bất cẩn dù thực chất đã nắm vững.

Khuyến nghị đặt 4 tham số này ở mức cố định hợp lý ngay từ đầu (ví dụ: xác suất biết trước khoảng 30%, xác suất học được mỗi lượt khoảng 30%, xác suất đoán đúng khoảng 20%, xác suất sai sót khoảng 10%) thay vì để hệ thống tự học các tham số này từ dữ liệu. Lý do: việc tự động ước lượng tham số cần một lượng dữ liệu đủ lớn (hàng chục học sinh, hàng chục lượt trả lời mỗi kỹ năng) mà một bản demo trong 48 giờ không thể có được. Đặt tham số cố định giúp hệ thống chạy ổn định và dễ giải thích với giám khảo hơn.

### 2.2. Cách cập nhật xác suất

Mỗi khi có một câu trả lời mới, việc cập nhật được thực hiện theo hai bước:

**Bước 1 — Cập nhật dựa trên bằng chứng vừa quan sát được.** Nếu học sinh trả lời đúng, xác suất thành thạo được điều chỉnh tăng lên theo tỷ lệ giữa "khả năng trả lời đúng nếu đã biết" và tổng khả năng trả lời đúng (kể cả trường hợp đoán đúng dù chưa biết). Nếu trả lời sai, phép tính diễn ra tương tự nhưng theo chiều ngược lại, cân nhắc cả khả năng "sai sót dù đã biết".

**Bước 2 — Cộng thêm phần tiến bộ tự nhiên qua lượt luyện.** Sau khi có xác suất mới từ bước 1, cộng thêm một phần nhỏ đại diện cho việc học sinh có cơ hội học thêm được gì đó qua chính lượt làm bài này, bất kể đúng hay sai.

Kết quả cuối cùng là một con số từ 0 đến 1, thể hiện mức độ tự tin của hệ thống rằng học sinh đã thành thạo kỹ năng đó tại thời điểm hiện tại.

### 2.3. Truy tìm gốc rễ lỗ hổng (root cause)

Khi học sinh làm sai một câu ở một kỹ năng nào đó, hệ thống không dừng lại ở việc báo "học sinh yếu kỹ năng này" mà tiếp tục **truy ngược lên các kỹ năng tiên quyết** trong đồ thị kiến thức. Với mỗi kỹ năng tiên quyết, hệ thống kiểm tra xác suất thành thạo hiện tại của học sinh ở đó; nếu cũng thấp hơn một ngưỡng nhất định (ví dụ dưới 50%), hệ thống tiếp tục truy ngược xa hơn.

Quá trình này dừng lại khi tìm được kỹ năng "gốc" — tức là kỹ năng có xác suất thành thạo thấp nhưng bản thân các kỹ năng tiên quyết của nó (nếu có) đều đã ổn. Đây chính là gốc rễ thật sự của lỗ hổng, thay vì chỉ báo cáo triệu chứng bề mặt. Ví dụ: học sinh làm sai bài phương trình chứa phân số không hẳn vì không hiểu phương trình, mà vì chưa nắm vững quy đồng phân số ở lớp dưới — hệ thống cần chỉ ra chính xác điểm gốc này.

### 2.4. Các trường hợp cần xử lý cẩn thận (fallback)

- **Học sinh mới, chưa có dữ liệu nào**: hệ thống dùng giá trị mặc định (xác suất biết trước ở mức prior đã đặt), đồng thời cần ghi rõ trong log rằng đây là ước lượng dựa trên giá trị mặc định, không phải dựa trên dữ liệu thực tế của học sinh đó — để tránh nhầm lẫn khi diễn giải kết quả sau này.
- **Kỹ năng được hỏi tới không tồn tại trong đồ thị kiến thức**: hệ thống cần báo lỗi rõ ràng ngay tại đây, để lớp LLM phía trên có thể trả lời "chưa đủ dữ liệu để chẩn đoán" một cách trung thực, thay vì để toàn bộ hệ thống bị lỗi ngầm hoặc trả về kết quả sai lệch.
- **Không tìm được gốc rễ nào đáng lo ngại** (tất cả các kỹ năng liên quan đều ở mức ổn): cần trả về kết quả rỗng kèm thông báo rõ ràng, tuyệt đối không để LLM tự suy diễn ra một lỗ hổng không có thật.

### 2.5. Yêu cầu kiểm thử

Trước khi tích hợp vào hệ thống, engine cần được kiểm thử với các kịch bản: (1) học sinh trả lời đúng liên tục — xác suất thành thạo phải tăng dần và tiệm cận về mức cao; (2) học sinh trả lời sai liên tục — xác suất phải giảm dần; (3) một kịch bản được thiết kế sẵn có đúng một kỹ năng gốc bị hổng — kiểm tra hệ thống có truy ngược tìm đúng kỹ năng đó hay không; (4) các trường hợp lỗi đã liệt kê ở mục 2.4 phải được xử lý đúng như mô tả, không được để hệ thống crash.

---

## 3. Đồ thị tri thức (Knowledge Graph)

Đồ thị tri thức mô tả các kỹ năng toán học và quan hệ tiên quyết giữa chúng (kỹ năng nào cần học trước kỹ năng nào). Về mặt kỹ thuật, đây là một đồ thị có hướng, nơi mỗi kỹ năng là một node và mỗi quan hệ tiên quyết là một cạnh nối. Việc truy ngược tìm gốc rễ lỗ hổng ở mục 2.3 thực chất là một phép duyệt đồ thị theo chiều ngược của các cạnh này.

Nội dung đồ thị nên lấy từ chương trình Giáo dục phổ thông môn Tiếng Anh — đây là tài liệu chính thức, công khai trên cổng thông tin của Bộ Giáo dục và Đào tạo, có sẵn mã số kỹ năng theo từng khối lớp. Vì thời gian hạn chế, nhóm nên chọn một mạch kiến thức hẹp và có liên hệ rõ ràng — ví dụ mạch "Phân số → Phương trình bậc nhất" ở Toán lớp 6–7 — với khoảng 20 đến 30 kỹ năng, thay vì cố gắng phủ toàn bộ chương trình.

Lưu ý quan trọng: tài liệu chương trình chính thức chỉ liệt kê yêu cầu cần đạt theo từng khối lớp, **không có sẵn quan hệ tiên quyết giữa các kỹ năng** — phần này cần người hiểu nội dung môn học tự xác định dựa theo thứ tự giảng dạy thực tế trong sách giáo khoa (nhóm sách Kết Nối Tri Thức, Chân Trời Sáng Tạo, hoặc Cánh Diều đều có thể dùng làm tham khảo thứ tự).

---

## 4. Tầng 1 và Tầng 3 — Vai trò của LLM

### 4.1. Lựa chọn model

Hệ thống hiện đã dùng API của FPT làm nền tảng LLM cho Planner Agent. Đề xuất phân bổ theo mức độ phức tạp của từng tác vụ: dùng model có chất lượng cao hơn (Claude Sonnet 5) cho Planner Agent chính và cho việc diễn giải kết quả BKT — vì đây là nơi cần văn phong tự nhiên, đúng ngữ cảnh, đúng tông với từng đối tượng người nghe. Với các tác vụ đơn giản và lặp lại nhiều lần — như trích xuất dữ liệu có cấu trúc đơn giản hoặc sinh hàng loạt câu hỏi luyện tập — có thể dùng một model nhẹ và nhanh hơn (Claude Haiku) để tiết kiệm thời gian phản hồi và chi phí khi demo nhiều lần.

### 4.2. Tầng Input — trích xuất dữ liệu có cấu trúc

Vai trò của LLM ở tầng này là đọc các tài liệu không có cấu trúc — như file PDF chương trình học hoặc hồ sơ học sinh viết dưới dạng văn xuôi — và chuyển chúng thành dữ liệu có cấu trúc rõ ràng (ví dụ: danh sách kỹ năng kèm mã số, hoặc hồ sơ học sinh dạng các trường thông tin cụ thể). Kỹ thuật cần dùng là ép LLM trả về đúng định dạng đầu ra mong muốn (structured output), tránh việc phải tự phân tích văn bản tự do sau đó.

Đây là phần có thể xếp vào nhóm công việc mở rộng, không bắt buộc để hệ thống chạy được bản demo cơ bản — vì đồ thị kiến thức viết tay ở mục 3 đã là phương án chính, đủ để chạy thử nghiệm mà không cần chờ phần trích xuất tự động này hoàn thiện.

### 4.3. Tầng Output — diễn giải kết quả

Đây là phần bắt buộc phải có. Sau khi BKT Engine tính ra danh sách các kỹ năng bị hổng kèm mức độ tin cậy, LLM có nhiệm vụ diễn giải cùng một dữ liệu đó thành hai văn phong khác nhau tùy theo người đọc:

- Với giáo viên: trình bày rõ ràng, có thể dùng thuật ngữ chuyên môn, kèm số liệu cụ thể.
- Với phụ huynh: dùng ngôn ngữ đơn giản, phi kỹ thuật, kèm gợi ý hành động cụ thể có thể thực hiện tại nhà (ví dụ: dành 15 phút mỗi ngày để ôn lại một kỹ năng cụ thể).

Nguyên tắc bắt buộc trong hướng dẫn hệ thống (system prompt) của LLM: chỉ được diễn giải những con số và kỹ năng thực sự do BKT Engine trả về, tuyệt đối không được tự suy diễn hay thêm thắt lỗ hổng kiến thức không có trong kết quả tính toán. Đây là yêu cầu cốt lõi để đảm bảo tiêu chí về độ tin cậy và an toàn của hệ thống AI.

---

## 5. Cách nối vào hệ thống hiện có — 4 công cụ (tools) cần xây dựng

Toàn bộ logic ở Tầng 2 và Tầng 3 cần được đóng gói thành các "công cụ" (tools) để Planner Agent (LLM chính điều phối hội thoại) có thể gọi tới khi cần, thay vì viết logic trực tiếp vào luồng hội thoại. Bốn công cụ cần có:

1. **Công cụ chẩn đoán lỗ hổng**: nhận vào thông tin học sinh và các câu trả lời đã làm, gọi tới BKT Engine để tính toán và trả về danh sách các kỹ năng bị hổng kèm mức độ tin cậy và lời giải thích. Đây là công cụ quan trọng nhất trong toàn bộ hệ thống.

2. **Công cụ sinh lộ trình luyện tập**: nhận vào danh sách lỗ hổng đã xác định, chọn ra các câu hỏi phù hợp theo từng kỹ năng, sắp xếp theo độ khó tăng dần để học sinh luyện tập.

3. **Công cụ tổng hợp cho giáo viên**: nhận vào mã lớp học, tổng hợp tình trạng lỗ hổng của toàn bộ học sinh trong lớp thành dạng biểu đồ nhiệt theo từng kỹ năng, nhóm các học sinh có cùng vấn đề lại với nhau, xếp hạng mức độ ưu tiên cần can thiệp, và cảnh báo nếu một kỹ năng nào đó có tỷ lệ học sinh hổng vượt ngưỡng đáng lo ngại. Công cụ này chỉ được phép trả về dữ liệu của đúng lớp học được yêu cầu, không được để lộ dữ liệu của lớp khác.

4. **Công cụ tổng hợp cho phụ huynh**: nhận vào thông tin học sinh và phụ huynh, trả về tiến độ học tập theo thời gian kèm gợi ý hành động cụ thể tại nhà. Công cụ này bắt buộc phải kiểm tra quyền truy cập — chỉ phụ huynh đúng của học sinh đó mới được xem dữ liệu, nếu không khớp phải trả về thông báo từ chối quyền truy cập rõ ràng, không được trả về kết quả rỗng gây hiểu lầm là "không có dữ liệu".

Bốn công cụ này được đăng ký vào phần thích ứng riêng cho dự án giáo dục trong hệ thống hiện có (domain adapter), theo đúng cấu trúc kiến trúc đã có sẵn — không cần sửa đổi phần điều phối hội thoại chính, phần đăng ký công cụ chung, hay phần giao tiếp với người dùng.

---

## 6. Nguồn dữ liệu

- **Dữ liệu đồ thị kỹ năng**: lấy từ chương trình Giáo dục phổ thông 2018 môn Toán (tài liệu chính thức, công khai trên cổng thông tin Bộ Giáo dục và Đào tạo).
- **Ngân hàng câu hỏi luyện tập**: lấy từ sách bài tập đi kèm sách giáo khoa chương trình mới, hoặc các trang bài tập theo chương trình phổ biến (VietJack, Lời Giải Hay, Hoc247, Violympic) — seed thủ công một số lượng câu hỏi vừa đủ cho các kỹ năng trong đồ thị đã chọn; nếu còn thời gian, có thể dùng LLM sinh thêm câu hỏi theo đúng kỹ năng và độ khó mong muốn, nhưng cần người có chuyên môn rà soát lại nội dung.
- **Dữ liệu để kiểm thử thuật toán**: có thể tham khảo các bộ dữ liệu công khai về theo dõi tri thức học sinh từ cộng đồng nghiên cứu quốc tế (như ASSISTments, EdNet) để kiểm tra logic của thuật toán hoạt động đúng, nhưng những bộ dữ liệu này là tiếng Anh và không khớp chương trình Việt Nam nên chỉ dùng cho việc kiểm thử nội bộ, không dùng để hiển thị trong bản demo.
- **Dữ liệu học sinh, lớp học, phụ huynh cho bản demo**: nên tự sinh dữ liệu giả (không dùng dữ liệu học sinh thật), thiết kế sẵn một kịch bản có lỗ hổng kiến thức rõ ràng ở đúng một kỹ năng gốc để khi demo, hệ thống có thể chứng minh rõ ràng khả năng truy tìm gốc rễ chính xác. Việc tránh dùng dữ liệu thật của học sinh (đối tượng vị thành niên) là cần thiết vì lý do đạo đức và pháp lý liên quan đến bảo vệ dữ liệu cá nhân.

---


## 7. Rủi ro cần nhóm trưởng lưu ý

1. Không để đội bỏ qua việc xây dựng BKT Engine để làm nhanh hơn bằng cách để LLM tự đoán lỗ hổng — điều này sẽ làm mất hoàn toàn điểm khác biệt của sản phẩm so với các đội khác.
2. Không dùng dữ liệu học sinh thật cho bản demo, chỉ dùng dữ liệu tự sinh.
3. Cần ghi lại nhật ký sử dụng AI ngay sau khi mỗi phần được tạo ra, không dồn lại đến cuối, vì ban tổ chức sẽ đối chiếu nhật ký này với lịch sử commit thực tế.
4. Việc kiểm thử kiểm soát quyền truy cập (cho công cụ dành cho giáo viên và phụ huynh) là bằng chứng trực tiếp cho tiêu chí về độ an toàn và độ tin cậy của hệ thống AI trong thang điểm chấm — không nên bỏ qua vì tưởng là chi tiết nhỏ.
5. Nếu thời gian quá gấp, bốn việc tối thiểu không thể bỏ là: chuẩn bị dữ liệu đồ thị kỹ năng, xây dựng BKT Engine, xây dựng công cụ chẩn đoán lỗ hổng, và nối công cụ này vào luồng hội thoại chính thông qua domain adapter. Đây là ranh giới giữa một sản phẩm AI-native thực sự và một chatbot thông thường.


# Đề xuất tối ưu Prompt — Đề xuất & Chọn Lộ trình thay thế khi Học sinh làm lại đề nhiều lần chưa đạt (<50%)

> Tình huống xử lý: cùng một đề khảo sát được học sinh làm lại **trên 2 lần** (từ lần thứ 3 trở lên) mà kết quả lần gần nhất **vẫn dưới 50%**. Hệ thống chủ động đề xuất cho giáo viên **tối thiểu 3 lộ trình chi tiết** khác nhau, giáo viên **tích chọn 1 lộ trình phù hợp riêng cho học sinh đó** để áp dụng.

---

## 1. Điều kiện kích hoạt — tính từ dữ liệu, không phải LLM tự quyết định

Điều kiện kích hoạt phải được xác nhận trước ở tầng dữ liệu (BKT Engine + lịch sử làm bài), LLM chỉ được gọi sau khi điều kiện đã được xác nhận là đúng.

**Logic kích hoạt cụ thể:**
- Học sinh làm lại **cùng một đề khảo sát** từ lần thứ 3 trở lên (trên 2 lần).
- Kết quả (điểm số hoặc mastery trung bình các kỹ năng trong đề) ở lần làm gần nhất **dưới 50%**.
- Chỉ tính các lượt làm bài **hợp lệ** — áp dụng bộ lọc chống spam: thời gian giữa 2 lần làm liên tiếp phải trên một ngưỡng tối thiểu (ví dụ 5 phút, điều chỉnh theo độ dài đề thực tế), kết hợp thêm tỷ lệ hoàn thành đề (đã trả lời đủ số câu, không nộp bừa) — các lượt không đạt bộ lọc này được lưu lại nhưng gắn cờ "không hợp lệ", không tính vào chuỗi đếm số lần làm lại.

**Vì sao kết hợp cả "số lần" và "ngưỡng <50%" thay vì chỉ dùng 1 điều kiện:** chỉ dùng ngưỡng điểm số đơn lẻ có thể kích hoạt sai với học sinh mới làm 1 lần (chưa đủ dữ liệu kết luận "không tiến bộ dù đã cố"); chỉ dùng số lần làm lại mà không xét điểm có thể kích hoạt nhầm với học sinh đang dần cải thiện (ví dụ từ 40% lên 55%) — trường hợp này chưa cần can thiệp gấp.

---

## 2. Nguyên tắc nền khi thiết kế prompt

- **Grounding là ưu tiên số một**: cả 3 lộ trình phải xây dựng từ dữ liệu thật (lịch sử làm bài, mastery hiện tại, đồ thị kỹ năng) — không được bịa kỹ năng hay số liệu không có trong dữ liệu.
- **Đối tượng đọc là giáo viên**: có thể dùng thuật ngữ chuyên môn, cần đủ chi tiết để ra quyết định.
- **3 lộ trình phải khác biệt thật sự về bản chất**, không phải 3 cách diễn đạt khác nhau của cùng một ý — đây là thách thức kỹ thuật chính, xử lý ở Mục 3.
- **Hệ thống chỉ đề xuất, không tự áp dụng** — quyết định cuối cùng và hành động tích chọn thuộc về giáo viên (chi tiết luồng ở Mục 5).

---

## 3. Kỹ thuật tối ưu prompt để sinh 3 lộ trình thực sự khác biệt

### 3.1. Gộp thành 1 lệnh gọi LLM duy nhất, ép schema JSON chặt

Vì đây là tính năng kích hoạt không thường xuyên (chỉ khi đúng điều kiện ở Mục 1), ưu tiên gộp 1 lệnh gọi thay vì 3 lệnh song song — tiết kiệm chi phí/độ trễ mà vẫn đảm bảo chất lượng nếu ép schema đúng cách:

- Yêu cầu model trả về JSON có đúng 3 phần tử.
- Mỗi phần tử **bắt buộc gán cứng 1 trong 3 trục chiến lược** ngay trong cấu trúc dữ liệu (không để model tự chọn tự do):
  1. **Quay lại gốc rễ sâu hơn** — mở rộng ôn các kỹ năng tiên quyết xa hơn trong đồ thị, không chỉ dừng ở kỹ năng ngay trước đó.
  2. **Đổi nhịp độ và mật độ luyện tập** — giữ nguyên phạm vi kỹ năng, nhưng giãn thời gian, giảm số câu mỗi buổi, tăng số lần lặp lại thay vì tăng độ khó nhanh.
  3. **Đổi hình thức tiếp cận** — giữ nguyên nội dung kỹ năng, nhưng đổi cách tiếp cận (học nhóm/kèm 1-1, đổi dạng bài tập từ trắc nghiệm sang có hướng dẫn từng bước).
- Mỗi phần tử JSON bắt buộc có các trường: tên trục chiến lược, danh sách kỹ năng mục tiêu (lấy từ đồ thị kỹ năng thật), thay đổi cụ thể so với lộ trình cũ, thời lượng ước tính, kết quả kỳ vọng, điểm cần lưu ý/rủi ro.

### 3.2. Đưa số liệu cụ thể của tình huống <50% thẳng vào phần bối cảnh

Truyền vào prompt số liệu thực tế thay vì mô tả chung chung — ví dụ: "học sinh đã làm lại đề này 3 lần, kết quả gần nhất 42%, lần trước đó 38%, các kỹ năng sai lặp lại qua các lần là...". Số liệu càng cụ thể, phần lý luận của model càng bám sát thực tế, và giáo viên đọc phần giải thích cũng thấy rõ căn cứ ra quyết định thay vì lời khuyên chung chung.

### 3.3. Bắt buộc nêu điểm khác biệt ngay câu đầu tiên của mỗi lộ trình

Ràng buộc trong prompt: câu đầu tiên của mỗi lộ trình phải nêu rõ **điều gì làm hướng này khác 2 hướng còn lại** (ví dụ: "Khác với việc chỉ ôn kỹ năng gần nhất, hướng này mở rộng ôn cả kỹ năng nền tảng từ 2 cấp trước đó"). Đưa kèm 1 ví dụ mẫu (few-shot) trong prompt để cố định định dạng này.

### 3.4. Chain-of-thought ngắn trước khi đề xuất từng lộ trình

Yêu cầu model tóm tắt ngắn gọn lý do lộ trình cũ chưa hiệu quả (dựa trên dữ liệu điểm không cải thiện qua các lần) trước khi viết lộ trình mới theo trục đã gán — giúp lộ trình mới thực sự "phản hồi" lại vấn đề cũ, không phải phương án ngẫu nhiên.

### 3.5. Temperature ở mức thấp-vừa (khoảng 0.3–0.5)

Khác với tầng diễn giải lộ trình thông thường (nên đặt rất thấp), ở tác vụ sinh 3 phương án cần một chút không gian để văn phong giữa 3 lộ trình không bị máy móc giống hệt nhau — nhưng phần dữ liệu/kỹ năng vẫn phải bám ràng buộc grounding, không phụ thuộc vào temperature.

### 3.6. Kiểm tra trùng lặp ở tầng code — dùng phép đếm đơn giản, không cần thuật toán phức tạp

Với chỉ 3 phần tử cần so sánh, không cần triển khai Cosine Similarity cho phần mô tả văn bản (đòi hỏi thêm embedding model, không đáng đầu tư cho quy mô này). Thay vào đó:
- So sánh tập hợp Skill ID giữa các lộ trình bằng phép đếm giao tập hợp đơn giản (`số kỹ năng chung / tổng số kỹ năng của lộ trình ngắn hơn`).
- Tận dụng trường `strategy_axis` đã ép cứng ở Mục 3.1 — nếu 3 phần tử đều có trục chiến lược khác nhau, gần như chắc chắn nội dung đã khác biệt về bản chất, không cần đo thêm ở tầng văn bản.
- Nếu phát hiện trùng lặp Skill ID vượt ngưỡng đơn giản (ví dụ trên 70%), chỉ cần gắn cờ cảnh báo hiển thị nhẹ cho giáo viên, không cần tự động gọi lại model để sinh lại (tốn thêm 1 lượt gọi không cần thiết cho bản demo).

---

## 4. Cấu trúc prompt tổng thể (mô tả, không phải code)

1. **Vai trò**: AI đóng vai trợ lý sư phạm, chỉ đề xuất phương án dựa trên dữ liệu, không tự quyết định thay giáo viên.
2. **Bối cảnh tình huống**: số lần đã làm đề, điểm số từng lần, các kỹ năng sai lặp lại, lộ trình cũ đã áp dụng (để model biết phải khác đi từ đâu).
3. **Yêu cầu schema JSON**: 3 phần tử, mỗi phần tử gán cứng 1 trục chiến lược, đầy đủ các trường đã liệt kê ở Mục 3.1.
4. **Ví dụ mẫu (few-shot)**: 1 ví dụ input/output ngắn minh hoạ đúng định dạng và cách nêu điểm khác biệt ở câu đầu.
5. **Ràng buộc grounding**: không được bịa kỹ năng ngoài đồ thị, không đổi độ khó/thứ tự ngoài phạm vi đã cho phép theo trục chiến lược tương ứng.
6. **Ghi chú vai trò giáo viên**: đây là gợi ý để giáo viên xem xét và chọn, không phải thay đổi đã được áp dụng.

---

## 5. Luồng giáo viên tích chọn lộ trình cho đúng học sinh

### 5.1. Hiển thị theo hàng đợi riêng từng học sinh, không gộp chung

Vì nhiều học sinh có thể cùng lúc rơi vào điều kiện kích hoạt, giao diện giáo viên hiển thị danh sách các đề xuất đang chờ xử lý, mỗi mục gắn rõ: mã/tên học sinh, đề khảo sát liên quan, số lần đã làm, điểm số từng lần, và 3 lộ trình đề xuất kèm theo. Giáo viên tích chọn đúng 1 lộ trình **cho đúng học sinh đó** — không có cơ chế chọn hàng loạt cho nhiều học sinh cùng lúc, vì mỗi học sinh có dữ liệu mastery riêng, lộ trình phù hợp cũng khác nhau dù cùng nằm trong danh sách chờ.

### 5.2. Ràng buộc khi lưu lựa chọn của giáo viên

- Bản ghi lựa chọn gắn chắc chắn với **mã học sinh + mã đề khảo sát + mốc thời gian phát hiện kích hoạt** — tránh lẫn lộn nếu cùng học sinh có nhiều lần kích hoạt khác nhau (ở các đề khác nhau, hoặc cùng đề nhưng lần trước đã xử lý xong).
- Sau khi xác nhận, lộ trình học của **riêng học sinh đó** được cập nhật theo nội dung đã chọn — không ảnh hưởng học sinh khác dù cùng lớp, cùng đề, cùng rơi vào điều kiện kích hoạt.
- Lưu lại **cả 3 phương án đã đề xuất và phương án đã chọn** trong lịch sử, không chỉ lưu kết quả cuối — hữu ích để xem lại căn cứ quyết định, và làm bằng chứng minh bạch khi trình bày với giám khảo.

### 5.3. Kiểm tra quyền hạn khi giáo viên thao tác

Kế thừa nguyên tắc kiểm soát quyền truy cập đã áp dụng cho các công cụ dành cho giáo viên: chỉ được xem và xử lý đề xuất của học sinh thuộc đúng lớp mình phụ trách. Khi nhận yêu cầu xác nhận lựa chọn, hệ thống cần kiểm tra lại quyền này ở tầng xử lý, không chỉ dựa vào việc giao diện chỉ hiển thị đúng danh sách.

### 5.4. Trạng thái chưa xử lý không tự động hết hạn hay tự áp dụng

Nếu giáo viên chưa xử lý, hệ thống giữ nguyên lộ trình cũ của học sinh cho đến khi có xác nhận chủ động — không tự động chọn hộ 1 trong 3 lộ trình sau một khoảng thời gian nào đó. Giữ đúng nguyên tắc con người luôn là người quyết định cuối cùng cho các thay đổi ảnh hưởng trực tiếp đến việc học của học sinh.

### 5.5. Cho phép giáo viên từ chối cả 3 phương án

Có thêm lựa chọn thứ 4 ngoài 3 lộ trình: "giữ nguyên lộ trình hiện tại" — tránh ép giáo viên phải chọn 1 trong 3 nếu cả 3 đều chưa thực sự phù hợp theo đánh giá riêng của giáo viên, người hiểu học sinh hơn dữ liệu số thuần túy.

---

## 6. Cách nối vào kiến trúc hệ thống hiện có

- **Công cụ đề xuất lộ trình thay thế**: nhận vào lịch sử làm bài của học sinh (đã qua bộ lọc chống spam) và lộ trình cũ, kiểm tra điều kiện kích hoạt (số lần + ngưỡng <50%), nếu đúng điều kiện thì gọi 1 lệnh LLM theo schema đã thiết kế ở Mục 3, kiểm tra trùng lặp ở tầng code, trả về 3 lộ trình có cấu trúc.
- **Công cụ xác nhận lựa chọn của giáo viên**: nhận vào mã học sinh, mã đề xuất đang chờ xử lý, lộ trình được chọn (hoặc "giữ nguyên"), kiểm tra quyền truy cập, sau đó cập nhật lộ trình học của đúng học sinh đó trong cơ sở dữ liệu.
- **Bảng lưu lịch sử đề xuất** cần có các trường: mã học sinh, mã đề khảo sát, số lần đã làm hợp lệ, điểm số từng lần, nội dung cả 3 lộ trình đã sinh, lộ trình được chọn (nếu có), trạng thái xử lý (chờ / đã chọn / đã giữ nguyên), thời gian xác nhận.
- Hiển thị trong phần tổng hợp dành cho giáo viên đã có sẵn trong kiến trúc — mở rộng thêm mục "đề xuất đang chờ xử lý" theo từng học sinh, không cần tạo giao diện hoàn toàn mới.

---

## 7. Tổng hợp kỹ thuật theo mức độ ưu tiên

| Kỹ thuật | Mức ưu tiên | Lý do |
|---|---|---|
| Điều kiện kích hoạt kết hợp số lần + ngưỡng <50%, tính từ dữ liệu | Cao | Nền tảng bắt buộc, sai điều kiện này thì mọi thứ phía sau vô nghĩa |
| Bộ lọc chống spam (thời gian tối thiểu + tỷ lệ hoàn thành) | Cao | Ảnh hưởng trực tiếp độ tin cậy của điều kiện kích hoạt |
| Gộp 1 lệnh gọi LLM, ép schema gán cứng 3 trục chiến lược | Cao | Cân bằng chi phí/độ trễ với chất lượng phân biệt |
| Đưa số liệu cụ thể vào bối cảnh prompt | Cao | Dễ làm, tăng đáng kể độ bám sát thực tế |
| Yêu cầu nêu điểm khác biệt ở câu đầu | Trung bình | Dễ thêm vào prompt, tăng chất lượng phân biệt rõ rệt |
| Kiểm tra trùng lặp bằng đếm giao tập hợp Skill ID | Trung bình | Đủ hiệu quả cho quy mô 3 phần tử, không cần thuật toán phức tạp |
| Hàng đợi riêng theo từng học sinh, không gộp chung | Cao | Bắt buộc để tránh nhầm lẫn khi áp dụng lộ trình cho đúng học sinh |
| Kiểm tra quyền hạn ở tầng xử lý xác nhận | Cao | Yêu cầu an toàn cốt lõi, không thể bỏ qua |
| Không tự động hết hạn/áp dụng khi chưa xác nhận | Cao | Giữ nguyên tắc con người quyết định cuối cùng |
| Lựa chọn "giữ nguyên lộ trình hiện tại" | Trung bình | Tôn trọng đánh giá chuyên môn của giáo viên |

---

## 8. Lưu ý khi trình bày với giám khảo

Tính năng này minh chứng trực tiếp cho tiêu chí an toàn AI và độ tin cậy: hệ thống không tự ý thay đổi lộ trình học khi phát hiện học sinh gặp khó khăn, mà **chủ động cảnh báo bằng dữ liệu cụ thể (số lần làm lại, điểm số dưới ngưỡng), đưa ra nhiều phương án có căn cứ, và để giáo viên — người hiểu học sinh thực tế — là người quyết định cuối cùng cho từng cá nhân học sinh**. Đây vừa là điểm mạnh sản phẩm, vừa thể hiện tư duy đạo đức AI trong giáo dục: AI hỗ trợ ra quyết định, không thay thế vai trò sư phạm của con người.
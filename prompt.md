# Đề xuất phương pháp tối ưu Prompt cho Lộ trình học tập cá nhân hoá theo Style học tập — V-NEXUS SCHOOL Adaptive Learning Platform

> Mở rộng từ tầng LLM Output Layer đã có (diễn giải kết quả BKT thành lộ trình), bổ sung thêm một trục dữ liệu đầu vào mới: **phong cách học tập (learning style)** của từng học sinh, thu thập qua một bộ câu hỏi khảo sát ngắn, để lộ trình không chỉ đúng về nội dung (dựa trên mastery/gap) mà còn đúng về cách trình bày, phù hợp với từng học sinh.

---

## 1. Nguyên tắc nền tảng (giữ nguyên, nhắc lại vì rất quan trọng)

**LLM vẫn không được quyết định lộ trình nội dung — chỉ được điều chỉnh cách trình bày lộ trình.** Thứ tự kỹ năng, mức độ khó, kỹ năng nào cần luyện trước vẫn hoàn toàn do BKT Engine và thuật toán chọn câu hỏi quyết định dựa trên dữ liệu mastery thực tế — đây là phần không đổi so với thiết kế trước.

Điểm mới ở đây: dữ liệu **style học tập** chỉ được phép ảnh hưởng đến:
- Cách diễn đạt nội dung từng bước (nhiều ví dụ trực quan hay nhiều bước logic tuần tự).
- Định dạng trình bày (dùng hình minh hoạ/sơ đồ mô tả bằng lời, hay danh sách gạch đầu dòng, hay đoạn văn kể chuyện).
- Gợi ý hình thức luyện tập đi kèm (câu hỏi trắc nghiệm, bài tập viết tay, giải thích bằng lời).

Style học tập **không được phép** thay đổi nội dung kiến thức, thứ tự kỹ năng, hay độ khó câu hỏi — những yếu tố này vẫn do engine quyết định. Đây là ranh giới cần giữ để tránh style học tập bị lạm dụng thành lý do cho AI "tự sáng tạo" lộ trình ngoài dữ liệu thật.

---

## 2. Thiết kế bộ câu hỏi đánh giá style học tập

### 2.1. Vì sao cần một bộ câu hỏi ngắn, không phải bài trắc nghiệm dài

Trong thời gian hackathon, không nên áp dụng nguyên bộ công cụ đánh giá phong cách học tập học thuật đầy đủ (thường có vài chục câu) — sẽ tốn thời gian học sinh làm và tốn thời gian đội xử lý. Nên rút gọn còn khoảng 5–7 câu hỏi trắc nghiệm ngắn, đủ để phân loại học sinh vào một vài nhóm phong cách chính, đo lường được ngay và dùng được ngay trong demo.

### 2.2. Khung phân loại đề xuất (đơn giản hoá từ mô hình VARK — Visual, Auditory, Reading/Writing, Kinesthetic)

Đây là một khung phân loại phong cách học tập phổ biến, dễ diễn giải với người không chuyên (giáo viên, phụ huynh), và dễ ánh xạ sang cách trình bày nội dung:

- **Trực quan (Visual)**: học tốt hơn qua hình ảnh, sơ đồ, màu sắc.
- **Nghe (Auditory)**: học tốt hơn qua giải thích bằng lời, âm thanh.
- **Đọc/Viết (Reading/Writing)**: học tốt hơn qua văn bản, danh sách, ghi chú.
- **Vận động (Kinesthetic)**: học tốt hơn qua thực hành trực tiếp, ví dụ cụ thể, làm bài tập ngay.

### 2.3. Ví dụ dạng câu hỏi khảo sát (mô tả, không phải bảng câu hỏi đầy đủ)

Mỗi câu hỏi nên đưa ra một tình huống học tập ngắn kèm 4 lựa chọn, mỗi lựa chọn tương ứng với một trong 4 phong cách trên. Ví dụ dạng câu hỏi: "Khi gặp một bài toán khó, em thích được giúp đỡ theo cách nào nhất?" với các lựa chọn tương ứng: xem hình vẽ minh hoạ cách giải, nghe giáo viên giảng lại từng bước, đọc lời giải chi tiết viết sẵn, hoặc tự thử làm với vài gợi ý nhỏ.

Sau khi học sinh trả lời hết bộ câu hỏi, hệ thống tính điểm cho mỗi nhóm phong cách (đếm số lần chọn tương ứng), phong cách có điểm cao nhất (hoặc 2 phong cách nếu học sinh có xu hướng pha trộn) được lưu vào hồ sơ học sinh.

### 2.4. Vị trí đặt bộ câu hỏi này trong hệ thống

Bộ câu hỏi này nên được hỏi **một lần duy nhất** khi học sinh tạo hồ sơ lần đầu (tương tự bước "onboarding"), không hỏi lại mỗi lần tương tác. Kết quả lưu vào hồ sơ học sinh trong cơ sở dữ liệu như một trường thông tin tĩnh (có thể cập nhật lại sau nếu học sinh muốn làm lại khảo sát), tách biệt hoàn toàn với dữ liệu mastery/gap vốn thay đổi liên tục.

---

## 3. Cấu trúc prompt tối ưu khi có thêm dữ liệu style học tập

### 3.1. Prompt vẫn giữ 5 phần cốt lõi, bổ sung 1 phần mới

Giữ nguyên cấu trúc prompt đã đề xuất trước đó (vai trò, input có cấu trúc, ví dụ mẫu, ràng buộc định dạng, xử lý trường hợp biên), bổ sung thêm:

6. **Phần mô tả style học tập** — truyền vào như một trường dữ liệu riêng biệt, tách bạch rõ ràng với dữ liệu mastery/gap, kèm chỉ dẫn rõ style này chỉ ảnh hưởng đến CÁCH trình bày, không ảnh hưởng đến NỘI DUNG.

### 3.2. Kỹ thuật cụ thể

**Tách rõ 2 loại dữ liệu đầu vào trong prompt — nội dung (content) và phong cách (style)**
Nên trình bày tách biệt rõ ràng hai khối dữ liệu ngay trong prompt: một khối là "dữ liệu lộ trình" (kỹ năng, mastery, lý do, độ khó — bất biến, do engine quyết định), một khối là "hồ sơ phong cách học tập" (loại phong cách, mức độ ưu tiên). Việc tách bạch rõ ràng giúp model không nhầm lẫn hai loại thông tin có vai trò khác nhau, giảm rủi ro style học tập "lấn sân" sang việc quyết định nội dung.

**Ánh xạ style sang chỉ dẫn trình bày cụ thể, không để model tự suy diễn**
Thay vì chỉ ghi "học sinh có phong cách trực quan" và để model tự hiểu phải làm gì, nên đưa kèm chỉ dẫn cụ thể ngay trong prompt tương ứng với từng phong cách đã xác định trước, ví dụ: với phong cách trực quan — mô tả bằng lời một hình ảnh/sơ đồ minh hoạ trước khi giải thích; với phong cách vận động — ưu tiên đưa ngay một ví dụ bài tập ngắn để thử trước khi giải thích lý thuyết. Việc định nghĩa sẵn các chỉ dẫn này (thay vì để model tự suy diễn từ nhãn phong cách) giúp đầu ra nhất quán hơn giữa các lần gọi và dễ kiểm soát chất lượng hơn.

**Few-shot theo từng cặp (nội dung, phong cách)**
Chuẩn bị sẵn một vài ví dụ mẫu minh hoạ cùng một nội dung kỹ năng nhưng được trình bày khác nhau theo từng phong cách, đặt trong phần ví dụ của prompt. Kỹ thuật này giúp model học được cách "giữ nguyên nội dung, chỉ đổi cách trình bày" — đúng ranh giới đã đặt ra ở Mục 1, thay vì để model tự đoán mức độ ảnh hưởng của style đến nội dung.

**Trọng số ưu tiên khi học sinh có phong cách pha trộn**
Nếu kết quả khảo sát cho ra 2 phong cách gần bằng điểm nhau, nên truyền cả hai vào prompt kèm tỷ lệ ưu tiên (ví dụ 60/40), và chỉ dẫn model kết hợp nhẹ nhàng hai cách trình bày thay vì chọn cứng một phong cách duy nhất — tránh việc ép học sinh vào đúng một khuôn mẫu khi thực tế phong cách học tập thường không tuyệt đối.

**Giữ ràng buộc grounding xuyên suốt kể cả khi cá nhân hoá theo style**
Câu ràng buộc "không thêm/bớt/đổi thứ tự kỹ năng" cần được nhắc lại rõ trong prompt ngay cả khi đã thêm phần cá nhân hoá theo style — vì khi prompt phức tạp hơn (có thêm nhiều chỉ dẫn về trình bày), nguy cơ model "quên" ràng buộc gốc cũng tăng lên, nên đặt ràng buộc này ở vị trí dễ thấy, tốt nhất là nhắc lại cả ở đầu và cuối prompt.

**Tự kiểm tra 2 lớp trước khi trả lời**
Mở rộng bước self-check đã có trước đó, thêm 1 lớp kiểm tra mới: ngoài việc tự đối chiếu "mọi kỹ năng nhắc đến có nằm trong dữ liệu được cung cấp không", model cần tự đối chiếu thêm "cách trình bày có đúng với phong cách học tập đã chỉ định không, và có làm thay đổi nội dung kiến thức so với dữ liệu gốc không".

### 3.3. Thứ tự trình bày dữ liệu trong prompt được đề xuất

1. Vai trò và ràng buộc grounding tổng quát.
2. Khối dữ liệu lộ trình (nội dung — bất biến).
3. Khối hồ sơ phong cách học tập (cách trình bày — có thể linh hoạt).
4. Chỉ dẫn ánh xạ cụ thể từ phong cách sang cách viết.
5. Ví dụ mẫu theo từng cặp nội dung/phong cách.
6. Yêu cầu định dạng đầu ra theo đối tượng người đọc (học sinh/giáo viên/phụ huynh — như đã có).
7. Ràng buộc nhắc lại + yêu cầu tự kiểm tra 2 lớp.

---

## 4. Cách nối vào kiến trúc hệ thống hiện có

- Thêm một trường mới vào hồ sơ học sinh trong cơ sở dữ liệu để lưu kết quả phong cách học tập, tách biệt với bảng lưu tiến độ mastery.
- Bổ sung một bước khảo sát ngắn trong luồng tạo tài khoản/onboarding học sinh — có thể triển khai như một công cụ riêng (tương tự các công cụ khác đã có trong hệ thống) nhận câu trả lời khảo sát và trả về kết quả phân loại phong cách, tách biệt hoàn toàn khỏi công cụ chẩn đoán lỗ hổng kiến thức.
- Khi gọi tầng diễn giải lộ trình, truyền thêm dữ liệu phong cách học tập đã lưu vào cùng với dữ liệu mastery/gap như đã mô tả ở Mục 3.

---

## 5. Kiểm thử khi có thêm trục cá nhân hoá style

Chuẩn bị thêm các kịch bản kiểm thử kết hợp: cùng một dữ liệu mastery/gap nhưng gán cho các phong cách học tập khác nhau, kiểm tra xem đầu ra có (a) đúng thay đổi về cách trình bày theo từng phong cách, và (b) giữ nguyên nội dung kiến thức không đổi giữa các phiên bản. Đây là cách kiểm thử nhanh, không cần công cụ đánh giá phức tạp, chỉ cần so sánh trực tiếp các phiên bản đầu ra với nhau.

---

## 6. Tổng hợp kỹ thuật theo mức độ ưu tiên trong 48 giờ

| Kỹ thuật | Mức ưu tiên | Lý do |
|---|---|---|
| Bộ câu hỏi khảo sát rút gọn 5–7 câu | Cao | Cần có trước để có dữ liệu đầu vào cho mọi kỹ thuật khác |
| Tách rõ khối dữ liệu nội dung và phong cách trong prompt | Cao | Nền tảng để tránh style lấn sân sang nội dung |
| Ánh xạ style sang chỉ dẫn trình bày cụ thể (định nghĩa sẵn) | Cao | Kiểm soát chất lượng đầu ra tốt hơn để model tự suy diễn |
| Nhắc lại ràng buộc grounding ở đầu và cuối prompt | Cao | Rủi ro tăng khi prompt phức tạp hơn, cần ưu tiên phòng ngừa |
| Few-shot theo cặp nội dung/phong cách | Trung bình | Hiệu quả tốt nhưng cần thời gian soạn ví dụ |
| Xử lý trọng số khi phong cách pha trộn | Trung bình–thấp | Tinh tế hơn, có thể làm sau nếu còn thời gian |
| Self-check 2 lớp | Trung bình | Dễ thêm vào prompt đã có, nên làm nếu còn thời gian tinh chỉnh |

---

## 7. Lưu ý khi trình bày với giám khảo

Việc thêm trục phong cách học tập là một điểm cộng cho tiêu chí cá nhân hoá và trải nghiệm người dùng, nhưng cần nhấn mạnh rõ với giám khảo (qua slide hoặc khi trả lời câu hỏi) rằng: **phong cách học tập chỉ ảnh hưởng đến cách trình bày, còn nội dung và thứ tự lộ trình vẫn hoàn toàn dựa trên mô hình xác suất BKT** — tránh gây hiểu lầm rằng phần cá nhân hoá này làm giảm tính khoa học/minh bạch của lõi AI chính đã xây dựng.
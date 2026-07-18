# Đề xuất phương pháp chạy Offline cho V-NEXUS SCHOOL — Tầng Lộ trình học tập cá nhân hoá

> Áp dụng cho toàn bộ pipeline đã thiết kế: BKT Engine (đã offline sẵn) + tầng diễn giải lộ trình học tập đã tối ưu prompt (bao gồm cá nhân hoá theo mastery/gap và theo phong cách học tập). Tài liệu này tập trung vào cách đưa **lớp LLM** trong pipeline chạy được hoàn toàn không cần kết nối internet/API cloud.

---

## 1. Xác định lại phạm vi cần offline hoá

Trước khi chọn kỹ thuật, cần phân tách rõ hệ thống hiện có thành 2 nhóm:

| Thành phần | Đã offline sẵn? | Có cần xử lý gì thêm không |
|---|---|---|
| BKT Engine (tính mastery, truy gốc rễ lỗ hổng) | Đã offline hoàn toàn (thuật toán xác suất tự viết) | Không cần |
| Knowledge Graph (đồ thị kỹ năng) | Đã offline hoàn toàn (đọc file JSON local) | Không cần |
| Bộ câu hỏi khảo sát phong cách học tập + tính điểm | Đã offline hoàn toàn (logic đếm điểm đơn giản) | Không cần |
| Tầng diễn giải lộ trình bằng LLM (đã tối ưu prompt) | Đang phụ thuộc API Claude qua internet | **Đây là phần cần offline hoá** |
| Planner Agent (điều phối hội thoại, gọi tool) | Đang phụ thuộc API Claude qua internet | Cân nhắc theo mức độ ưu tiên (Mục 5) |

Việc offline hoá chỉ thực sự cần thiết cho **lớp LLM** — phần lõi tính toán đã tự chủ hoàn toàn theo đúng kiến trúc "AI thực sự, minh bạch" đã thống nhất từ đầu.

---

## 2. Chọn model chạy local phù hợp với prompt đã tối ưu

### 2.1. Yêu cầu đặc thù của prompt đã thiết kế

Prompt tầng diễn giải lộ trình (đã tối ưu ở tài liệu trước) có 3 đặc điểm cần model local đáp ứng tốt:
- **Tiếng Việt tự nhiên** — vì đầu ra hướng tới học sinh/giáo viên/phụ huynh Việt Nam.
- **Tuân thủ structured input/output** — vì prompt yêu cầu model đọc dữ liệu có cấu trúc (bảng mastery, hồ sơ phong cách học tập) và trả về đúng khuôn dạng đã quy định.
- **Bám sát ràng buộc grounding phức tạp** — prompt có nhiều ràng buộc lồng nhau (không đổi nội dung, chỉ đổi cách trình bày, tự kiểm tra 2 lớp) — đòi hỏi model có khả năng tuân thủ chỉ dẫn (instruction-following) tốt dù kích thước nhỏ.

### 2.2. Công cụ chạy model local: Ollama

Ollama là công cụ phổ biến nhất hiện nay để chạy LLM mã nguồn mở hoàn toàn trên máy cá nhân, cài đặt và tải model chỉ bằng 1–2 dòng lệnh, tự động lượng tử hoá để chạy vừa trên phần cứng phổ thông, và cung cấp sẵn một API tương thích chuẩn OpenAI ngay tại máy local — thuận lợi để tích hợp vào kiến trúc hiện có.

### 2.3. Model đề xuất theo cấu hình máy thực tế của nhóm (laptop sinh viên)

| Model | Kích thước (lượng tử hoá Q4) | RAM cần | Đánh giá cho use case này |
|---|---|---|---|
| **Qwen3 8B** | ~5GB | 8GB | Ưu tiên hàng đầu — hỗ trợ đa ngôn ngữ mạnh (bao gồm tiếng Việt), khả năng tuân thủ structured output tốt, giấy phép mở dùng thoải mái |
| **Qwen3 4B** | ~3GB | 4–6GB | Phương án dự phòng nếu máy demo yếu hơn, chất lượng giảm nhẹ nhưng vẫn chạy được prompt có cấu trúc |
| **Gemma 3 4B** | ~3GB | 8GB | Đa ngôn ngữ tốt, phương án thay thế nếu Qwen3 gặp vấn đề tương thích |
| **Phi-4-mini** | ~3GB | 4GB | Nhanh nhất, dùng nếu máy demo rất yếu, nhưng cần test kỹ chất lượng tiếng Việt trước khi chọn |

**Khuyến nghị chốt**: dùng **Qwen3 8B (Q4)** làm phương án chính nếu máy demo có tối thiểu 8GB RAM — cân bằng tốt nhất giữa chất lượng tiếng Việt, khả năng tuân thủ prompt có cấu trúc, và tốc độ phản hồi khi demo trực tiếp.

---

## 3. Kỹ thuật điều chỉnh prompt khi chuyển sang chạy local (khác với khi dùng Claude)

Prompt đã tối ưu cho Claude ở các tài liệu trước cần điều chỉnh thêm khi chạy trên model local nhỏ hơn, vì model nhỏ có xu hướng tuân thủ chỉ dẫn kém ổn định hơn:

### 3.1. Rút gọn số lượng ràng buộc đồng thời trong 1 prompt
Model nhỏ dễ "quên" một vài ràng buộc nếu prompt có quá nhiều lớp yêu cầu chồng lên nhau (nội dung bất biến, phong cách linh hoạt, 2 lớp self-check, định dạng đầu ra...). Nên **tách prompt phức tạp thành 2 lượt gọi model** thay vì 1 lượt duy nhất: lượt 1 chỉ tập trung sinh nội dung lộ trình đúng dữ liệu (grounding), lượt 2 chỉ tập trung điều chỉnh văn phong theo phong cách học tập dựa trên kết quả lượt 1. Cách này giảm tải nhận thức cho model nhỏ ở mỗi lượt gọi, dù tốn thêm 1 lần gọi model.

### 3.2. Rút ngắn few-shot examples
Model nhỏ có giới hạn cửa sổ ngữ cảnh hiệu quả thấp hơn model lớn dù về lý thuyết hỗ trợ ngữ cảnh dài — nên ưu tiên 1 ví dụ mẫu thật sát thay vì 2–3 ví dụ như khi dùng Claude, tránh làm loãng trọng tâm.

### 3.3. Dùng structured output dạng đơn giản hơn
Nếu model local gặp khó khăn khi trả JSON lồng nhau phức tạp (nhiều cấp), nên đơn giản hoá khuôn dạng đầu ra thành danh sách phẳng (mỗi bước là 1 dòng có các trường cách nhau rõ ràng) thay vì cấu trúc JSON lồng sâu — dễ parse ổn định hơn với model nhỏ.

### 3.4. Temperature thấp hơn nữa
Với model local, nên đặt nhiệt độ sinh còn thấp hơn mức đã đề xuất cho Claude (gần 0) — model nhỏ có xu hướng lệch khỏi ràng buộc nhiều hơn khi nhiệt độ tăng, nên ưu tiên độ ổn định hơn độ đa dạng văn phong.

### 3.5. Thêm bước validate sau khi model trả lời (kiểm tra ở tầng code, không chỉ dựa vào self-check trong prompt)
Vì model nhỏ tuân thủ self-check trong prompt kém tin cậy hơn model lớn, nên bổ sung một bước kiểm tra đơn giản ở tầng code sau khi nhận kết quả từ model: so khớp danh sách kỹ năng xuất hiện trong câu trả lời với danh sách kỹ năng có trong dữ liệu đầu vào; nếu phát hiện có kỹ năng lạ (không nằm trong dữ liệu gốc), hệ thống có thể yêu cầu model sinh lại hoặc trả về một thông báo lỗi rõ ràng thay vì hiển thị nội dung có khả năng bị bịa thêm. Đây là lớp bảo vệ bổ sung cần thiết khi hạ cấp từ Claude xuống model nhỏ hơn.

---

## 4. Cách tích hợp vào kiến trúc hiện có mà không phá vỡ cấu trúc

Kiến trúc hiện tại của repo đã tách lớp gọi LLM ra một module riêng (client wrapper), đây là điểm thuận lợi lớn để chuyển đổi:

- **Tạo thêm một client thay thế** implement cùng giao diện với client hiện có (nhận vào tin nhắn, trả về văn bản hoặc lệnh gọi công cụ), nhưng trỏ tới địa chỉ API local của Ollama thay vì endpoint của Claude.
- **Domain Adapter và Planner Agent không cần biết đang gọi model nào** — miễn giao diện giữ nguyên, đúng theo nguyên tắc tách lớp đã có sẵn trong kiến trúc repo, không cần sửa các phần khác của hệ thống.
- **Chuyển đổi giữa 2 chế độ (cloud/local) bằng một biến cấu hình** (ví dụ một biến môi trường), để có thể chuyển nhanh giữa lúc phát triển (dùng Claude cho chất lượng cao) và lúc demo dự phòng (dùng model local khi không có mạng).

---

## 5. Mức độ offline hoá đề xuất theo từng thành phần

Không nhất thiết phải offline hoá toàn bộ hệ thống LLM — nên phân cấp theo mức độ rủi ro khi mất mạng lúc demo:

| Thành phần | Có cần offline không | Lý do |
|---|---|---|
| Tầng diễn giải lộ trình học tập | Nên có phương án offline dự phòng | Đây là phần hiển thị trực tiếp cho giám khảo xem, rủi ro cao nhất nếu mất mạng giữa demo |
| Planner Agent (hội thoại chính, chọn tool) | Cân nhắc theo thời gian còn lại | Phức tạp hơn (cần tuân thủ định dạng gọi tool chính xác), model nhỏ có rủi ro cao hơn khi đảm nhiệm vai trò này |
| Tầng trích xuất dữ liệu có cấu trúc từ tài liệu (nếu có làm) | Không cần thiết phải offline | Đây là công việc chuẩn bị trước, không diễn ra trong lúc demo trực tiếp |

**Khuyến nghị cho 48 giờ**: chỉ cần đảm bảo chắc chắn tầng diễn giải lộ trình học tập có phương án offline dự phòng đã test kỹ. Việc offline hoá cả Planner Agent chỉ nên làm nếu còn nhiều thời gian dư, vì độ phức tạp và rủi ro cao hơn hẳn.

---

## 6. Quy trình kiểm thử trước khi tin tưởng dùng offline cho demo

1. Chạy đúng bộ prompt đã tối ưu (bao gồm cả nhánh cá nhân hoá theo phong cách học tập) trên model local với toàn bộ các kịch bản dữ liệu mẫu đã chuẩn bị sẵn từ trước.
2. So sánh trực tiếp chất lượng đầu ra giữa bản chạy trên Claude và bản chạy trên model local, ghi nhận lại những chỗ model local cho kết quả kém tự nhiên hơn để tinh chỉnh thêm prompt riêng cho nhánh offline nếu cần.
3. Đo thời gian phản hồi thực tế trên đúng máy sẽ dùng để demo (không phải máy có cấu hình mạnh nhất của nhóm) — đảm bảo tốc độ đủ nhanh để không làm gián đoạn phần trình bày.
4. Thử tắt mạng hoàn toàn trên máy demo và chạy lại toàn bộ luồng một lượt để chắc chắn không còn phụ thuộc ngầm nào vào kết nối internet (kể cả các phần khác của hệ thống như cơ sở dữ liệu, không chỉ riêng lớp LLM).

---

## 7. Timeline đề xuất bổ sung vào kế hoạch 48 giờ

Việc chuẩn bị phương án offline nên xếp vào giai đoạn dự phòng, sau khi phần chính đã ổn định, không nên làm sớm hơn vì không ảnh hưởng trực tiếp đến điểm số kỹ thuật cốt lõi:

| Giờ | Việc |
|---|---|
| 26–28 | Cài Ollama, tải thử model Qwen3 8B, viết client thay thế theo đúng giao diện đã có |
| 28–30 | Chạy thử bộ prompt đã tối ưu trên model local, đối chiếu chất lượng với bản chạy trên Claude |
| 30–32 | Tinh chỉnh prompt riêng cho nhánh offline theo Mục 3 nếu cần, đo thời gian phản hồi trên máy demo thật |
| Trước giờ demo | Thử tắt mạng, chạy lại toàn bộ luồng một lượt để xác nhận hệ thống hoạt động ổn định khi offline |

Nếu đến giờ 26 mà phần chính (Ưu tiên 1 và 2 trong plan tổng thể) chưa ổn định, nên **bỏ qua toàn bộ mục offline này** và dồn thời gian còn lại cho phần lõi — offline hoá chỉ là phương án dự phòng, không phải yêu cầu bắt buộc của đề bài.

---

## 8. Tổng hợp kỹ thuật theo mức độ ưu tiên

| Kỹ thuật | Mức ưu tiên | Lý do |
|---|---|---|
| Chọn Qwen3 8B qua Ollama | Cao | Cân bằng tốt nhất chất lượng tiếng Việt và khả năng chạy trên laptop phổ thông |
| Tạo client thay thế theo đúng giao diện đã có | Cao | Không phá vỡ kiến trúc hiện tại, dễ chuyển đổi qua lại |
| Tách prompt phức tạp thành 2 lượt gọi | Trung bình | Cần thiết nếu model local gặp khó khăn tuân thủ nhiều ràng buộc đồng thời |
| Thêm bước validate ở tầng code sau khi model trả lời | Cao | Lớp bảo vệ bổ sung cần thiết khi hạ cấp từ Claude xuống model nhỏ |
| Đơn giản hoá structured output | Trung bình | Chỉ cần nếu model local gặp lỗi parse với JSON lồng nhau phức tạp |
| Giảm nhiệt độ sinh thêm | Cao | Chỉnh 1 tham số, hiệu quả ổn định cao, không tốn thời gian |
| Kiểm thử tắt mạng hoàn toàn trước demo | Cao | Bước xác nhận cuối cùng bắt buộc, tránh rủi ro không lường trước |

---

## 9. Lưu ý khi trình bày với giám khảo

Nếu quyết định triển khai phương án offline, nên trình bày rõ đây là **lớp dự phòng cho tình huống mất mạng khi demo**, không phải kiến trúc chính của sản phẩm — tránh gây hiểu lầm rằng sản phẩm hoạt động kém ổn định hoặc chất lượng AI chính bị hạ thấp. Có thể nhấn mạnh thêm: phần lõi AI quan trọng nhất của hệ thống (BKT Engine, đồ thị tri thức, đánh giá phong cách học tập) vốn đã hoạt động hoàn toàn offline ngay từ thiết kế ban đầu, không phụ thuộc vào quyết định có dùng thêm model local cho tầng diễn giải hay không.
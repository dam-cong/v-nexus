# V-Nexus Tutor

> Mô tả dự án và phạm vi MVP 48 giờ

| Thuộc tính | Giá trị |
| --- | --- |
| Môn học chính | Tiếng Anh |
| Đối tượng chính | Học sinh tiểu học, chủ yếu lớp 3–4 |
| Phạm vi | Prototype/MVP phục vụ trình diễn trong 48 giờ |
| Chương trình tham chiếu | GDPT 2018 và cấu trúc SGK Global Success |
| Nguyên tắc | **AI đề xuất – giáo viên quyết định** |

## 1. Tổng quan

V-Nexus Tutor là nền tảng học Tiếng Anh thích ứng dành cho trường tiểu học. Sản phẩm
bắt đầu với học sinh lớp 3–4 và tập trung vào ba nhóm kỹ năng: **từ vựng, mẫu câu và
đọc/phát âm ở mức cơ bản**.

Hệ thống hướng tới một vòng lặp học tập khép kín:

1. Chẩn đoán kỹ năng đang gặp khó khăn.
2. Truy ngược kỹ năng tiên quyết để tìm nguyên nhân gốc có bằng chứng.
3. Tạo lộ trình học cá nhân từ kỹ năng nền đến kỹ năng mục tiêu.
4. Cho học sinh luyện tập và nhận phản hồi phù hợp lứa tuổi.
5. Cập nhật tiến bộ và đề xuất hành động cho giáo viên.

Các hoạt động học cốt lõi có thể chạy khi mạng yếu hoặc mất mạng sau khi nội dung đã
được tải trước. Dữ liệu được lưu cục bộ và đồng bộ khi có kết nối.

> **Quy ước thuật ngữ**
>
> - **Kỹ năng mục tiêu (target skill):** kỹ năng biểu hiện lỗi trong bài học hiện tại.
> - **Kỹ năng nguyên nhân gốc (root-cause skill):** kỹ năng tiên quyết sâu nhất được xác
>   nhận là chưa vững và có đủ bằng chứng.
> - **Mastery:** điểm thành thạo ước tính của một kỹ năng; không phải nhãn năng lực cố
>   định của học sinh.

## 2. Người dùng và phân quyền

| Vai trò | Nhu cầu và chức năng chính | Phạm vi dữ liệu |
| --- | --- | --- |
| **Học sinh lớp 3–4** | Làm bài chẩn đoán, học theo lộ trình, luyện đọc/phát âm, nhận coin/huy hiệu và xem tiến bộ | Chỉ xem dữ liệu của chính mình |
| **Giáo viên** | Xem heatmap lớp, nhóm gợi ý, danh sách ưu tiên; giao bài; sửa và duyệt nhận xét AI | Chỉ xem các lớp được phân công |
| **Ban giám hiệu (BGH)** | Xem tổng quan theo khối/lớp, cảnh báo và bảng vinh danh | Mặc định chỉ xem dữ liệu tổng hợp; không xem hồ sơ cá nhân nếu chưa được cấp quyền phù hợp |
| **Quản trị viên** | Tạo lớp, cấp tài khoản và quản lý cấu hình demo | Không mặc định được xem hồ sơ học tập cá nhân |

## 3. Phạm vi MVP 48 giờ

### 3.1. Thứ tự ưu tiên

| Mức | Hạng mục | Tiêu chí trình diễn |
| --- | --- | --- |
| **P0** | Đồ thị khoảng 70 kỹ năng từ dữ liệu seed; ngân hàng câu hỏi do LLM hỗ trợ sinh và BA/chuyên gia duyệt ngoài ứng dụng | Có đường tiên quyết đủ cho kịch bản demo; không xây workflow kiểm duyệt trong ứng dụng |
| **P0** | Đánh giá đầu vào thích ứng, tối đa 20 câu/phiên; truy gốc và bản đồ lỗ hổng | Phân biệt kỹ năng mục tiêu/nguyên nhân gốc; trả “cần kiểm tra thêm” khi thiếu bằng chứng |
| **P0** | Lộ trình cá nhân và luyện tập offline: từ vựng, mẫu câu, quiz; audio được sinh sẵn | Bật chế độ máy bay vẫn học và nhận phản hồi; kết nối lại không mất hoặc trùng dữ liệu |
| **P0** | Phản hồi luyện đọc/phát âm: thu âm, STT, so khớp từng từ, điểm phần trăm và nghe mẫu | Chỉ chạy online; công bố rõ đây là phản hồi mức demo, không phải chấm ngữ âm chuyên sâu |
| **P0** | Coin, XP và huy hiệu | Cộng thưởng đúng luật; không dùng để biểu thị năng lực học tập |
| **P0** | Dashboard giáo viên: heatmap, nhóm gợi ý, ưu tiên hỗ trợ và nhận xét AI | Mọi đề xuất có lý do; giáo viên sửa/duyệt trước khi gửi |
| **P0** | Phân quyền học sinh/giáo viên | Học sinh không xem dữ liệu của bạn; giáo viên không xem lớp ngoài phân công |
| **P1** | Xếp hạng XP và dashboard nhà trường một màn hình | Chỉ thực hiện sau khi P0 ổn định; dữ liệu cá nhân được bảo vệ |
| **P1** | Hồ sơ tiến bộ học sinh; giáo viên chỉnh nhóm và phản hồi kết luận | So sánh được mốc đầu vào với hiện tại |
| **P1** | Hội thoại đóng vai với AI theo tình huống bài học | Chỉ hiển thị khi online và có kiểm soát an toàn cho trẻ em |
| **P2** | Gian hàng đổi quà, import CSV và ghi nhận can thiệp trước/sau | Chỉ trình bày bằng mock/roadmap, không cam kết logic hoàn chỉnh |

### 3.2. Nguyên tắc cắt phạm vi

- Ưu tiên xây thật các hạng mục được dùng trực tiếp trong kịch bản chấm: chẩn đoán,
  dashboard giáo viên, offline và phản hồi luyện đọc/phát âm.
- Các hạng mục P1 chỉ bắt đầu khi luồng P0 đã chạy xuyên suốt.
- Các hạng mục P2 chỉ xuất hiện trong mock hoặc roadmap; không mô tả như tính năng đã
  hoàn thành.

## 4. Bản đồ AI toàn hệ thống

Hệ thống sử dụng ba nhóm kỹ thuật:

1. **AI trước runtime:** LLM hỗ trợ sinh nội dung; con người duyệt rồi đóng gói để dùng
   offline.
2. **AI tại runtime:** chỉ dùng ở các điểm cần cá nhân hóa tức thì và có fallback rõ
   ràng.
3. **Thuật toán nghiệp vụ:** dùng cho phần lõi cần minh bạch, giải thích được và có thể
   chạy offline, như truy đồ thị, tính mastery, sắp lộ trình, gom nhóm và xếp ưu tiên.

| Luồng | Thời điểm | AI/thuật toán thực hiện | Khi lỗi hoặc offline |
| --- | --- | --- | --- |
| Ngân hàng câu hỏi, nội dung và audio | Trước runtime | LLM sinh bản nháp câu hỏi, distractor và phản hồi; TTS sinh audio; người có chuyên môn duyệt | Nội dung đã duyệt được đóng gói, không phụ thuộc AI tại runtime |
| Chẩn đoán và truy gốc | Runtime | Thuật toán chọn câu và duyệt đồ thị; LLM chỉ diễn giải kết quả | Dùng mẫu câu có sẵn để diễn giải |
| Lộ trình và luyện tập | Runtime | Thuật toán sắp thứ tự tiên quyết; phản hồi lấy từ mapping distractor đã duyệt | Chạy offline sau khi tải gói nội dung |
| Luyện đọc/phát âm | Runtime | STT chuyển giọng nói thành văn bản; thuật toán căn chỉnh từ | Ẩn hoặc vô hiệu hóa tính năng; nhắc luyện lại khi có mạng |
| Động lực học | Trước runtime | Luật coin/XP; LLM chỉ hỗ trợ sinh tên huy hiệu và lời động viên | Luật thưởng chạy offline |
| Dashboard giáo viên | Runtime | Thuật toán gom nhóm/xếp ưu tiên; LLM hỗ trợ nhận xét và hoạt động phụ đạo | Dùng khung nhận xét có sẵn; nhóm/ưu tiên vẫn hoạt động |
| Dashboard nhà trường | Runtime | Thuật toán tổng hợp số liệu; LLM hỗ trợ viết tóm tắt tuần | Chỉ hiển thị số liệu |
| Dashboard học sinh | Trước runtime | Thuật toán tổng hợp tiến bộ; lời diễn giải lấy từ kho câu đã duyệt | Chạy offline với dữ liệu cục bộ |
| Hội thoại đóng vai (P1) | Runtime | LLM đóng vai trong phạm vi từ vựng và mẫu câu cho phép | Không hiển thị khi offline |

### 4.1. Công nghệ dự kiến

- **LLM:** gọi qua backend; không để khóa API hoặc gọi trực tiếp từ client.
- **STT:** ưu tiên Web Speech API khi trình duyệt hỗ trợ; có thể dùng dịch vụ nhận dạng
  giọng nói phía backend nếu thử nghiệm với giọng trẻ em không đạt yêu cầu.
- **TTS:** sinh sẵn audio Tiếng Anh trong bước chuẩn bị nội dung.
- **Offline:** PWA + IndexedDB; đồng bộ phải idempotent để retry không tạo bản ghi trùng.

Tên nhà cung cấp chỉ là lựa chọn triển khai dự kiến, không phải ràng buộc nghiệp vụ.

## 5. Các luồng chức năng chính

### 5.1. Chẩn đoán và truy gốc

Học sinh làm một phiên đánh giá thích ứng, tối đa 20 câu. Luồng xử lý:

1. Xác định kỹ năng mục tiêu từ câu trả lời sai.
2. Duyệt các kỹ năng tiên quyết trên đồ thị và chọn câu thăm dò phù hợp.
3. Thu thập bằng chứng cho từng nhánh; quy tắc `2/3 câu đúng` chỉ là ngưỡng tạm thời
   trong demo.
4. Chọn kỹ năng tiên quyết sâu nhất có đủ bằng chứng là chưa vững làm nguyên nhân gốc.
5. Nếu bằng chứng mâu thuẫn hoặc chưa đủ, trả trạng thái **“cần kiểm tra thêm”**.

Kết quả gồm kỹ năng mục tiêu, kỹ năng nguyên nhân gốc, bản đồ đỏ/vàng/xanh và các câu
trả lời làm bằng chứng.

**Vai trò của AI:** thuật toán tự thiết kế chọn câu và truy đồ thị; không gọi LLM trong
quá trình chọn câu. Khi kết thúc phiên, LLM có thể tạo hai phần diễn giải:

- Bản thân thiện, khích lệ dành cho học sinh.
- Bản chuyên môn, nêu rõ bằng chứng dành cho giáo viên.

Khi LLM lỗi, hệ thống ghép mẫu câu có sẵn với tên kỹ năng và kết quả chẩn đoán.

### 5.2. Lộ trình và luyện tập offline

Lộ trình bắt đầu từ lỗ hổng nền sâu nhất, đi dần đến kỹ năng mục tiêu và bỏ qua kỹ năng
đã vững. Sau mỗi bước có bài kiểm tra lại; khi kỹ năng nền đạt yêu cầu, học sinh quay về
kỹ năng mục tiêu.

Gói offline gồm nội dung, hình ảnh, audio, câu hỏi và phản hồi đã duyệt. Bài làm được lưu
cục bộ, sau đó đồng bộ khi có mạng. Giao diện dành cho trẻ 8–9 tuổi sử dụng hình ảnh lớn,
ít chữ và audio ở các hướng dẫn quan trọng.

**Vai trò của AI:** LLM hỗ trợ sinh trước nội dung giải thích, ví dụ, bài luyện tập và
phản hồi theo dạng lỗi. Mỗi distractor được mapping với một dạng lỗi và một câu phản hồi
phù hợp lứa tuổi. Tại runtime, thuật toán sắp lộ trình và lấy phản hồi đã duyệt; không cần
gọi LLM.

### 5.3. Phản hồi luyện đọc/phát âm online

Học sinh nghe câu mẫu, thu âm, nhận transcript từ STT, xem các từ đọc thiếu hoặc không
khớp, nghe lại mẫu và thử lại. Khi đạt ngưỡng demo, hệ thống có thể cộng coin.

> **Giới hạn cần công bố:** STT kết hợp so khớp từ chủ yếu đo mức độ đọc đúng/đủ và khả
> năng được hệ thống nhận diện. Cách này không đánh giá chính xác trọng âm, âm vị hay
> ngữ điệu như một hệ thống chấm phát âm chuyên sâu.

- Thuật toán căn chỉnh transcript với câu gốc và chỉ đánh dấu từ sai rõ ràng hoặc bị bỏ
  sót.
- Kết quả không được dùng làm kết luận duy nhất về năng lực nói của học sinh.
- Audio của trẻ không được lưu lâu dài mặc định; mọi việc lưu hoặc gửi tới dịch vụ bên
  thứ ba phải theo chính sách của nhà trường và có cơ sở đồng ý phù hợp.
- Khi offline, tính năng bị vô hiệu hóa và hệ thống nhắc học sinh luyện lại khi có mạng.

### 5.4. Động lực học

- **Coin:** nhận khi hoàn thành nhiệm vụ hoặc đạt điều kiện luyện tập.
- **XP:** phản ánh mức độ tham gia/nỗ lực, dùng để mở huy hiệu.
- **Huy hiệu:** trao theo mốc XP hoặc chuỗi hoạt động tích cực.
- **Xếp hạng:** chỉ dựa trên XP, không dựa trên mastery hoặc lỗ hổng.

Nếu triển khai bảng vinh danh, nhà trường phải có tùy chọn bật/tắt, sử dụng tên hiển thị
phù hợp và không công khai dữ liệu học tập nhạy cảm. Gian hàng đổi coin thuộc P2.

**Vai trò của AI:** luật thưởng là thuật toán và chạy offline. LLM chỉ hỗ trợ sinh trước
tên huy hiệu, mô tả và kho lời động viên; không được tự quyết định phần thưởng tại
runtime.

### 5.5. Dashboard giáo viên

Dashboard cung cấp:

- Heatmap lớp × kỹ năng, có drill-down tới bằng chứng của học sinh thuộc lớp được giao.
- Ba loại nhóm gợi ý: **học lại nền**, **luyện thêm** và **nâng cao**.
- Danh sách ưu tiên hỗ trợ kèm lý do.
- Cảnh báo kỹ năng có tỷ lệ chưa đạt cao để cân nhắc dạy lại cả lớp.
- Nhận xét cá nhân và hoạt động phụ đạo do AI đề xuất.

Thuật toán gom nhóm theo nguyên nhân gốc và xếp ưu tiên theo tác động. LLM có thể tạo
nhận xét 3–4 câu theo cấu trúc: ghi nhận tiến bộ → nêu điểm cần cải thiện tích cực → đề
xuất việc phụ huynh có thể làm cùng con. Giáo viên phải sửa/duyệt trước khi gửi; hệ thống
lưu rõ trạng thái **“AI đề xuất”** và **“giáo viên đã duyệt”**.

### 5.6. Dashboard nhà trường

Dashboard một màn hình gồm tổng quan theo khối/lớp, xu hướng tiến bộ, bảng vinh danh XP
và cảnh báo lớp cần hỗ trợ. LLM có thể viết một đoạn tóm tắt tuần từ số liệu đã tổng
hợp; khi LLM lỗi, dashboard chỉ hiển thị số liệu.

BGH mặc định xem dữ liệu tổng hợp. Việc truy cập hồ sơ cá nhân phải dựa trên vai trò,
mục đích hợp lệ và dấu vết kiểm tra; không mở drill-down toàn trường theo mặc định.

### 5.7. Dashboard và hồ sơ học sinh

Trang **“Hành trình của em”** trả lời ba câu hỏi:

1. **Em bắt đầu từ đâu?** Kết quả đánh giá đầu vào làm mốc xuất phát.
2. **Em đang ở đâu?** Bản đồ kỹ năng, coin, XP, huy hiệu và nhiệm vụ tiếp theo.
3. **Em đã tiến bộ thế nào?** So sánh mốc xuất phát với hiện tại và làm nổi bật kỹ năng
   vừa tiến bộ.

Dashboard của trẻ chỉ nói về chính em, không hiển thị lỗ hổng hoặc mastery của bạn khác.
Xếp hạng XP nằm ở màn hình riêng và chỉ phản ánh nỗ lực. Hồ sơ chi tiết chỉ dành cho học
sinh và giáo viên phụ trách; BGH xem dữ liệu tổng hợp theo chính sách phân quyền.

### 5.8. Hội thoại đóng vai với AI (P1)

Học sinh trò chuyện với nhân vật AI trong một tình huống quen thuộc, chẳng hạn làm quen
bạn mới hoặc hỏi đáp về đồ chơi. Đây là tính năng online, chỉ triển khai khi P0 ổn định.

LLM phải được giới hạn bởi:

- Từ vựng và mẫu câu thuộc phạm vi kỹ năng đã học hoặc đang học.
- Câu trả lời ngắn, thân thiện và phù hợp lứa tuổi.
- Không yêu cầu trẻ cung cấp thông tin cá nhân.
- Bộ lọc chủ đề, giới hạn lượt hội thoại và cơ chế kết thúc an toàn.
- Nhật ký kỹ thuật tối thiểu phục vụ kiểm tra, tuân theo chính sách lưu trữ dữ liệu.

System prompt là một lớp bảo vệ nhưng không thay thế kiểm thử an toàn và kiểm soát phía
ứng dụng.

## 6. Kịch bản demo 5 phút

1. **Chẩn đoán:** Bé An, học sinh lớp 4, làm đánh giá đầu vào và sai bài tả ngoại hình.
   Hệ thống truy ngược, xác định em cần củng cố từ vựng về bộ phận cơ thể và màu sắc;
   một mẫu câu liên quan đã được xác nhận là vững.
2. **Cá nhân hóa và offline:** Lộ trình cá nhân xuất hiện. Người trình diễn bật chế độ
   máy bay; học sinh vẫn luyện từ vựng và nhận phản hồi đã đóng gói.
3. **Luyện đọc/phát âm:** Kết nối được bật lại. Học sinh đọc câu mẫu, xem từ chưa khớp,
   thử lại và nhận coin khi đạt ngưỡng demo.
4. **Giáo viên:** Dashboard hiển thị heatmap, ba nhóm gợi ý và hoạt động phụ đạo. Giáo
   viên yêu cầu AI sinh nhận xét, sửa một câu rồi duyệt.
5. **Nhà trường (nếu P1 hoàn thành):** Dashboard hiển thị tổng quan khối, tóm tắt tuần
   và bảng vinh danh XP. Nếu chưa hoàn thành, bỏ bước này khỏi luồng demo chính.
6. **Roadmap:** Trình bày mock gian hàng đổi quà và kế hoạch mở rộng khối lớp/môn học;
   không mô tả các phần này như tính năng đã hoàn thành.

## 7. Tiêu chí nghiệm thu MVP

| Hạng mục | Điều kiện chấp nhận tối thiểu |
| --- | --- |
| Chẩn đoán | Phân biệt target/root cause; hiển thị bằng chứng; không kết luận chắc chắn khi thiếu dữ liệu |
| Lộ trình | Tuân theo quan hệ tiên quyết và bỏ qua kỹ năng đã vững |
| Offline | Học được với gói đã tải; mất mạng không mất bài; retry đồng bộ không tạo dữ liệu trùng |
| Luyện đọc/phát âm | Hoạt động online trên thiết bị demo; hiển thị đúng giới hạn của phép đo |
| Dashboard giáo viên | Nhóm và ưu tiên có lý do; nhận xét AI phải qua giáo viên duyệt |
| Phân quyền | Học sinh, giáo viên, BGH và quản trị viên không xem dữ liệu ngoài phạm vi |
| Nội dung | Câu hỏi, phản hồi, audio và mapping kỹ năng dùng trong demo đã được người có chuyên môn duyệt |

## 8. Nguyên tắc AI và dữ liệu

- AI đề xuất, giáo viên quyết định.
- Mọi kết luận chẩn đoán phải gắn với bằng chứng; thiếu bằng chứng thì trả **“cần kiểm
  tra thêm”**.
- Không gắn nhãn học sinh là “yếu/kém”; mastery là trạng thái có thể thay đổi theo bằng
  chứng mới.
- Không công khai mastery, lỗ hổng hoặc hồ sơ học tập. Bảng vinh danh chỉ phản ánh XP
  và phải tuân theo cấu hình riêng tư của nhà trường.
- Nội dung do LLM hỗ trợ sinh phải được duyệt trước khi đưa tới học sinh. Nhận xét gửi
  phụ huynh phải qua giáo viên duyệt.
- Không sao chép nguyên văn nội dung SGK. Chỉ tham chiếu cấu trúc chương trình; câu hỏi,
  phản hồi và hình ảnh phải là nội dung gốc hoặc có quyền sử dụng.
- Dữ liệu demo là dữ liệu mẫu tự tạo. Không tuyên bố hiệu quả thực nghiệm khi chưa có
  pilot và phương pháp đo phù hợp.
- Thu thập, lưu trữ và truyền dữ liệu của trẻ em phải theo chính sách nhà trường, nguyên
  tắc tối thiểu hóa dữ liệu và thời hạn lưu trữ rõ ràng.

## 9. Giả định và rủi ro cần xác nhận

| Nội dung | Trạng thái cần chốt |
| --- | --- |
| Đồ thị khoảng 70 kỹ năng | Chuyên gia Tiếng Anh tiểu học phải xác nhận mapping với GDPT 2018 và tài liệu tham chiếu trước khi dùng để chẩn đoán |
| Công thức mastery `0.5/0.3/0.2` và ngưỡng `0.4/0.75` | Phải định nghĩa rõ ba thành phần trong đặc tả kỹ thuật; hiện chỉ là heuristic cho demo, chưa phải thang đo đã kiểm chứng |
| Quy tắc `2/3 câu đúng` | Là cấu hình tạm thời; cần pilot để đánh giá độ tin cậy và nguy cơ kết luận từ quá ít bằng chứng |
| Nhận dạng giọng trẻ em | Phải thử trên trình duyệt, thiết bị và môi trường ồn thực tế; chuẩn bị kịch bản demo dự phòng |
| Phạm vi 48 giờ | Chỉ khả thi khi dữ liệu seed, câu hỏi, audio, tài khoản và thiết bị demo được chuẩn bị trước |
| Xếp hạng XP | Cần chính sách bật/tắt, tên hiển thị và cơ chế tránh tạo áp lực hoặc so sánh gây hại |

## 10. Ngoài phạm vi MVP

- Dashboard phụ huynh hoàn chỉnh.
- Các khối lớp ngoài lớp 3–4 và các môn học khác.
- Placement test đầy đủ bốn kỹ năng.
- Workflow kiểm duyệt nội dung trong ứng dụng.
- Đánh giá phát âm/nói chuyên sâu ở mức âm vị, trọng âm và ngữ điệu.
- Logic hoàn chỉnh cho gian hàng đổi quà.

Các hạng mục này chỉ được trình bày trong roadmap khi pitch.

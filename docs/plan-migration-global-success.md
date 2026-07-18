# Kế hoạch: Chuyển BKT sang giáo trình Global Success + thêm hồ sơ học sinh (profile survey)

> Tài liệu này là **kế hoạch triển khai kỹ thuật** cho dev thực hiện. Chưa có code nào được
> thay đổi tại thời điểm viết tài liệu này (2026-07-18). Người viết plan không tự triển khai.

## Bối cảnh

Team đã đối chiếu 3 nguồn dữ liệu:

- `docs/2026 syllabus - Academy Star (revised).xlsx` → sinh ra `docs/data/knowledge-graph.json`
  (156 node auto-dump, **chưa từng dùng thật**) và là cơ sở đặt tên cho `domain/knowledge_graph.py`
  (25 skill_id chọn lọc, dùng thật bởi `domain/bkt.py`) và `docs/data/question-bank.json` (42 câu).
- `docs/V-Nexus_Content_Workbook_1.xlsx` — nội dung content team đang viết theo **SGK Global
  Success lớp 3–4** (giáo trình công lập thật), có sheet `NODE_INPUT` (70 node kỹ năng) và
  `QUESTION_BANK` (193 câu đã duyệt, phủ 16/70 node).
- `docs/PROFILE_SURVEY.xlsx` — khảo sát hồ sơ học sinh (sở thích/cách học/thói quen/cảm xúc),
  hoàn toàn độc lập với skill graph, chưa có chỗ chứa trong data model hiện tại.

**Quyết định của team (2026-07-18):**
1. Chuyển nền tảng BKT từ Academy Stars sang Global Success (khớp SGK thật, khớp nội dung content
   team đang viết).
2. Dữ liệu profile survey dùng đúng nguyên tắc ghi trong chính file khảo sát: chỉ mô tả lựa chọn
   + đề xuất hành động sư phạm, **không gắn nhãn tính cách** (không thêm trường hướng nội/hướng
   ngoại dù có yêu cầu).

Hai giáo trình Academy Stars và Global Success **không map 1-1 được** — thứ tự và chủ đề Unit
khác nhau hoàn toàn (VD Unit 4 Academy Stars = "Safari Adventure", Unit 4 Global Success =
"Our bodies"). Đây là thay thế nền tảng, không phải một phép chuyển đổi dữ liệu.

## Phát hiện quan trọng cho dev

`domain/knowledge_graph.py` là module Python **viết tay**, độc lập với file
`docs/data/knowledge-graph.json` (file đó chỉ là dump thô, tự ghi chú "chưa qua kiểm duyệt giáo
viên", không được `bkt.py` đọc). `domain/bkt.py` hoàn toàn **generic theo skill_id** — không
hardcode bất kỳ skill_id nào. Vì vậy việc chuyển giáo trình chỉ cần sửa:
1. `domain/knowledge_graph.py` (bảng `SKILLS` + `PREREQUISITES`)
2. `docs/data/question-bank.json`
3. (tuỳ chọn) `docs/data/survey-results.json`, `docs/data/placement-test.json` nếu muốn dữ liệu
   demo tham chiếu skill_id mới cho nhất quán

không cần sửa `domain/bkt.py`.

## Phạm vi cho hackathon (còn ~1 ngày, kết thúc 2026-07-19)

Chỉ 16/70 node Global Success đã có câu hỏi soạn sẵn (193 câu, "Đã duyệt" toàn bộ), thuộc 8 unit:

| node_id VOC | node_id PAT | Chủ đề |
|---|---|---|
| G3U04-VOC | G3U04-PAT | Our bodies (bộ phận cơ thể) |
| G3U09-VOC | G3U09-PAT | Colours (màu sắc) |
| G3U11-VOC | G3U11-PAT | My family (gia đình) |
| G3U14-VOC | G3U14-PAT | My bedroom (phòng ngủ, vị trí in/on/under/behind) |
| G4U01-VOC | G4U01-PAT | My friends (quốc tịch, Where are you from?) |
| G4U02-VOC | G4U02-PAT | Time and daily routines (giờ giấc) |
| G4U03-VOC | G4U03-PAT | My week (ngày trong tuần, thói quen) |
| G4U05-VOC | G4U05-PAT | Things we can do (Can you...?) |

**Đề xuất: chỉ migrate 16 node này cho demo**, quy mô tương đương hiện trạng (25 skill/42 câu) nên
rủi ro thời gian chấp nhận được. 54 node còn lại (gồm cả 6 node PHO phonics và 4 node DLG hội
thoại) để lại roadmap sau hackathon, khi content team soạn xong câu hỏi cho các node đó.

## Việc cần làm

### 1. `domain/knowledge_graph.py` — thay skill graph

- Thay `SKILLS` bằng 16 entry, dùng thẳng `node_id` của workbook làm `skill_id` (VD
  `"G3U04-VOC"`, `"G3U04-PAT"`) — tránh bịa namespace mới rồi lệch với dữ liệu gốc trong
  `NODE_INPUT`/`QUESTION_BANK`. Lấy `ten_ky_nang` (cột 3 trong NODE_INPUT) làm `name`, grade suy
  từ tiền tố `G3`/`G4`.
- Thay `PREREQUISITES`:
  - Trong cùng unit: `PAT` phụ thuộc `VOC` (phải có từ vựng trước khi dùng mẫu câu).
  - Giữa các unit: theo đúng thứ tự dạy trong `NODE_INPUT` (G3U04 → G3U09 → G3U11 → G3U14 →
    G4U01 → G4U02 → G4U03 → G4U05) — chuỗi tuyến tính đơn giản hoá, cùng kiểu giả định MVP mà
    chính `knowledge-graph.json` cũ đã ghi chú là chấp nhận được khi chưa có chuyên gia rà soát
    quan hệ tiên quyết thật.
- Giữ nguyên toàn bộ API hiện có (`get_skill_name`, `get_prerequisites`, `has_skill`,
  `trace_root_causes`) — không đổi chữ ký hàm, chỉ đổi dữ liệu trong `SKILLS`/`PREREQUISITES`.

### 2. Script import `QUESTION_BANK` sheet → `docs/data/question-bank.json`

Đọc 193 dòng đã "Đã duyệt" trong sheet `QUESTION_BANK` của
`docs/V-Nexus_Content_Workbook_1.xlsx`, map cột sang schema hiện có:

| Cột sheet | Field JSON | Ghi chú |
|---|---|---|
| `node_id` | `skill_id` | dùng thẳng, khớp `knowledge_graph.py` mới |
| `loai` (CHAN_DOAN/LUYEN_TAP) | `purpose` | `CHAN_DOAN` → `"diagnostic"`, `LUYEN_TAP` → `"practice"` (giá trị mới, hiện schema mới chỉ có `"diagnostic"`) |
| `do_kho` (1/2/3) | `difficulty` | 1→`"easy"`, 2→`"medium"`, 3→`"hard"` |
| `cau_hoi_audio_script` | `prompt.audio_transcript` (và `prompt.text` nếu cần hiển thị chữ) | mọi câu đều có audio — xem mục type bên dưới |
| `image_desc` | field ảnh mới, VD `prompt.image_desc` | hiện schema chưa có field này, cần bổ sung |
| `dap_an_A/B/C` | `options[].label` | `option_id` = `"a"/"b"/"c"` |
| `dap_an_dung` (A/B/C) | `correct_option_id` | lowercase |
| `loi_A/B/C` | `options[].error_tag` | `"-"` → `null` |
| `phan_hoi_A/B/C` | **field mới**: `options[].feedback_vi` | schema hiện tại chỉ có 1 `explanation` chung — không đủ chỗ chứa phản hồi riêng cho từng đáp án sai. Cần bổ sung field này vào schema câu hỏi. |
| `nguoi_duyet`, `trang_thai` | không cần đưa vào JSON runtime (chỉ dùng để lọc dòng đủ điều kiện import — chỉ lấy dòng `trang_thai == "Đã duyệt"`) | |

- `type`/`instruction_label`: mọi câu đều audio-first. Nếu có `image_desc` → dùng biến thể
  audio+icon-choice; nếu không → audio+text-choice (khớp 3 loại câu hỏi đã thấy ở mockup "Medi
  Bee" trong `docs/Screenshot (5/6/7).png`, xem `docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md`).
- 42 câu Academy Stars cũ trong `question-bank.json` hiện tại: **archive**, không xoá — đổi tên
  file thành `docs/data/question-bank.academy-stars.json` trước khi ghi đè, vì skill_id cũ sẽ
  không còn tồn tại trong `knowledge_graph.py` mới → giữ nguyên sẽ gây lỗi tra cứu skill khi
  chấm.

### 3. `docs/data/knowledge-graph.json`

Không dùng thật bởi code (xem "Phát hiện quan trọng" ở trên) — không cần sửa gấp. Có thể để lại
làm tài liệu tham khảo cũ, hoặc (không gấp) regenerate từ toàn bộ 70 node `NODE_INPUT` để làm tài
liệu roadmap cho các node chưa có câu hỏi.

### 4. `docs/data/survey-results.json` và `docs/data/placement-test.json`

Kiểm tra xem có tham chiếu skill_id `as3.*`/`as4.*` không (đã xác nhận `survey-results.json` có,
trong `answers[].skill_id` của dữ liệu mẫu 5 học sinh). Cập nhật mẫu dữ liệu demo sang 16 skill_id
mới để nhất quán với `knowledge_graph.py` mới, hoặc archive cùng lúc với
`question-bank.academy-stars.json` nếu không cần demo dữ liệu mẫu ngay.

### 5. Hồ sơ học sinh — `docs/data/student-profile.json` (file mới)

Parse `docs/PROFILE_SURVEY.xlsx` (12 câu S01–S12, 4 nhóm: `so_thich`, `cach_hoc`, `thoi_quen`,
`cam_xuc`) thành:
- Phần metadata tĩnh: định nghĩa 12 câu hỏi (mã, nhóm, kiểu chọn, lựa chọn, mô tả cách app dùng)
  — dùng để UI hiển thị khảo sát.
- Phần dữ liệu mẫu: câu trả lời cho 5 học sinh demo (khớp 5 học sinh đã có trong
  `survey-results.json`) để tầng cá nhân hoá có dữ liệu chạy thử.

**Ràng buộc bắt buộc** (ghi rõ trong chính file khảo sát, mục "NGUYÊN TẮC BẮT BUỘC"):
- Đây là hồ sơ tự khai, **không phải công cụ chẩn đoán tâm lý**.
- Không được sinh/hiển thị bất kỳ nhãn tính cách nào (file liệt kê thẳng ví dụ cấm: "hướng
  nội/hướng ngoại", "nhút nhát", "thiếu tự tin", "lười"). Chỉ được: mô tả điều học sinh đã chọn +
  nối với dữ liệu học tập + đề xuất hành động sư phạm cụ thể.
- Nhóm câu cảm xúc (S08–S10) luôn phải có lựa chọn "Em không muốn trả lời", bỏ qua không ảnh
  hưởng và không hỏi lại trong phiên.
- Dữ liệu chỉ hiển thị cho giáo viên/nhà trường, không lên bảng xếp hạng, không chia sẻ giữa học
  sinh.
- Đây là **trục dữ liệu tách biệt với BKT** — dùng cho tầng cá nhân hoá nội dung (chọn theme ví
  dụ, mascot, nhịp độ luyện tập, cách phản hồi khi sai...), không trộn vào công thức tính
  `mastery` trong `domain/bkt.py`.

## Kiểm tra sau khi triển khai

- Chạy lại `tests/test_knowledge_graph.py` và test BKT liên quan sau khi đổi `SKILLS`/
  `PREREQUISITES` — đảm bảo `trace_root_causes` vẫn hoạt động đúng logic với skill_id mới.
- Chạy thử 1 luồng chẩn đoán mẫu bằng 16 skill mới: học sinh yếu `G4U03-PAT` (thói quen, thì hiện
  tại đơn) nhưng gốc rễ nên truy ra `G3U04-VOC`/`G3U04-PAT` nếu nền tảng câu cơ bản chưa vững —
  xác nhận chuỗi tiên quyết trả về hợp lý.
- Xác nhận `question-bank.json` mới có đúng 193 câu (hoặc số dòng "Đã duyệt" thực tế tại thời
  điểm import), mỗi câu có `skill_id` tồn tại trong `knowledge_graph.py` mới (không có skill_id
  mồ côi).
- Xác nhận không có bất kỳ chuỗi "hướng nội", "hướng ngoại", "nhút nhát", "thiếu tự tin" nào xuất
  hiện trong code/copy sinh ra từ `student-profile.json`.

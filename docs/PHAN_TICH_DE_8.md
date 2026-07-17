# Phân tích Đề 8: Từ slide/giáo án thành video bài giảng

**Nhóm bài toán:** EdTech / Educators | **API chính:** TTS Batch (Vbee)

> Đề thuộc nhóm **Giáo dục & Đào tạo**, khác chủ đề đăng ký ban đầu (SME) → cần thay
> `domain/sme_innovation_adapter.py` bằng adapter mới (xem phần Giải pháp).

## Đề bài

Giáo viên upload slide (PPTX/PDF) hoặc giáo án (Word) → hệ thống tự sinh lời giảng,
lồng giọng đọc Vbee, render video bài giảng hoàn chỉnh kèm phụ đề — phục vụ lớp học đảo
ngược, LMS, ôn tập tại nhà.

## Ràng buộc bắt buộc

- TTS/STT tiếng Việt **phải dùng API Vbee** làm engine chính — bắt buộc, không thay thế.
  LLM/OCR/dịch máy/render video: tự do lựa chọn.
- Sản phẩm phải chạy thật (live deployed URL) — không mockup/video dựng sẵn.
- Checkpoint 1 (tên dự án + mô tả): 11:00 T7 18/7. Checkpoint 2 (URL+repo): 23:00 T7
  18/7. Final: 11:00 CN 19/7, **không gia hạn**.

## Yêu cầu chức năng chính

1. Nhận PPTX/PDF/Word → trích nội dung + speaker notes (nếu có).
2. LLM sinh lời giảng tự nhiên cho từng slide (có dẫn dắt/ví dụ/câu chuyển tiếp — không
   đọc nguyên văn bullet point).
3. UI duyệt & sửa kịch bản trước khi tạo audio; chỉnh tông giọng theo cấp học (tiểu
   học ↔ đại học).
4. TTS batch Vbee sinh audio (chọn giọng/tốc độ) → render video: slide + audio + phụ đề
   đồng bộ.
5. Phụ đề: lấy timestamp từ metadata TTS nếu có, hoặc chạy STT Vbee trên audio vừa sinh
   để lấy word-level timestamp.
6. Giáo án không kèm slide → tự sinh bộ slide đơn giản (tiêu đề + ý chính + ảnh minh
   họa) từ nội dung giáo án.
7. Xuất MP4 + phụ đề rời .srt + link chia sẻ; quản lý thư viện bài giảng đã tạo.

## Điểm khó / rủi ro kỹ thuật

- **Đồng bộ phụ đề** — rủi ro cao nhất. Ưu tiên lấy timestamp trực tiếp từ TTS Vbee, tránh
  chạy thêm STT làm phức tạp pipeline.
- **Render video** tốn thời gian (CPU-bound) — đo thời gian render thật sớm, tránh
  timeout khi demo live.
- **Sinh lời giảng tự nhiên**: cần prompt LLM tốt, tùy biến theo cấp học, tránh đọc lại
  y nguyên bullet point.
- **Trích xuất PPTX/PDF/Word**: layout đa dạng (bảng, hình, notes), không luôn có text
  thuần dễ parse.

## Giải pháp đề xuất

**Kiến trúc:** map vào khung V-Nexus sẵn có — chỉ thay Domain Adapter, không đổi
Gateway/Planner Agent/Tool Registry/MCP Server.

`domain/lecture_video_adapter.py` cấp cho Planner Agent:

- **Prompt hệ thống**: "trợ lý biên soạn bài giảng" — nhận file, sinh/sửa lời giảng theo
  yêu cầu giáo viên qua hội thoại.
- **Tool `extract_content`**: parse PPTX (python-pptx) / PDF (pypdf/OCR) / Word
  (python-docx) → text + speaker notes + ảnh.
- **Tool `generate_narration`**: LLM sinh lời giảng theo từng slide + tông giọng (tham
  số cấp học).
- **Tool `tts_vbee`**: gọi TTS Batch Vbee sinh audio theo giọng đã chọn (bắt buộc dùng
  API Vbee).
- **Tool `align_subtitle`**: lấy timestamp từ TTS metadata; fallback chạy STT Vbee trên
  audio đã sinh.
- **Tool `render_video`**: ghép slide (ảnh) + audio + phụ đề bằng ffmpeg/moviepy → MP4 +
  .srt.
- **Tool `auto_slide`**: sinh slide đơn giản từ giáo án Word không có slide sẵn (LLM tóm
  tắt ý chính + template ảnh).

**Luồng người dùng (happy path):** Upload file → trích nội dung → LLM sinh nháp lời
giảng từng slide → giáo viên xem/sửa trên UI (mở rộng frontend chat sẵn có, hiển thị
danh sách slide) → chọn giọng Vbee → sinh audio → ghép phụ đề + video → xuất MP4/srt +
lưu thư viện.

## MVP ưu tiên trong 48 giờ

**Phải có:** upload PPTX → trích text → LLM sinh lời giảng → duyệt/sửa cơ bản → TTS
Vbee → ghép video đơn giản (slide tĩnh + audio + phụ đề) → xuất MP4+srt, deploy live URL.

**Có thể bỏ nếu thiếu giờ:** tự sinh slide từ giáo án Word thuần; thư viện quản lý nhiều
bài giảng (demo 1 bài chạy mượt là đủ); tùy biến giọng theo nhiều cấp học (chọn cố định
1–2 tông trước).

## Business case (gợi ý cho tiêu chí Pilot)

Người trả tiền tiềm năng: nhà trường/trung tâm (gói theo giáo viên/tháng) hoặc giáo viên
cá nhân (freemium — giới hạn số phút video/tháng). Pilot đầu tiên: hợp tác 1 trường/LMS
để giáo viên thật dùng thử, đo thời gian tiết kiệm so với tự quay dựng video thủ công.

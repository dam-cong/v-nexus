# Self-check theo tiêu chí chấm điểm (100 điểm, 6 tiêu chí)

Dùng để tự soát trước khi nộp — không phải tiêu chí chính thức của ban giám khảo, chỉ là
checklist nội bộ đối chiếu theo thể lệ mục 2 (100 điểm).

## Chất lượng triển khai kỹ thuật — 20đ

- [ ] `docker compose up --build` chạy được từ đầu, không cần sửa tay
- [ ] Luồng chính (happy path) chạy ổn định, không lỗi khi demo
- [ ] Code không có phần dở dang / dead code hiển nhiên

## Kiến trúc AI-Native & Đổi mới sáng tạo — 20đ

- [ ] Sản phẩm AI-first ngay từ luồng chính, không phải AI gắn thêm vào flow CRUD thường
- [ ] `docs/AI_LOG.md` đầy đủ, phản ánh đúng quá trình cộng tác với AI
- [ ] Domain Adapter thể hiện rõ điểm sáng tạo của giải pháp (không chỉ là wrapper gọi LLM)

## Tính khả thi kinh doanh & Lộ trình Pilot — 20đ

- [ ] `docs/PROJECT_DESCRIPTION.md` mục Business case & Pilot đã điền cụ thể, có số liệu/giả định rõ ràng
- [ ] Xác định được ai trả tiền / ai tài trợ nếu triển khai thật

## UX AI-Native & Tư duy thiết kế — 15đ

- [ ] Chat UI đơn giản nhưng rõ ràng, không gây nhầm lẫn cho người dùng thử lần đầu
- [ ] Phản hồi AI có ngữ cảnh, không trả lời chung chung

## An toàn AI, Grounding & Độ tin cậy — 15đ

- [ ] Câu trả lời quan trọng được grounding qua tool/DB, không để LLM tự bịa
- [ ] Có xử lý khi tool lỗi hoặc dữ liệu thiếu (không crash, không im lặng trả lời sai)

## Trình bày & Bảo vệ giải pháp — 10đ

- [ ] Demo video ≤ 5 phút, đi thẳng vào happy path
- [ ] Slide thuyết trình có kiến trúc, vấn đề, giải pháp, business case rõ ràng
- [ ] Chuẩn bị trước câu hỏi Q&A dự kiến (2 phút) cho Vòng 3

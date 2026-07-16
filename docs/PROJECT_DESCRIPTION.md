# Project Description — V-Nexus

Bắt buộc nộp cùng bài (thể lệ 2.2). Điền đủ trước hạn chốt đội / nộp bài.

## 1. Tên dự án & chủ đề

- **Tên:** V-Nexus
- **Chủ đề (đề bài):** Đổi mới sáng tạo & Năng suất doanh nghiệp vừa và nhỏ (SME)
  — _cập nhật lại theo đề bài chính thức công bố 11:00, 17/7/2026_

## 2. Vấn đề

_Vấn đề thực tế nào đang giải quyết? Ai gặp vấn đề này? Vì sao AI-native là cách tiếp
cận đúng thay vì một tính năng AI gắn thêm?_

## 3. Người dùng mục tiêu

_Chân dung người dùng, quy mô, hành vi hiện tại._

## 4. Giải pháp

_Giải pháp làm gì, luồng sử dụng chính (happy path), điểm khác biệt AI-native._

## 5. Kiến trúc

```
Frontend (chat) → FastAPI Gateway → Planner Agent (LLM + Tool Registry)
                                          ├─ Tool: MCP Server mẫu
                                          └─ Tool: (đề bài thật sẽ thêm)
                        Gateway → PostgreSQL (log hội thoại, dữ liệu nghiệp vụ)
```

Domain Adapter (`domain/`) là lớp duy nhất chứa prompt + tool đặc thù đề bài — xem
[README](../README.md#kiến-trúc) để biết cách thay khi có đề bài thật.

## 6. Tính khả thi kinh doanh & Lộ trình Pilot

_Mô hình vận hành/kinh doanh nếu triển khai thật, ai trả tiền/tài trợ, bước pilot đầu
tiên sau cuộc thi._

## 7. An toàn AI, Grounding & Độ tin cậy

_Cách hạn chế ảo giác (grounding qua tool/DB thay vì để LLM tự bịa), giới hạn phạm vi
trả lời, xử lý khi tool lỗi hoặc dữ liệu thiếu._

## 8. Tech stack

- Backend: FastAPI (Gateway), Planner Agent gọi Anthropic Claude
- Tool integration: MCP (Model Context Protocol), Tool Registry nội bộ
- Database: PostgreSQL (SQLAlchemy async)
- Frontend: Streamlit (chat UI)
- Hạ tầng: Docker Compose

## 9. Team

| Tên | Vai trò | Phụ trách |
|---|---|---|
| | Dev | |
| | Design | |
| | Business | |
| | AI | |

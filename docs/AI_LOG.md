# Nhật ký cộng tác với AI

Bắt buộc nộp cùng bài (xem thể lệ 2.2 — mục "Bài nộp"). Ghi lại **mọi** phiên làm việc
có AI tham gia tạo/sửa code, không chỉ những phiên "quan trọng". Đây là bằng chứng chính
cho tiêu chí *Kiến trúc AI-Native & Đổi mới sáng tạo* và cam kết 100% AI-native.

## Cách ghi

Mỗi dòng = một phiên trao đổi có kết quả cụ thể (không ghi tin nhắn chit-chat qua lại).

| Thời gian | Người | Công cụ AI | Yêu cầu gửi AI (tóm tắt) | Kết quả / Quyết định | Review bởi |
|---|---|---|---|---|---|
| 2026-07-17 14:41 | _tên_ | Claude Code | Dựng khung kiến trúc V-Nexus (Gateway + Planner Agent + Tool Registry + MCP Server mẫu + Domain Adapter) | Tạo scaffold ban đầu, xem chi tiết commit `<hash>` | _tên_ |

## Quy tắc

- Mỗi thành viên tự thêm dòng khi dùng AI để tạo/sửa code — không dồn lại ghi cuối ngày.
- Cột "Quyết định" ghi rõ nếu bạn **sửa lại** hoặc **từ chối** đề xuất của AI và vì sao —
  đây là phần giám khảo quan tâm nhất, không phải việc AI viết được gì.
- Khi thay Domain Adapter theo đề bài thật (xem `domain/adapter.py`), ghi lại prompt đã
  dùng để sinh phiên bản mới.
- Trước khi nộp bài: đối chiếu log này với `git log` — mọi commit có thay đổi code nên có
  ít nhất một dòng tương ứng ở đây.

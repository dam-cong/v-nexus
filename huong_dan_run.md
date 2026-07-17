# HƯỚNG DẪN KHỞI CHẠY DỰ ÁN V-NEXUS

Dự án **V-Nexus** sử dụng kiến trúc container hóa thông qua Docker Compose bao gồm các dịch vụ:
1. **db**: PostgreSQL Database (cổng 5433 trên host).
2. **mcp_server**: Model Context Protocol server.
3. **gateway**: FastAPI Backend API (cổng 8000).
4. **frontend**: React + Vite UI (cổng 8501) thiết kế theo giao diện dashboard chuyên nghiệp **Akademi**.

---

## 1. Khởi chạy bằng Docker Compose (Khuyên dùng)

### Chạy hệ thống
Ở thư mục gốc của dự án, chạy lệnh sau để khởi động toàn bộ dịch vụ ngầm:
```bash
docker compose up -d
```

### Build lại hệ thống khi có thay đổi code
Nếu bạn cập nhật mã nguồn ở backend hoặc frontend và muốn cập nhật trong Docker:
```bash
docker compose up --build -d
```
*(Đã cấu hình tối ưu build cache `.dockerignore` giúp tải ngữ cảnh siêu nhanh chỉ trong vài giây).*

### Dừng hệ thống
```bash
docker compose down
```

### Kiểm tra Logs (Xem lỗi nếu có)
Xem log thời gian thực của toàn bộ hệ thống hoặc từng service riêng lẻ:
```bash
# Xem log toàn bộ hệ thống
docker compose logs -f

# Chỉ xem log của backend gateway
docker compose logs -f gateway

# Chỉ xem log của frontend
docker compose logs -f frontend
```

---

## 2. Các địa chỉ truy cập chính

* **Giao diện Dashboard Akademi (Frontend):**
  👉 [http://localhost:8501](http://localhost:8501)
  *(Có đầy đủ các tab: Dashboard Overview, Học sinh, Giáo viên, Bảng xếp hạng và Khảo sát đầu vào).*

* **Backend Swagger API Docs:**
  👉 [http://localhost:8000/docs](http://localhost:8000/docs)
  *(Cho phép xem trực quan và test trực tiếp các endpoint CRUD).*

---

## 3. Khởi chạy cục bộ (Phục vụ phát triển/Debug nhanh)

Nếu muốn chạy trực tiếp trên máy không qua Docker:

1. **Khởi chạy PostgreSQL Container làm database:**
   ```bash
   docker compose up -d db
   ```

2. **Chạy FastAPI Backend:**
   ```bash
   # Kích hoạt virtual environment
   source venv/bin/activate
   # Khởi chạy uvicorn
   DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus uvicorn gateway.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Chạy React + Vite Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

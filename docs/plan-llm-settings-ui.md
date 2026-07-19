# Plan: UI Cấu Hình LLM cho Admin

## Mục tiêu
Thêm modal popup cho admin để cấu hình LLM (API Key, Base URL, Model, Mode) trực tiếp từ giao diện, lưu vào database, áp dụng ngay lập tức.

## Thay đổi cần thiết

### 1. Database - Model mới (`db/models.py`)
Thêm `AppSetting` model — bảng key-value đơn giản:
```
id | key (unique) | value (text) | updated_at
```
- Mở rộng được cho cấu hình khác trong tương lai
- Tự động tạo bảng khi startup (via `create_all`)

### 2. Backend - Config linh hoạt (`gateway/app/config.py`)
- Chuyển `Settings` thành class có thể cập nhật runtime
- Thêm phương thức `load_from_db()` và `update_from_db()`
- Khi startup: load từ DB → override env defaults
- `llm_client.py` đọc từ `settings` object → thay đổi có hiệu lực ngay

### 3. Backend - API Routes mới (`gateway/app/routes/settings.py`)
| Method | Endpoint | Mô tả | Auth |
|--------|----------|-------|------|
| `GET` | `/api/settings/llm` | Lấy cấu hình LLM hiện tại | admin |
| `PUT` | `/api/settings/llm` | Cập nhật + lưu DB + apply ngay | admin |

### 4. Frontend - Modal Component (`frontend/src/v2/SettingsModal.jsx`)
Form fields:
- **LLM Mode**: Select (offline / fpt / ollama)
- **API Key**: Text input (password-type)
- **Base URL**: Text input
- **Model**: Text input

### 5. Frontend - Wire up trong `AppV2.jsx`
- Thêm `onClick` cho icon Settings ở line 1207 (chỉ admin thấy)
- Thêm state `showSettingsModal`
- Import + render `SettingsModal`

## Flow hoạt động
```
Admin bấm icon Settings
  → Modal hiện, gọi GET /api/settings/llm
  → Hiển thị form với giá trị hiện tại
  → Admin sửa (vd: đổi sang Gemini key)
  → Bấm Lưu → PUT /api/settings/llm
  → Backend lưu vào DB + cập nhật settings object
  → Lần gọi LLM tiếp theo dùng config mới
```

## Switch sang Gemini
- **Mode**: `fpt`
- **API Key**: Gemini key
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **Model**: `gemini-2.0-flash` hoặc `gemini-2.5-flash`

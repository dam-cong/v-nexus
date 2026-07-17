# V-Nexus Tutor — VAIC 2026

*"Mỗi học sinh một lộ trình, mỗi giáo viên một trợ lý" / "Close every learning gap, one
root cause at a time"* _(tagline đề xuất, có thể đổi)_

Đội thi Vietnam AI Innovation Challenge 2026 (48h hackathon, 17–19/7/2026, FPT Tower).
**Gia sư thích ứng thu hẹp khoảng cách năng lực trong lớp học** (Giáo dục phổ thông —
Adaptive Learning). Xem phân tích chi tiết ở
[docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md).

_(Đề 8 — Vbee lecture video — không còn theo đuổi, giữ lại ở
[docs/PHAN_TICH_DE_8.md](docs/PHAN_TICH_DE_8.md) làm tài liệu tham khảo.)_

## Kiến trúc

Nguyên tắc: khung này chạy được ngay bây giờ, và **khi có đề bài thật, chỉ cần thay
`domain/` — không đổi gì ở Gateway, Planner Agent, Tool Registry hay MCP Server**.

```
┌─────────────┐      ┌──────────────────┐      ┌────────────────────────────┐
│  Frontend   │─────▶│  FastAPI Gateway │─────▶│      Planner Agent         │
│ (Streamlit  │      │   (/chat, /health)│     │  (LLM + Tool Registry)      │
│  chat đơn   │◀─────│                  │◀─────│                             │
│  giản)      │      └──────────────────┘      │  ├─ Domain Adapter ◀── đề bài│
└─────────────┘               │                │  │   (system_prompt + tools)│
                               ▼                │  ├─ Tool: MCP Server mẫu    │
                        ┌─────────────┐         │  └─ Tool: echo (ví dụ)      │
                        │ PostgreSQL  │         └────────────────────────────┘
                        └─────────────┘
```

- **Chỉ 1 Planner Agent** — không tạo thêm agent khác.
- **Domain Adapter** (`domain/adapter.py`, `domain/sme_innovation_adapter.py`): nơi
  DUY NHẤT chứa prompt + tool đặc thù đề bài. Khi có đề bài thật: tạo file
  `domain/<ten_de_bai>_adapter.py` mới implement `DomainAdapter`, rồi trỏ
  `gateway/app/routes/chat.py` sang adapter đó.
- **Tool Registry** (`tools/registry.py`): đăng ký tool theo format Anthropic tool-use,
  Planner Agent không cần biết tool đến từ đâu (hàm Python thường hay MCP server).
- **MCP Server mẫu** (`mcp_server/`): 1 tool minh hoạ (`lookup_sme_fact`), thay bằng
  nguồn dữ liệu/API thật khi cần.

## Cấu trúc thư mục

```
v-nexus/
├── gateway/        FastAPI Gateway — entrypoint, routes /chat /health
├── agent/          Planner Agent (LLM + vòng lặp tool-use)
├── tools/          Tool Registry + tool mẫu + tool gọi MCP Server
├── mcp_server/      MCP Server mẫu (1 tool minh hoạ)
├── domain/         Domain Adapter — PHẦN CẦN THAY khi có đề bài
├── db/             PostgreSQL connector + model mẫu (SQLAlchemy async)
├── frontend/       Chat UI đơn giản (Streamlit)
├── docs/           AI_LOG, PROJECT_DESCRIPTION, timeline, scoring-checklist
├── tests/          Test tối thiểu cho Tool Registry & Gateway health
├── docker-compose.yml
└── .env.example
```

## Quickstart (Docker Compose — khuyến nghị)

```bash
cp .env.example .env        # điền ANTHROPIC_API_KEY
docker compose up --build
```

- Frontend (chat): http://localhost:8501
- Gateway API: http://localhost:8000/health
- MCP Server mẫu: http://localhost:8100/mcp

## Chạy local không dùng Docker

```bash
pip install -r requirements.txt
export $(cat .env | xargs)   # hoặc set biến môi trường thủ công

# Terminal 1 — MCP server mẫu
python mcp_server/server.py

# Terminal 2 — Gateway
uvicorn gateway.app.main:app --reload --port 8000

# Terminal 3 — Frontend
streamlit run frontend/streamlit_app.py
```

Cần Postgres chạy sẵn (local hoặc container riêng) khớp với `DATABASE_URL` trong `.env`.

## Test

```bash
pytest
```

## Tài liệu bắt buộc nộp bài

Xem [docs/](docs/) — đặc biệt `docs/AI_LOG.md` (Nhật ký cộng tác với AI, bắt buộc) và
`docs/PROJECT_DESCRIPTION.md`. Xem tiến độ 48h ở `docs/timeline.md` và tự chấm trước khi
nộp ở `docs/scoring-checklist.md`.

## Cam kết AI-native

Toàn bộ mã nguồn trong khung này được tạo bởi AI (Claude Code). Mọi thay đổi/bổ sung
tiếp theo cần được ghi lại trong `docs/AI_LOG.md`.

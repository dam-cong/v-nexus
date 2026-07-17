# V-Nexus Tutor — VAIC 2026

*"V-Nexus Tutor — Mỗi em một lộ trình, cả trường cùng tiến bộ."*

Đội thi Vietnam AI Innovation Challenge 2026 (48h hackathon, 17–19/7/2026, FPT Tower).
**Nền tảng học Tiếng Anh thích ứng cho trường K12** (bắt đầu lớp 3–4, GDPT 2018) — chẩn
đoán tận gốc lỗ hổng kiến thức của từng học sinh, không chỉ chấm đúng/sai. Xem phân tích
chi tiết ở [docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md)
và kế hoạch triển khai ở [docs/KE_HOACH_TRIEN_KHAI.md](docs/KE_HOACH_TRIEN_KHAI.md).

## Kiến trúc

Hai bề mặt sản phẩm, tách theo ràng buộc mạng — xem đầy đủ ở
[docs/KE_HOACH_TRIEN_KHAI.md](docs/KE_HOACH_TRIEN_KHAI.md):

```
┌─────────────┐      ┌──────────────────────────┐      ┌────────────────────────────┐
│  Frontend   │─────▶│      FastAPI Gateway      │─────▶│      Planner Agent         │
│ (Streamlit  │      │ /diagnostic /practice      │     │  (LLM + Tool Registry)      │
│  cho demo)  │◀─────│ /teacher    /parent  /chat │◀────│                             │
└─────────────┘      └──────────────────────────┘      │  ├─ Domain Adapter          │
                               │                        │  │  (adaptive_tutor_adapter)│
                               ▼                        │  ├─ Tool: diagnose_gap      │
                        ┌─────────────┐                 │  ├─ Tool: generate_practice_path
                        │ PostgreSQL  │                 │  ├─ Tool: teacher_dashboard_query
                        └─────────────┘                 │  └─ Tool: parent_dashboard_query
                                                         └────────────────────────────┘
```

- **Chỉ 1 Planner Agent** — không tạo thêm agent khác.
- **Domain Adapter** (`domain/adapter.py`, `domain/adaptive_tutor_adapter.py`): nơi
  DUY NHẤT chứa prompt + tool đặc thù đề bài.
- **Lõi chẩn đoán KHÔNG phải LLM** — Bayesian Knowledge Tracing (`domain/bkt.py`) trên
  đồ thị tri thức tiên quyết (`domain/knowledge_graph.py`) suy ra gap tường minh, giải
  thích được. LLM chỉ giữ 3 vai trò biên: trích xuất, chấm chủ quan, diễn giải kết quả —
  xem chi tiết ở [docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md](docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md#áp-dụng-ai-vào-từng-bước--và-vì-sao-không-chỉ-là-gọi-llm).
- **Tool Registry** (`tools/registry.py`): đăng ký tool theo format Anthropic tool-use,
  Planner Agent không cần biết tool đến từ đâu.
- REST routes `/diagnostic`, `/practice`, `/teacher`, `/parent` là bề mặt sản phẩm chính
  (chấm điểm ở server, không tin LLM); `/chat` là bot hỏi-đáp phụ, tái dùng Planner Agent.

## Cấu trúc thư mục

```
v-nexus/
├── gateway/        FastAPI Gateway — /diagnostic /practice /teacher /parent /chat /health
├── agent/          Planner Agent (LLM + vòng lặp tool-use)
├── tools/          Tool Registry + 4 tool gia sư thích ứng (adaptive_tutor_tools.py)
├── mcp_server/      MCP Server mẫu (không dùng cho đề bài hiện tại)
├── domain/         Domain Adapter + BKT engine + đồ thị tri thức (xem domain/data/)
├── db/             PostgreSQL connector + schema (Skill, Student, StudentResponse...)
├── frontend/       Chat UI đơn giản (Streamlit) — demo, PWA offline là roadmap
├── docs/           Phân tích đề bài, kế hoạch triển khai, mockup UI (docs/UI/), docs nộp bài
├── tests/          Test cho BKT engine, đồ thị tri thức, dashboard, Tool Registry
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

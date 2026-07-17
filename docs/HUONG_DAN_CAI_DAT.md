# HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY V-NEXUS TUTOR

Mục này hướng dẫn cài đặt từ đầu trên máy developer mới, bao gồm cả cách chạy cục bộ (local dev) và chạy qua Docker.

---

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
3. [Cài đặt cục bộ (Local Dev)](#3-cài-đặt-cục-bộ-local-dev)
   - 3.1 clone repo
   - 3.2 Python virtual environment
   - 3.3 cài thư viện Python
   - 3.4 PostgreSQL
   - 3.5 Anthropic API Key
   - 3.6 Frontend (React + Vite)
4. [Chạy dự án](#4-chạy-dự-án)
   - 4.1 Chạy cục bộ không Docker
   - 4.2 Chạy bằng Docker Compose
5. [Chạy test](#5-chạy-test)
6. [Seed dữ liệu mẫu](#6-seed-dữ-liệu-mẫu)
7. [API Endpoints](#7-api-endpoints)
8. [Khắc phục sự cố](#8-khắc-phục-sự-cố)

---

## 1. Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| **Python** | 3.11+ | Kiểm tra: `python --version` |
| **Node.js** | 18+ | Kiểm tra: `node --version` |
| **npm** | 9+ | Đi kèm Node.js |
| **Docker** | 24+ | Chỉ cần khi chạy Docker mode |
| **Docker Compose** | v2+ | Đi kèm Docker Desktop |
| **PostgreSQL** | 16+ | Cần thiết nếu chạy local (không Docker) |
| **Anthropic API Key** | — | Dùng cho LLM (Claude). Cần có tài khoản tại console.anthropic.com |

---

## 2. Cấu trúc thư mục

```
v-nexus/
├── agent/                  # Planner Agent — planner loop + LLM client
│   ├── planner.py
│   └── llm_client.py
├── ai/                     # AI Core — BKT Engine + Knowledge Graph + CAT + I/O Layers
│   ├── knowledge_graph.json        # 26 skills Toán 6-7
│   ├── knowledge_graph.py          # KnowledgeGraph class
│   ├── bkt_engine.py               # Bayesian Knowledge Tracing engine
│   ├── adaptive_test.py            # Computerized Adaptive Testing (CAT)
│   ├── output_interpreter.py       # Chuyển raw data → NL (teacher/parent/student)
│   └── input_extractor.py          # Trích xuất skills/profile từ text
├── tools/                  # 4 Tools + Question Bank
│   ├── question_bank.py            # Load + query câu hỏi từ JSON
│   ├── questions.json              # 45 sample questions Toán 6-7
│   ├── diagnose_gap_tool.py        # Tool: chẩn đoán lỗ hổng
│   ├── practice_path_tool.py       # Tool: tạo lộ trình ôn tập
│   ├── teacher_dashboard_tool.py   # Tool: dashboard giáo viên
│   └── parent_dashboard_tool.py    # Tool: dashboard phụ huynh
├── domain/                 # Domain Adapter + Prompts
│   ├── domain_adapter.py           # AdaptiveTutorAdapter
│   └── prompts/
│       ├── system.md               # System prompt cho Planner Agent
│       ├── diagnose_explain.md     # Prompt giải thích cho học sinh
│       ├── parent_explain.md       # Prompt giải thích cho phụ huynh
│       └── teacher_explain.md      # Prompt giải thích cho giáo viên
├── gateway/                # FastAPI Gateway — REST API
│   └── app/
│       ├── main.py                 # FastAPI app entrypoint
│       └── routes/
│           ├── chat.py             # POST /chat — planner agent
│           └── diagnose.py         # POST /diagnose — direct diagnosis
├── db/                     # Database layer
│   ├── models.py                   # SQLAlchemy ORM models
│   ├── connector.py                # PostgreSQL async connector
│   └── seed_data.py                # Script seed dữ liệu mẫu
├── frontend/               # React + Vite UI
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── tests/                  # Test suite (pytest)
│   ├── test_bkt_engine.py          # 43 tests — KG + BKT
│   ├── test_tools.py               # 32 tests — 4 Tools
│   ├── test_domain_adapter.py      # 23 tests — Domain Adapter
│   ├── test_output_interpreter.py  # 16 tests — Output Interpreter
│   ├── test_adaptive_test.py       # 24 tests — CAT Engine
│   └── test_integration.py         # 14 tests — End-to-end
├── mcp_server/             # MCP Server (Model Context Protocol)
├── requirements.txt        # Python dependencies tổng hợp
├── docker-compose.yml      # Docker Compose full stack
├── .env.example            # Mẫu biến môi trường
└── docs/
    ├── PROJECT_DESCRIPTION.md
    ├── AI_LOG.md
    └── plan.md
```

---

## 3. Cài đặt cục bộ (Local Dev)

### 3.1 Clone repo

```bash
git clone <repo-url>
cd v-nexus
```

### 3.2 Tạo Python virtual environment

```bash
# Tạo venv
python -m venv venv

# Kích hoạt (Linux/macOS)
source venv/bin/activate

# Kích hoạt (Windows — PowerShell)
venv\Scripts\Activate.ps1
```

Khi kích hoạt thành công, bạn sẽ thấy `(venv)` ở đầu terminal.

### 3.3 Cài thư viện Python

```bash
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi `pip` không tìm thấy package nào, đảm bảo bạn đã kích hoạt `venv`.

Các thư viện chính sẽ được cài:

| Thư viện | Phiên bản | Mục đích |
|---|---|---|
| `fastapi` | ≥ 0.115 | Web framework (Gateway API) |
| `uvicorn[standard]` | ≥ 0.30 | ASGI server cho FastAPI |
| `anthropic` | ≥ 0.40 | Anthropic Claude API client |
| `mcp` | ≥ 1.0 | Model Context Protocol |
| `sqlalchemy[asyncio]` | ≥ 2.0 | ORM + async database |
| `asyncpg` | ≥ 0.29 | PostgreSQL async driver |
| `pydantic` | ≥ 2.8 | Data validation |
| `pytest` | ≥ 8.0 | Test framework |
| `pytest-asyncio` | ≥ 0.24 | Async test support |

### 3.4 PostgreSQL

**Cách nhanh — dùng Docker chạy PostgreSQL (không cần cài PostgreSQL gốc):**

```bash
docker compose up -d db
```

Sẽ chạy PostgreSQL trên cổng **5433** (host) → map sang 5432 (container).

**Cách cài PostgreSQL gốc (nếu không dùng Docker):**

- Ubuntu/Debian: `sudo apt install postgresql postgresql-contrib`
- macOS: `brew install postgresql@16`
- Windows: Tải installer tại postgresql.org/download

Sau đó tạo database và user:

```sql
CREATE USER vnexus WITH PASSWORD 'vnexus';
CREATE DATABASE vnexus OWNER vnexus;
```

### 3.5 Cấu hình biến môi trường

```bash
cp .env.example .env
```

Chỉnh sửa file `.env`:

```env
# --- LLM (Anthropic Claude) ---
ANTHROPIC_API_KEY=sk-ant-...          # BẮT BUỘC — lấy từ console.anthropic.com
LLM_MODEL=claude-sonnet-5             # Model name

# --- PostgreSQL ---
POSTGRES_USER=vnexus
POSTGRES_PASSWORD=vnexus
POSTGRES_DB=vnexus
DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus

# --- MCP Server ---
MCP_SERVER_URL=http://localhost:8100/mcp

# --- Frontend → Gateway ---
GATEWAY_URL=http://localhost:8000
```

**Lưu ý quan trọng:**
- `DATABASE_URL` khi chạy local dùng `localhost:5433` (không phải `db:5432` —那是 Docker internal).
- `ANTHROPIC_API_KEY` là **bắt buộc** cho Planner Agent và Output/Input Interpreters.
- Nếu chưa có API key, hệ thống vẫn chạy được ở chế độ **offline mode** (không gọi LLM, dùng rule-based fallback).

### 3.6 Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:5173`

---

## 4. Chạy dự án

### 4.1 Chạy cục bộ không Docker (Local Dev)

Mở **3 terminal** chạy song song:

**Terminal 1 — PostgreSQL (nếu chưa chạy):**

```bash
docker compose up -d db
```

**Terminal 2 — Backend Gateway:**

```bash
source venv/bin/activate

DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus \
uvicorn gateway.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Gateway sẽ chạy tại: `http://localhost:8000`

**Terminal 3 — Frontend:**

```bash
cd frontend
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:5173`

### 4.2 Chạy bằng Docker Compose (toàn bộ)

```bash
docker compose up -d
```

Lệnh này sẽ khởi động 4 services:
| Service | Cổng | Mô tả |
|---|---|---|
| `db` | 5433 | PostgreSQL 16 |
| `mcp_server` | 8100 | MCP Server |
| `gateway` | 8000 | FastAPI Backend |
| `frontend` | 8501 | React + Vite UI |

**Xem log realtime:**

```bash
# Toàn bộ
docker compose logs -f

# Chỉ backend
docker compose logs -f gateway

# Chỉ frontend
docker compose logs -f frontend
```

**Build lại khi có thay đổi code:**

```bash
docker compose up --build -d
```

**Dừng toàn bộ:**

```bash
docker compose down
```

**Dừng và xóa dữ liệu database:**

```bash
docker compose down -v
```

---

## 5. Chạy test

### Chạy toàn bộ test suite

```bash
source venv/bin/activate
python -m pytest tests/ -v
```

**Kết quả mong đợi:** 154 tests all passing.

### Chạy test theo từng module

```bash
# Phase 1 — Knowledge Graph + BKT Engine (43 tests)
python -m pytest tests/test_bkt_engine.py -v

# Phase 2 — 4 Tools + Question Bank (32 tests)
python -m pytest tests/test_tools.py -v

# Phase 3 — Domain Adapter + Prompts (23 tests)
python -m pytest tests/test_domain_adapter.py -v

# Phase 4 — Output Interpreter + Input Extractor (16 tests)
python -m pytest tests/test_output_interpreter.py -v

# Phase 4 — Computerized Adaptive Testing (24 tests)
python -m pytest tests/test_adaptive_test.py -v

# Phase 5 — End-to-end Integration (14 tests)
python -m pytest tests/test_integration.py -v
```

### Chạy 1 test cụ thể

```bash
python -m pytest tests/test_bkt_engine.py::TestBKTEngineUpdate::test_update_correct_increases_mastery -v
```

---

## 6. Seed dữ liệu mẫu

Trước khi dùng API lần đầu, seed dữ liệu (skills + questions + sample students) vào DB:

```bash
source venv/bin/activate

# Đảm bảo DB đang chạy (docker compose up -d db)
# Đảm bảo DATABASE_URL đúng trong .env hoặc export trực tiếp

DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus \
python -m db.seed_data
```

**Output mong đợi:**

```
✅ Seed complete:
   Skills: 26 new
   Questions: 45 new
   Classes: 1
   Students: 5
   Parents: 2
```

**Dữ liệu seed bao gồm:**
- 26 kỹ năng Toán 6-7 (Phân số, Thập phân, Tỷ lệ, Đại số, Hình học, Thống kê)
- 45 câu hỏi trắc nghiệm mẫu
- 1 lớp: `CLASS01` — Lớp 6A1
- 5 học sinh: `STU01` → `STU05`
- 2 phụ huynh: `PAR01`, `PAR02` (liên kết parent → student)

---

## 7. API Endpoints

Sau khi chạy backend, truy cập Swagger UI tại: `http://localhost:8000/docs`

### Các endpoint chính

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/health` | Kiểm tra trạng thái server |
| `POST` | `/chat` | Gửi tin nhắn → Planner Agent xử lý (role: student/teacher/parent) |
| `POST` | `/diagnose` | Chẩn đoán lỗ hổng kiến thức trực tiếp (không qua chat) |

### Ví dụ gọi `/diagnose` bằng curl

```bash
curl -X POST http://localhost:8000/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU01",
    "answers": [
      {"question_id": "Q_FRAC01_01", "skill_id": "M6.RA.FRAC01", "correct": true},
      {"question_id": "Q_FRAC02_01", "skill_id": "M6.RA.FRAC02", "correct": true},
      {"question_id": "Q_FRAC03_01", "skill_id": "M6.RA.FRAC03", "correct": false},
      {"question_id": "Q_FRAC04_01", "skill_id": "M6.RA.FRAC04", "correct": false}
    ]
  }'
```

### Ví dụ gọi `/chat` (Planner Agent)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Em chưa hiểu phần quy đồng phân số, cô giáo có thể giải thích giúp em không?",
    "student_id": "STU01",
    "role": "student"
  }'
```

---

## 8. Khắc phục sự cố

### `ModuleNotFoundError: No module named 'fastapi'`

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### `psycopg2.OperationalError: could not connect to server`

- Kiểm tra PostgreSQL có đang chạy: `docker compose ps` hoặc `pg_isready`
- Kiểm tra `DATABASE_URL` trong `.env` —端口号 đúng chưa (5433 nếu dùng Docker)
- Nếu dùng Docker: đảm bảo đã `docker compose up -d db`

### `anthropic.APIError: Authentication failed`

- Kiểm tra `ANTHROPIC_API_KEY` trong `.env` có đúng format `sk-ant-...`
- Đảm bảo API key còn hiệu lực tại console.anthropic.com

### `ConnectionRefusedError: [Errno 111] Connection refused` khi gọi LLM

- Hệ thống sẽ tự động chuyển sang **offline mode** (rule-based fallback)
- Kiểm tra kết nối internet
- Kiểm tra API key

### Tests fail — `ModuleNotFoundError`

```bash
source venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Docker build chậm

```bash
# Xóa cache và build lại
docker compose down
docker system prune -f
docker compose up --build -d
```

---

## Tóm tắt nhanh cho developer mới

```bash
# 1. Clone
git clone <repo-url> && cd v-nexus

# 2. Tạo venv + cài deps
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 3. Cấu hình env
cp .env.example .env
# Chỉnh .env — thêm ANTHROPIC_API_KEY, sửa DATABASE_URL dùng localhost:5433

# 4. Chạy PostgreSQL
docker compose up -d db

# 5. Seed dữ liệu
DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus \
python -m db.seed_data

# 6. Chạy backend
DATABASE_URL=postgresql+asyncpg://vnexus:vnexus@localhost:5433/vnexus \
uvicorn gateway.app.main:app --host 0.0.0.0 --port 8000 --reload

# 7. Chạy frontend
cd frontend && npm install && npm run dev

# 8. Mở trình duyệt
# Swagger: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

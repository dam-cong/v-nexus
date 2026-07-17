"""FastAPI Gateway — entrypoint duy nhất của hệ thống V-Nexus."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connector import init_db
from .routes.chat import router as chat_router
from .routes.crud import router as crud_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo CSDL: tự động tạo các bảng và các vai trò (roles) mặc định khi chạy app
    await init_db()
    yield


app = FastAPI(
    title="V-Nexus Gateway",
    lifespan=lifespan,
    description="Gateway API hỗ trợ chẩn đoán và quản lý người dùng V-Nexus Tutor"
)

# Cấu hình CORS để cho phép Frontend React gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Hỗ trợ tất cả các domain hoặc có thể giới hạn nếu cần
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(chat_router)
app.include_router(crud_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

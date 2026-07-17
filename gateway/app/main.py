"""FastAPI Gateway — entrypoint duy nhất của hệ thống V-Nexus."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connector import init_db
from .routes.chat import router as chat_router
from .routes.diagnose import router as diagnose_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="V-Nexus Gateway",
    lifespan=lifespan,
    description="Gateway API hỗ trợ chẩn đoán và quản lý người dùng V-Nexus Tutor"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(diagnose_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

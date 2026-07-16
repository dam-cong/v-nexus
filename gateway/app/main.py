"""FastAPI Gateway — entrypoint duy nhất của hệ thống V-Nexus."""
from fastapi import FastAPI

from .routes.chat import router as chat_router

app = FastAPI(title="V-Nexus Gateway")
app.include_router(chat_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}

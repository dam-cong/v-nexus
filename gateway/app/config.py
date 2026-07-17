"""Cấu hình non-secret của Gateway. Secret (API key, mật khẩu DB) nằm ở .env."""
import os


class Settings:
    api_key: str = os.environ.get("API_KEY", "")
    llm_base_url: str = os.environ.get("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1")
    llm_model: str = os.environ.get("LLM_MODEL", "GLM-5.2")
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://vnexus:vnexus@localhost:5432/vnexus"
    )
    mcp_server_url: str = os.environ.get("MCP_SERVER_URL", "http://mcp_server:8100/mcp")
    auth_secret: str = os.environ.get("AUTH_SECRET", "change-me-dev-only-secret")


settings = Settings()

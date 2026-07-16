"""Cấu hình non-secret của Gateway. Secret (API key, mật khẩu DB) nằm ở .env."""
import os


class Settings:
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    llm_model: str = os.environ.get("LLM_MODEL", "claude-sonnet-5")
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql+asyncpg://vnexus:vnexus@localhost:5432/vnexus"
    )
    mcp_server_url: str = os.environ.get("MCP_SERVER_URL", "http://mcp_server:8100/mcp")


settings = Settings()

"""Cấu hình Gateway — hỗ trợ cập nhật runtime từ database."""
import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Cấu hình LLM unified — runtime mutable.

    Thuộc tính được map từ env vars khi khởi tạo, và có thể được
    ghi đè bởi giá trị lưu trong database (app_settings table).
    """

    def __init__(self):
        self.llm_mode: str = os.environ.get("LLM_MODE", "offline")
        self.llm_api_key: str = os.environ.get("API_KEY", "") or os.environ.get("FPT_API_KEY", "")
        self.llm_base_url: str = os.environ.get("LLM_BASE_URL", "") or os.environ.get(
            "FPT_API_BASE", "https://mkp-api.fptcloud.com/v1"
        )
        self.llm_model: str = os.environ.get("LLM_MODEL", "") or os.environ.get(
            "FPT_MODEL", "DeepSeek-V4-Flash"
        )
        # Legacy aliases (giữ cho backward compat)
        self.fpt_api_key: str = self.llm_api_key
        self.fpt_api_base: str = self.llm_base_url
        self.fpt_model: str = self.llm_model

        self.anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
        self.ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")
        self.ollama_model: str = os.environ.get("OLLAMA_MODEL", "llama3")
        self.database_url: str = os.environ.get(
            "DATABASE_URL", "postgresql+asyncpg://vnexus:vnexus@localhost:5432/vnexus"
        )
        self.mcp_server_url: str = os.environ.get("MCP_SERVER_URL", "http://mcp_server:8100/mcp")
        self.auth_secret: str = os.environ.get("AUTH_SECRET", "change-me-dev-only-secret")

    def update(self, **kwargs):
        """Cập nhật runtime giá trị từ dict."""
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        # Sync legacy aliases
        self.fpt_api_key = self.llm_api_key
        self.fpt_api_base = self.llm_base_url
        self.fpt_model = self.llm_model

    def to_llm_dict(self) -> dict:
        """Trả về dict các trường LLM hiện tại."""
        return {
            "llm_mode": self.llm_mode,
            "llm_api_key": self.llm_api_key,
            "llm_base_url": self.llm_base_url,
            "llm_model": self.llm_model,
        }


settings = Settings()

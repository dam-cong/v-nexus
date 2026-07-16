"""Giao diện Domain Adapter.

Đây là phần DUY NHẤT cần thay khi đề bài chính thức được công bố (11:00, 17/7/2026).
Gateway, Planner Agent, Tool Registry và MCP Server không cần đổi.
"""
from abc import ABC, abstractmethod

from tools.base import Tool


class DomainAdapter(ABC):
    @abstractmethod
    def system_prompt(self) -> str:
        """Prompt hệ thống mô tả vai trò của agent cho domain cụ thể."""

    @abstractmethod
    def tools(self) -> list[Tool]:
        """Danh sách tool domain-specific mà Planner Agent được phép gọi."""

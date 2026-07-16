"""Domain Adapter PLACEHOLDER cho chủ đề "Đổi mới sáng tạo & Năng suất doanh nghiệp
vừa và nhỏ (SME)".

Thay nội dung file này (system_prompt + tools) ngay khi đề bài chính thức được công bố.
Không cần sửa gì ở gateway/, agent/, tools/registry.py hay mcp_server/.
"""
from domain.adapter import DomainAdapter
from tools.base import Tool
from tools.examples.example_tool import echo_tool
from tools.mcp_tool import mcp_lookup_tool


class SMEInnovationAdapter(DomainAdapter):
    def system_prompt(self) -> str:
        return (
            "Bạn là trợ lý AI hỗ trợ doanh nghiệp vừa và nhỏ (SME) đổi mới sáng tạo. "
            "Đây là placeholder — cập nhật vai trò, ngữ cảnh nghiệp vụ và ràng buộc thật "
            "ngay khi đề bài chính thức của VAIC 2026 được công bố."
        )

    def tools(self) -> list[Tool]:
        return [echo_tool, mcp_lookup_tool]

"""Tool bắc cầu để Planner Agent gọi sang MCP Server mẫu (transport: streamable-http)."""
import os

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from tools.base import Tool

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://mcp_server:8100/mcp")


async def _call_mcp(topic: str) -> str:
    async with streamablehttp_client(MCP_SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("lookup_sme_fact", {"topic": topic})
            return result.content[0].text if result.content else ""


mcp_lookup_tool = Tool(
    name="mcp_lookup_sme_fact",
    description="Tra cứu thông tin mẫu từ MCP Server (thay bằng nguồn dữ liệu thật của đề bài).",
    input_schema={
        "type": "object",
        "properties": {"topic": {"type": "string"}},
        "required": ["topic"],
    },
    func=_call_mcp,
)

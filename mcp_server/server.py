"""MCP Server mẫu — 1 tool minh hoạ (transport: streamable-http).

Thay `lookup_sme_fact` bằng tool gọi nguồn dữ liệu/API thật của đề bài khi cần.
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("vnexus-mcp-sample", host="0.0.0.0", port=8100)


@mcp.tool()
def lookup_sme_fact(topic: str) -> str:
    """Trả về thông tin mẫu liên quan tới đổi mới sáng tạo / SME cho chủ đề `topic`."""
    return f"[mock] Dữ liệu mẫu cho '{topic}'. Thay bằng dữ liệu thật của đề bài khi có."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")

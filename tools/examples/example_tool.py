"""Tool mẫu để kiểm tra Tool Registry hoạt động — thay bằng tool thật của đề bài."""
from tools.base import Tool


def _echo(text: str) -> str:
    return f"[echo] {text}"


echo_tool = Tool(
    name="echo",
    description="Lặp lại văn bản đầu vào — dùng để kiểm tra pipeline tool-calling.",
    input_schema={
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    },
    func=_echo,
)

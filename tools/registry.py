"""Tool Registry: đăng ký và gọi tool cho Planner Agent duy nhất của hệ thống."""
import inspect

from tools.base import Tool


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def specs(self) -> list[dict]:
        """Trả về tool specs theo format Anthropic Messages API (tools=...)."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
        ]

    async def call(self, name: str, arguments: dict):
        tool = self._tools[name]
        result = tool.func(**arguments)
        if inspect.isawaitable(result):
            result = await result
        return result

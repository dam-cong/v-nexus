"""Planner Agent — MỘT agent duy nhất của hệ thống.

Nhận tin nhắn, gọi LLM, thực thi tool qua Tool Registry khi model yêu cầu, lặp tới khi
có câu trả lời cuối. Không thêm agent thứ hai ở đây — logic domain-specific (prompt +
tool nào được dùng) nằm trong DomainAdapter (xem domain/adapter.py).
"""
from agent.llm_client import create_message
from domain.adapter import DomainAdapter
from tools.registry import ToolRegistry


class PlannerAgent:
    def __init__(self, domain: DomainAdapter, model: str = "claude-sonnet-5") -> None:
        self.domain = domain
        self.model = model
        self.registry = ToolRegistry()
        for tool in domain.tools():
            self.registry.register(tool)

    async def run(self, message: str, history: list[dict]) -> tuple[str, list[dict]]:
        messages = [*history, {"role": "user", "content": message}]
        tool_specs = self.registry.specs()

        response = create_message(
            model=self.model,
            system=self.domain.system_prompt(),
            messages=messages,
            tools=tool_specs,
        )

        while response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await self.registry.call(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            response = create_message(
                model=self.model,
                system=self.domain.system_prompt(),
                messages=messages,
                tools=tool_specs,
            )

        reply = "".join(block.text for block in response.content if block.type == "text")
        messages.append({"role": "assistant", "content": reply})
        return reply, messages

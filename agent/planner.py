"""Planner Agent — MỘT agent duy nhất của hệ thống.

Gọi LLM (FPT AI / OpenAI-compatible), thực thi tool khi model yêu cầu,
lặp tới khi có câu trả lời cuối. Logic domain-specific nằm trong DomainAdapter.
"""
from __future__ import annotations

from agent.llm_client import create_message, TextBlock, ToolCall
from domain.adapter import DomainAdapter
from tools.registry import ToolRegistry


class PlannerAgent:
    def __init__(self, domain: DomainAdapter, model: str = "GLM-5.2") -> None:
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

        while response.stop_reason == "tool_calls":
            raw_msg = response.raw_message
            messages.append({
                "role": "assistant",
                "content": raw_msg.content if raw_msg.content else "",
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": {"name": tc.name, "arguments": tc.input}}
                    for tc in response.content if isinstance(tc, ToolCall)
                ],
            })

            for tc in response.content:
                if isinstance(tc, ToolCall):
                    result = await self.registry.call(tc.name, tc.input)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result)})

            response = create_message(
                model=self.model,
                system=self.domain.system_prompt(),
                messages=messages,
                tools=tool_specs,
            )

        reply = "".join(block.text for block in response.content if isinstance(block, TextBlock))
        messages.append({"role": "assistant", "content": reply})
        return reply, messages

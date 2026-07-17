"""LLM Client — wrapper mỏng quanh OpenAI-compatible API (FPT AI Inference).

FPT dùng OpenAI format: https://mkp-api.fptcloud.com/v1
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from openai import OpenAI


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.environ.get("API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1"),
        )
    return _client


def get_model() -> str:
    return os.environ.get("LLM_MODEL", "GLM-5.2")


@dataclass
class ToolCall:
    id: str
    name: str
    input: dict = field(default_factory=dict)


@dataclass
class TextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class LLMResponse:
    stop_reason: str
    content: list
    raw_message: object = None


def create_message(
    *,
    model: str,
    system: str,
    messages: list[dict],
    tools: list[dict],
    max_tokens: int = 4096,
) -> LLMResponse:
    client = _get_client()

    api_messages = [{"role": "system", "content": system}]
    api_messages.extend(messages)

    api_tools = _convert_tools(tools) if tools else None

    response = client.chat.completions.create(
        model=model or get_model(),
        messages=api_messages,
        tools=api_tools,
        max_tokens=max_tokens,
    )

    choice = response.choices[0]
    message = choice.message

    if message.tool_calls:
        tool_calls = []
        for tc in message.tool_calls:
            args = {}
            if tc.function.arguments:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError):
                    args = {}
            tool_calls.append(ToolCall(id=tc.id, name=tc.function.name, input=args))
        return LLMResponse(stop_reason="tool_calls", content=tool_calls, raw_message=message)

    text = message.content or ""
    if not text and hasattr(message, "reasoning_content") and message.reasoning_content:
        text = message.reasoning_content
    return LLMResponse(stop_reason="stop", content=[TextBlock(type="text", text=text)], raw_message=message)


def _convert_tools(tools: list[dict]) -> list[dict]:
    """Chuyển tool specs sang OpenAI format."""
    result = []
    for tool in tools:
        if "type" in tool and tool["type"] == "function":
            result.append(tool)
        elif "input_schema" in tool:
            result.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("input_schema", {}),
                },
            })
        elif "name" in tool:
            result.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                    "parameters": tool.get("parameters", tool.get("input_schema", {})),
                },
            })
    return result

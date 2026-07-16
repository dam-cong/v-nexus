"""Wrapper mỏng quanh Anthropic SDK để Planner Agent gọi LLM."""
import os

from anthropic import Anthropic

_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


def create_message(*, model: str, system: str, messages: list[dict], tools: list[dict]):
    return _client.messages.create(
        model=model,
        system=system,
        messages=messages,
        tools=tools,
        max_tokens=1024,
    )

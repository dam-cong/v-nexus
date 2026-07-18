"""LLM client: hỗ trợ cả Anthropic (cũ) và FPT AI Inference (OpenAI-compatible).

FPT endpoint là OpenAI-compatible: https://mkp-api.fptcloud.com/v1
Model mặc định: DeepSeek-V4-Flash (cấu hình qua env FPT_MODEL).
"""
import os

from app.config import settings


def create_message(*, model: str, system: str, messages: list[dict], tools: list[dict]):
    """Giữ nguyên API cho Anthropic (dùng bởi /chat cũ)."""
    from anthropic import Anthropic

    _client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
    return _client.messages.create(
        model=model,
        system=system,
        messages=messages,
        tools=tools,
        max_tokens=1024,
    )


def create_message_fpt(*, system: str, messages: list[dict], tools: list[dict] = None, model: str = None):
    """Gọi FPT AI Inference (OpenAI-compatible chat completions).

    Trả về dict: {"text": str, "tool_calls": [{"name", "input"}]} để Planner Agent
    (hoặc tool trực tiếp) dễ sử dụng. Nếu không có tool_call thì chỉ có text.
    """
    from openai import OpenAI

    client = OpenAI(base_url=settings.llm_base_url, api_key=settings.api_key, timeout=30.0)
    req_model = model or settings.llm_model

    openai_tools = None
    if tools:
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", t.get("parameters", {})),
                },
            }
            for t in tools
        ]

    completion = client.chat.completions.create(
        model=req_model,
        messages=[{"role": "system", "content": system}, *messages],
        tools=openai_tools,
        tool_choice="auto" if openai_tools else None,
        temperature=0.3,
    )
    choice = completion.choices[0].message

    text = choice.content or ""
    tool_calls = []
    if getattr(choice, "tool_calls", None):
        for tc in choice.tool_calls:
            import json

            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            tool_calls.append({"name": tc.function.name, "input": args})

    return {"text": text, "tool_calls": tool_calls}


def create_message_ollama(*, system: str, messages: list[dict], tools: list[dict] = None, model: str = None):
    """Gọi Ollama (OpenAI-compatible chat completions).

    Trả về dict: {"text": str, "tool_calls": [{"name", "input"}]}
    """
    from openai import OpenAI

    client = OpenAI(base_url=settings.ollama_base_url, api_key="ollama", timeout=30.0)
    req_model = model or settings.ollama_model

    openai_tools = None
    if tools:
        openai_tools = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t.get("description", ""),
                    "parameters": t.get("input_schema", t.get("parameters", {})),
                },
            }
            for t in tools
        ]

    completion = client.chat.completions.create(
        model=req_model,
        messages=[{"role": "system", "content": system}, *messages],
        tools=openai_tools,
        tool_choice="auto" if openai_tools else None,
        temperature=0.3,
    )
    choice = completion.choices[0].message

    text = choice.content or ""
    tool_calls = []
    if getattr(choice, "tool_calls", None):
        for tc in choice.tool_calls:
            import json

            try:
                args = json.loads(tc.function.arguments or "{}")
            except Exception:
                args = {}
            tool_calls.append({"name": tc.function.name, "input": args})

    return {"text": text, "tool_calls": tool_calls}


def call_llm(*, system: str, messages: list[dict], tools: list[dict] = None, model: str = None):
    """Bộ điều phối (dispatcher) cuộc gọi LLM dựa trên LLM_MODE."""
    mode = (settings.llm_mode or "offline").lower()
    if mode == "fpt":
        return create_message_fpt(system=system, messages=messages, tools=tools, model=model)
    elif mode == "ollama":
        return create_message_ollama(system=system, messages=messages, tools=tools, model=model)
    elif mode == "offline":
        raise RuntimeError("LLM is configured in offline mode.")
    else:
        raise ValueError(f"Unknown LLM mode: {settings.llm_mode}")


def is_llm_available() -> bool:
    """Kiểm tra xem LLM hiện tại có thể kết nối được không."""
    mode = (settings.llm_mode or "offline").lower()
    if mode == "offline":
        return False

    import requests

    if mode == "fpt":
        if not settings.api_key:
            return False
        try:
            url = f"{settings.llm_base_url.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {settings.api_key}"}
            r = requests.get(url, headers=headers, timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False
    elif mode == "ollama":
        try:
            url = f"{settings.ollama_base_url.rstrip('/')}/models"
            r = requests.get(url, timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False
    return False

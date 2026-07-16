import pytest

from tools.examples.example_tool import echo_tool
from tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_echo_tool_roundtrip():
    registry = ToolRegistry()
    registry.register(echo_tool)

    result = await registry.call("echo", {"text": "hello"})

    assert result == "[echo] hello"


def test_specs_include_registered_tool():
    registry = ToolRegistry()
    registry.register(echo_tool)

    specs = registry.specs()

    assert specs[0]["name"] == "echo"

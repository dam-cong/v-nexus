"""Định nghĩa Tool dùng chung cho Tool Registry."""
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Union

ToolFunc = Callable[..., Union[Any, Awaitable[Any]]]


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    func: ToolFunc

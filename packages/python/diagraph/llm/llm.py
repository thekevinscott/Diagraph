from __future__ import annotations
from typing import Any, Awaitable

from diagraph.classes.types import FunctionLogHandler


class LLM:
    kwargs: dict[str, Any]

    async def run(self, _prompt: Any, _log: FunctionLogHandler, **kwargs) -> Awaitable[Any]:
        ...

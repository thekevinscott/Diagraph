from __future__ import annotations
from typing import Any, Awaitable


class LLM:
    kwargs: dict[str, Any]

    async def run(self, *args, **kwargs) -> Awaitable[Any]:
        ...

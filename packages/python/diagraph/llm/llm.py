from typing import Any, Awaitable


class LLM:
    kwargs: dict[str, Any]

    async def run(self, *args, **kwargs) -> Awaitable[Any]:
        ...

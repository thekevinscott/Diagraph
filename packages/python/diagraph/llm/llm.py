from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import Any, Awaitable

from diagraph.classes.types import FunctionLogHandler


class LLM(metaclass=ABCMeta):
    kwargs: dict[str, Any]

    @abstractmethod
    async def run(
        self, _prompt: Any, _log: FunctionLogHandler, **kwargs
    ) -> Awaitable[Any]:
        ...

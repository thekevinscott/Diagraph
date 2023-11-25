from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

Fn = Callable[..., Any]

Result = Any

LogEventName = Literal["start", "end", "data"]
Rerunner = Callable[..., None]

LogHandler = Callable[[str, str, Fn], None]
FunctionLogHandler = Callable[[LogEventName, str | None], None]
ErrorHandler = Callable[[Exception, Rerunner, Fn], None]
# TODO: Support arbitrary args and kwargs.
FunctionErrorHandler = Callable[[Exception, Rerunner], None]

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

Fn = Callable[..., Any]

Result = Any

LogEventName = Literal["start", "end", "data"]
Rerunner = Callable[..., None]

LogHandler = Callable[[str, dict | None, Fn], None]
FunctionLogHandler = Callable[[LogEventName, dict | None], None]
ErrorHandler = Callable[[Exception, Rerunner, Fn], None]
# TODO: Support arbitrary args and kwargs.
FunctionErrorHandler = Callable[[Exception, Rerunner], None]

from __future__ import annotations

from typing import Callable, Any, Literal

Fn = Callable[..., Any]

Result = Any

LogEventName = Literal["start", "end", "data"]
Rerunner = Callable[..., None]

LogHandler = Callable[[str, str, Fn], None]
FunctionLogHandler = Callable[[LogEventName, str | None], None]
ErrorHandler = Callable[[Exception, Rerunner, Fn], None]
FunctionErrorHandler = Callable[[Exception, Rerunner], None]

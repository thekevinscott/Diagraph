from __future__ import annotations

from typing import Callable, Any

Fn = Callable[..., Any]

Result = Any

LogHandler = Callable[[str, str, Fn], None]
ErrorHandler = Callable[[str, str, Fn], None]

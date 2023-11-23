from __future__ import annotations

import inspect
import functools
from typing import Any, Awaitable, Optional

from ..classes.types import ErrorHandler, Fn, FunctionLogHandler, LogEventName


from ..llm.llm import LLM
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


class UserHandledException(Exception):
    def __init__(self, exception: Exception, raised_exception: Exception) -> None:
        self.exception = exception
        self.raised_exception = raised_exception


__default_llm__: Optional[LLM] = None


def set_default_llm(llm: LLM) -> None:
    global __default_llm__
    if llm is None:
        raise Exception("You cannot pass a null LLM")
    __default_llm__ = llm


def get_default_llm() -> LLM:
    global __default_llm__
    if __default_llm__ is None:
        __default_llm__ = OpenAI()
    return __default_llm__


def get_if_valid_llm(llm: Any) -> LLM:
    # TODO: Enable this
    # if isinstance(llm, LLM):
    #     return llm
    # else:
    #     raise Exception("The llm passed to @prompt is not a valid LLM object; ensure it is a subclass of LLM")
    return llm


def get_llm(wrapper_fn) -> LLM:
    function_llm = getattr(wrapper_fn, "__function_llm__", None)
    if function_llm is not None:
        return get_if_valid_llm(function_llm)

    diagraph_llm = getattr(wrapper_fn, "__diagraph_llm__", None)
    if diagraph_llm is not None:
        return get_if_valid_llm(diagraph_llm)
    return get_default_llm()


async def generate_prompt(func, *args, **kwargs) -> Any:
    if inspect.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    else:
        return func(*args, **kwargs)


def decorate(prompt_fn, _func=None, **kwargs):
    def decorator(
        func: Fn,
    ):  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]:
        @functools.wraps(func)
        async def wrapper_fn(*args, **kwargs) -> Awaitable[Any]:
            return await prompt_fn(wrapper_fn, func, *args, **kwargs)

        setattr(wrapper_fn, IS_DECORATED_KEY, True)
        setattr(wrapper_fn, "__fn__", func)
        for key, value in kwargs.items():
            setattr(wrapper_fn, key, value)
        return wrapper_fn

    if _func is None:
        # Being called with arguments
        return decorator
    else:
        setattr(_func, IS_DECORATED_KEY, True)
        _decorator = decorator(_func)
        setattr(_decorator, "__fn__", _func)
        return _decorator


def prompt(
    _func=None,
    *,
    log: Optional[FunctionLogHandler] = None,
    llm: Optional[LLM] = None,
    error: Optional[ErrorHandler] = None,
):  # -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]] | _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]:
    async def prompt_fn(
        wrapper_fn, decorated_fn: Fn, original_fn: Fn, *args, **kwargs
    ) -> Awaitable[Any]:
        llm = get_llm(wrapper_fn)
        diagraph_log: Optional[FunctionLogHandler] = getattr(
            wrapper_fn, "__diagraph_log__", None
        )
        # diagraph_error: Optional[ErrorHandler] = getattr(
        #     wrapper_fn, "__diagraph_error__", None
        # )

        def _log(event: LogEventName, chunk: str) -> None:
            if log:
                log(event, chunk)
            elif diagraph_log:
                diagraph_log(event, chunk)

        original_fn.prompt = await generate_prompt(decorated_fn, *args, **kwargs)

        return await llm.run(original_fn.prompt, log=_log)
        # try:
        #     return await llm.run(original_fn.prompt, log=_log)
        # except Exception as e:
        #     # TODO: Should both error functions be called? Or should one supersede the other?
        #     for err_handler in [error, diagraph_error]:
        #         if err_handler:
        #             try:
        #                 result = err_handler(e)
        #                 return result
        #             except Exception as raised_exception:
        #                 raise UserHandledException(e, raised_exception)
        #     raise e

    return decorate(prompt_fn, _func, __function_llm__=llm, __function_error__=error)

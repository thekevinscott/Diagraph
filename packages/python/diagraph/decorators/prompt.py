import inspect
import functools
from typing import Any, Awaitable

from ..classes.diagraph_node import DiagraphNode

from ..llm.llm import LLM
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


class UserHandledException(Exception):
    pass


default_llm = OpenAI()


def set_default_llm(llm: LLM):
    global default_llm
    if llm is None:
        raise Exception("You cannot pass a null LLM")
    default_llm = llm


def prompt(
    _func=None, *, log=None, llm=None, error=None, return_type=None
):  # -> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]] | _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]:
    def decorator(
        func,
    ):  # -> _Wrapped[Callable[..., Any], Any, Callable[..., Any], Generator[Any | Literal[''] | None, Any, None]]:
        @functools.wraps(func)
        async def wrapper_fn(node: DiagraphNode, *args, **kwargs) -> Awaitable[Any]:
            global default_llm
            function_llm = getattr(wrapper_fn, "__function_llm__", None)
            diagraph_llm = getattr(wrapper_fn, "__diagraph_llm__", None)
            if function_llm is not None:
                llm = function_llm
            elif diagraph_llm is not None:
                llm = diagraph_llm
            else:
                llm = default_llm
            diagraph_log = getattr(wrapper_fn, "__diagraph_log__", None)
            diagraph_error = getattr(wrapper_fn, "__diagraph_error__", None)

            def _log(event: str, chunk: str):
                if log:
                    log(event, chunk)
                elif diagraph_log:
                    diagraph_log(event, chunk, wrapper_fn)

            if inspect.iscoroutinefunction(func):
                generated_prompt = await func(*args, **kwargs)
            else:
                generated_prompt = func(*args, **kwargs)
            node.prompt = generated_prompt

            try:
                return await llm.run(node.prompt, log=_log)
            except Exception as e:
                # TODO: Should both error functions be called? Or should one supersede the other?
                if error:
                    error(e)
                    raise UserHandledException(e)
                elif diagraph_error:
                    diagraph_error(e, wrapper_fn)
                    raise UserHandledException(e)
                else:
                    raise e

        setattr(wrapper_fn, IS_DECORATED_KEY, True)
        setattr(wrapper_fn, "__fn__", func)
        setattr(wrapper_fn, "__function_llm__", llm)
        return wrapper_fn

    if _func is None:
        # Being called with arguments
        return decorator
    else:
        setattr(_func, IS_DECORATED_KEY, True)
        _decorator = decorator(_func)
        setattr(_decorator, "__fn__", _func)
        return _decorator

import functools
from typing import Any
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


class UserHandledException(Exception):
    pass


def prompt(_func=None, *, log=None, llm=None, error=None, return_type=None):
    if llm is None:
        llm = OpenAI()

    def decorator(func):
        @functools.wraps(func)
        def wrapper_fn(*args, **kwargs):
            diagraph_log = getattr(wrapper_fn, "__log__", None)
            diagraph_error = getattr(wrapper_fn, "__error__", None)

            def _log(event: str, chunk: str):
                if log:
                    log(event, chunk)
                if diagraph_log:
                    diagraph_log(event, chunk, wrapper_fn)

            generated_prompt = func(*args, **kwargs)
            try:
                return llm.run(generated_prompt, log=_log)
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

        return wrapper_fn

    if _func is None:
        # Being called with arguments
        setattr(decorator, IS_DECORATED_KEY, True)
        setattr(decorator, "__fn__", _func)
        return decorator
    else:
        setattr(_func, IS_DECORATED_KEY, True)
        _decorator = decorator(_func)
        setattr(_decorator, "__fn__", _func)
        return _decorator

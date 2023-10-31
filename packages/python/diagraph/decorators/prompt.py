import functools
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


class UserHandledException(Exception):
    pass


def prompt(_func=None, *, log=None, llm=None, error=None, return_type=None):
    if llm is None:
        llm = OpenAI()

    def decorator(func):
        # print(func)

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
            yield generated_prompt

            try:
                yield llm.run(generated_prompt, log=_log)
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
        return wrapper_fn

    if _func is None:
        # Being called with arguments
        return decorator
    else:
        setattr(_func, IS_DECORATED_KEY, True)
        _decorator = decorator(_func)
        setattr(_decorator, "__fn__", _func)
        return _decorator

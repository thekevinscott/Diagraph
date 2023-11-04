import functools

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


def prompt(_func=None, *, log=None, llm=None, error=None, return_type=None):
    def decorator(func):
        # print(func)

        @functools.wraps(func)
        def wrapper_fn(*args, **kwargs):
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

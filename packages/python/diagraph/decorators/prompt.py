import functools
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


def prompt(_func=None, *, llm=None, error=None, return_type=None):
    if llm is None:
        llm = OpenAI()

    def decorator(func):
        @functools.wraps(func)
        def wrapper_fn(*args, **kwargs):
            generated_prompt = func(*args, **kwargs)
            result = llm.run(generated_prompt)
            return result

        return wrapper_fn

    setattr(_func, IS_DECORATED_KEY, True)

    if _func is None:
        setattr(decorator, "__fn__", _func)
        return decorator
    else:
        _decorator = decorator(_func)
        setattr(_decorator, "__fn__", _func)
        return _decorator

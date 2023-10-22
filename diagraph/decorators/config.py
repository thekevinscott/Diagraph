import functools
from ..llm.openai_llm import OpenAI
from .is_decorated import IS_DECORATED_KEY


def config(_func=None, *, llm=None, error=None, return_type=None):
    if llm is None:
        llm = OpenAI()

    def decorator(func):
        @functools.wraps(func)
        def wrapper_fn(*args, **kwargs):
            generated_prompt = func(*args, **kwargs)
            print("> Function: ", func.__name__)
            print(f"Prompt: {generated_prompt}")
            print("-" * 15)
            result = llm.run(generated_prompt)
            return result

        return wrapper_fn

    print("decorate!")
    setattr(decorator, IS_DECORATED_KEY, True)
    print(getattr(decorator, IS_DECORATED_KEY, False))
    print(decorator)

    if _func is None:
        print("1")
        return decorator
    else:
        print("2")
        return decorator(_func)

IS_DECORATED_KEY = "decorated"


def is_decorated(func):
    return getattr(func, IS_DECORATED_KEY, False)

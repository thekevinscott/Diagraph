from typing import Annotated, Any, Callable
from ..classes.types import Fn


def is_annotated(val: Any):
    return hasattr(val, "__metadata__")


def get_annotations(node: Callable):
    # inspect.get_annotations() does not work with MagicMock (mocker.stub())
    # for key, val in inspect.get_annotations(node).items():
    for key, val in node.__annotations__.items():
        if key != "return" and is_annotated(val):
            yield key, val


def get_dependency(val: Annotated) -> Fn:
    return val.__metadata__[0].dependency

import inspect
from typing import Annotated, Any, Callable
from ..classes.types import Fn
from .depends import Depends


def is_annotated(val: Any):
    return hasattr(val, "__metadata__")


def get_dependencies(node: Callable):
    # inspect.get_annotations() does not work with MagicMock (mocker.stub())
    # for key, val in inspect.get_annotations(node).items():
    for val in inspect.signature(node).parameters.values():
    # print(node.__annotations__, inspect.signature(node).parameters.values())
    # for key, val in node.__annotations__.items():
        # print('key', key)
        # print('annotation', val.annotation)
        # print('default', val.default)
        # print('val', val)
        if isinstance(val.default, Depends):
            yield val.default
        elif val.annotation is not None:
            try:
                for metadata in val.annotation.__metadata__:
                    if isinstance(metadata, Depends):
                        yield metadata
                        break
            except Exception:
                pass
        # if key != "return" and is_annotated(val):
        #     yield key, val


def get_dependency(val: Annotated) -> Fn:
    return val.__metadata__[0].dependency

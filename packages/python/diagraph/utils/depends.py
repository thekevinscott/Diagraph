from typing import Callable, Any


class Depends:
    dependency: Callable[..., Any]

    def __init__(self, dependency: Callable[..., Any]):
        self.dependency = dependency

    def __repr__(self) -> str:
        attr = getattr(self.dependency, "__name__", type(self.dependency).__name__)
        return f"{self.__class__.__name__}({attr})"

from typing import Any, Optional
import tiktoken

# To get the tokeniser corresponding to a specific model in the OpenAI API:
from ..decorators import is_decorated
from .types import Node
import inspect


class DiagraphNode:
    __fn__: Node
    depth: int

    def __init__(self, node: Node, depth: int):
        self.__fn__ = node
        self.depth = depth

    def __repr__(self):
        return inspect.getsource(self.__fn__)

    def _is_decorated_(self):
        return is_decorated(self.__fn__)

    # def __getattribute__(self, __name__: str) -> Any:
    #     if __name__ == "prompt":
    #         # if self._is_decorated_() is False:
    #         #     raise Exception("This function has not been decorated with @prompt")

    #         print(super(DiagraphNode, self).__getattr__("node"))

    #         return "foo"

    def prompt(self, *args, **kwargs):
        if self._is_decorated_() is False:
            raise Exception("This function has not been decorated with @prompt")

        kwargs = {
            **kwargs,
        }
        for i, item in enumerate(self.__fn__.__annotations__.items()):
            key, _ = item
            if key != "return" and key not in kwargs:
                if len(args) > 0 and args[i] is not None:
                    kwargs[key] = args[i]
                else:
                    kwargs[key] = f"{{{key}}}"
        return self.__fn__.__fn__(**kwargs)

    def tokens(self, *args, **kwargs):
        if self._is_decorated_() is False:
            raise Exception("This function has not been decorated with @prompt")

        enc = tiktoken.encoding_for_model("gpt-4")
        for i, item in enumerate(self.__fn__.__annotations__.items()):
            key, _ = item
            if key != "return" and key not in kwargs:
                if len(args) > 0 and args[i] is not None:
                    kwargs[key] = args[i]
                else:
                    kwargs[key] = f""
        prompt = self.__fn__.__fn__(**kwargs)
        return len(enc.encode(prompt))

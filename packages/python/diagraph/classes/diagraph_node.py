from __future__ import annotations
from typing import Any
import tiktoken

# To get the tokeniser corresponding to a specific model in the OpenAI API:
from ..decorators.is_decorated import is_decorated
from .graph import Graph, Key


class DiagraphNode:
    diagraph: Any
    __graph__: Graph
    key: Key

    def __init__(self, diagraph, key: Key):
        self.diagraph = diagraph
        self.__graph__ = diagraph.__graph__
        self.key = key

    @property
    def fn(self):
        return self.diagraph.fns[self.key]

    @property
    def ancestors(self):
        return [
            DiagraphNode(self.diagraph, node)
            for node in self.__graph__.out_edges(self.key)
        ]

    @property
    def children(self):
        return [
            DiagraphNode(self.diagraph, node)
            for node in self.__graph__.in_edges(self.key)
        ]

    # @result.setter
    # def result(self, value):
    #     self.traversal.results[self.__fn__] = value

    # def __repr__(self):
    #     return self
    #     # return inspect.getsource(self.fn)

    def _is_decorated_(self):
        return is_decorated(self.fn)

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
        for i, item in enumerate(self.fn.__annotations__.items()):
            ann_key, _ = item
            if ann_key != "return" and ann_key not in kwargs:
                if len(args) > 0 and args[i] is not None:
                    kwargs[ann_key] = args[i]
                else:
                    kwargs[ann_key] = f"{{{ann_key}}}"
        return self.fn.__fn__(**kwargs)

    def tokens(self, *args, **kwargs):
        if self._is_decorated_() is False:
            raise Exception("This function has not been decorated with @prompt")

        enc = tiktoken.encoding_for_model("gpt-4")

        for i, item in enumerate(self.fn.__annotations__.items()):
            ann_key, _ = item
            if ann_key != "return" and ann_key not in kwargs:
                if len(args) > 0 and args[i] is not None:
                    kwargs[ann_key] = args[i]
                else:
                    kwargs[ann_key] = ""
        prompt = self.fn.__fn__(**kwargs)
        return len(enc.encode(prompt))

    def run(self, *input_args):
        self.diagraph.__run_from__(self.key, *input_args)

    @property
    def result(self):
        return self.diagraph.results[self.key]

    @result.setter
    def result(self, value):
        self.diagraph.results[self.key] = value

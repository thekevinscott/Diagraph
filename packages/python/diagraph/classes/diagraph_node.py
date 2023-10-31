from __future__ import annotations
from typing import Any, Callable
import tiktoken

# To get the tokeniser corresponding to a specific model in the OpenAI API:
from ..decorators.is_decorated import is_decorated
from .graph import Graph, Key


def is_function(key: Key):
    return isinstance(key, Callable)


class DiagraphNode:
    diagraph: Any
    __graph__: Graph
    key: Key

    def __init__(self, diagraph, key: Key):
        self.diagraph = diagraph
        self.__graph__ = diagraph.__graph__
        self.key = key

    def __str__(self):
        if is_function(self.key):
            return self.key.__name__
        return self.key

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

    @property
    def depth(self):
        int_key = self.diagraph.__graph__.get_int_key_for_node(self.key)
        # if self.key not in self.diagraph.__graph__.depth_map_by_key:
        #     raise Exception(f"Key {self.key} not in depth map")
        return self.diagraph.__graph__.depth_map_by_key[int_key]

    # @result.setter
    # def result(self, value):
    #     self.traversal.results[self.__fn__] = value

    def __repr__(self):
        # print("repr for diagraph nod")
        return str(self.key)

    #     # return inspect.getsource(self.fn)

    @property
    def __is_decorated__(self):
        # print(self.fn, IS_DECORATED_KEY)
        # print(getattr(self.fn, IS_DECORATED_KEY, False))
        return is_decorated(self.fn)

    def run(self, *input_args):
        self.diagraph.__run_from__(self.key, *input_args)

    @property
    def result(self):
        return self.diagraph.results[self.key]

    @result.setter
    def result(self, value):
        self.diagraph.results[self.key] = value

    @property
    def prompt(self):
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        return self.diagraph.prompts[self.key]

    @prompt.setter
    def prompt(self, value):
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        self.diagraph.prompts[self.key] = value

    @property
    def tokens(self):
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        enc = tiktoken.encoding_for_model("gpt-4")

        prompt = self.prompt
        return len(enc.encode(prompt))

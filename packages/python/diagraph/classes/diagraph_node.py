from __future__ import annotations
from typing import Any, Callable
import tiktoken

# To get the tokeniser corresponding to a specific model in the OpenAI API:
from ..decorators.is_decorated import is_decorated
from .graph import Graph, Key


def is_function(key: Key):
    """
    Check if a given key is a callable function.

    Args:
        key (Key): The key to check.

    Returns:
        bool: True if the key is a callable function, False otherwise.
    """
    return isinstance(key, Callable)


class DiagraphNode:
    """A node in a Diagraph representing a function or a value."""

    diagraph: Any
    __graph__: Graph
    key: Key

    def __init__(self, diagraph, key: Key):
        """
        Initialize a DiagraphNode.

        Args:
            diagraph (Any): The Diagraph instance that contains this node.
            key (Key): The key associated with the node.
        """
        self.diagraph = diagraph
        self.__graph__ = diagraph.__graph__
        self.key = key

    def __str__(self):
        """
        Get a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        if is_function(self.key):
            return self.key.__name__
        return self.key

    @property
    def fn(self):
        """
        Get the function associated with the node.

        Returns:
            Callable: The function associated with the node.
        """
        return self.diagraph.fns[self.key]

    @property
    def ancestors(self):
        """
        Get the ancestor nodes of the current node.

        Returns:
            list[DiagraphNode]: A list of DiagraphNode instances representing the ancestor nodes.
        """
        return [
            DiagraphNode(self.diagraph, node)
            for node in self.__graph__.out_edges(self.key)
        ]

    @property
    def children(self):
        """
        Get the child nodes of the current node.

        Returns:
            list[DiagraphNode]: A list of DiagraphNode instances representing the child nodes.
        """
        return [
            DiagraphNode(self.diagraph, node)
            for node in self.__graph__.in_edges(self.key)
        ]

    @property
    def depth(self):
        """
        Get the depth of the current node in the Diagraph.

        Returns:
            int: The depth of the node.
        """
        int_key = self.diagraph.__graph__.get_int_key_for_node(self.key)
        # if self.key not in self.diagraph.__graph__.depth_map_by_key:
        #     raise Exception(f"Key {self.key} not in depth map")
        return self.diagraph.__graph__.depth_map_by_key[int_key]

    # @result.setter
    # def result(self, value):
    #     self.traversal.results[self.__fn__] = value

    def __repr__(self):
        """
        Get a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        # print("repr for diagraph nod")
        return str(self.key)

    #     # return inspect.getsource(self.fn)

    @property
    def __is_decorated__(self):
        """
        Check if the function associated with the node is decorated with @prompt.

        Returns:
            bool: True if the function is decorated with @prompt, False otherwise.
        """
        # print(self.fn, IS_DECORATED_KEY)
        # print(getattr(self.fn, IS_DECORATED_KEY, False))
        return is_decorated(self.fn)

    def run(self, *input_args):
        """
        Run the Diagraph starting from the current node.

        Args:
            *input_args: Input arguments to be passed to the Diagraph.

        Returns:
            None
        """
        self.diagraph.__run_from__(self.key, *input_args)

    @property
    def result(self):
        """
        Get the result associated with the current node.

        Returns:
            Any: The result associated with the node.
        """
        return self.diagraph.results[self.key]

    @result.setter
    def result(self, value):
        """
        Set the result associated with the current node.

        Args:
            value (Any): The value to set as the result for the node.

        Returns:
            None
        """
        self.diagraph.results[self.key] = value

    @property
    def prompt(self):
        """
        Get the prompt associated with the current node.

        Returns:
            str: The prompt associated with the node.
        """
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        return self.diagraph.prompts[self.key]

    @prompt.setter
    def prompt(self, value):
        """
        Set the prompt associated with the current node.

        Args:
            value (str): The prompt string to associate with the node.

        Returns:
            None
        """
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        self.diagraph.prompts[self.key] = value

    @property
    def tokens(self):
        """
        Get the number of tokens in the associated prompt.

        Returns:
            int: The number of tokens in the associated prompt.
        """
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        enc = tiktoken.encoding_for_model("gpt-4")

        prompt = self.prompt
        return len(enc.encode(prompt))

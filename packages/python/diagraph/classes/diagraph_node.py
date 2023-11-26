from __future__ import annotations

from typing import TYPE_CHECKING

import tiktoken

from ..decorators.is_decorated import is_decorated
from .graph import Graph
from .types import Fn, Result

if TYPE_CHECKING:
    from .diagraph import Diagraph


class DiagraphNode:
    """A node in a Diagraph representing a function or a value."""

    diagraph: Diagraph
    __graph__: Graph
    key: Fn

    def __init__(self, diagraph: Diagraph, key: Fn) -> None:
        """
        Initialize a DiagraphNode.

        Args:
            diagraph (Diagraph): The Diagraph instance that contains this node.
            key (Key): The key associated with the node.
        """
        self.diagraph = diagraph
        self.__graph__ = diagraph.__graph__
        self.key = key

    def __str__(self) -> str:
        """
        Get a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        if isinstance(self.key, str):
            return f"DiagraphNode[{self.key!s}]"

        # return self.key.__name__
        return f"DiagraphNode[{self.key!s}]"

    @property
    def fn(self) -> Fn:
        """
        Get the function associated with the node.

        Returns:
            Fn: The function associated with the node.
        """
        return self.diagraph.fns[self.key]

    @property
    def ancestors(self) -> list[DiagraphNode]:
        """
        Get the ancestor nodes of the current node.

        Returns:
            list[DiagraphNode]: A list of DiagraphNode instances representing the ancestor nodes.
        """
        return self.diagraph.get_ancestors_of_node(self)

    @property
    def children(self) -> list[DiagraphNode]:
        """
        Get the child nodes of the current node.

        Returns:
            list[DiagraphNode]: A list of DiagraphNode instances representing the child nodes.
        """
        return self.diagraph.get_children_of_node(self)

    def __repr__(self) -> str:
        """
        Get a string representation of the node.

        Returns:
            str: The string representation of the node.
        """
        return f"Key: [{self.key!s}]"

    @property
    def __is_decorated__(self) -> bool:
        """
        Check if the function associated with the node is decorated with @prompt.

        Returns:
            bool: True if the function is decorated with @prompt, False otherwise.
        """
        return is_decorated(self.fn)

    def run(self, *input_args, **kwargs) -> Diagraph:
        """
        Run the Diagraph starting from the current node.

        Args:
            *input_args: Input arguments to be passed to the Diagraph.

        Returns:
            None
        """

        self.diagraph.__run_from__(self, *input_args, **kwargs)
        return self.diagraph

    @property
    def __ready__(self) -> bool:
        for ancestor in self.ancestors:
            if ancestor.result is None:
                return False
        return True

    @property
    def result(self) -> Result:
        """
        Get the result associated with the current node.

        Returns:
            Any: The result associated with the node.
        """
        try:
            return self.diagraph.results[self.key]
        except Exception:
            return None

    @result.setter
    def result(self, value: Result) -> None:
        """
        Set the result associated with the current node.

        Args:
            value (Any): The value to set as the result for the node.

        Returns:
            None
        """
        self.diagraph.results[self.key] = value

    @property
    def error(self) -> None | Exception:
        """
        Get the error associated with the current node.

        Returns:
            Exception | None: The error associated with the node.
        """
        try:
            return self.diagraph.errors[self.key]
        except Exception:
            return None

    @error.setter
    def error(self, error: Exception) -> None:
        """
        Set the error associated with the current node.

        Args:
            error (Exception): The error to set as the result for the node.

        Returns:
            None
        """
        self.diagraph.errors[self.key] = error

    @property
    def prompt(self) -> str:
        """
        Get the prompt associated with the current node.

        Returns:
            str: The prompt associated with the node.
        """
        if self.__is_decorated__ is False:
            raise Exception("This function has not been decorated with @prompt")

        return self.diagraph.prompts[self.key]

    @prompt.setter
    def prompt(self, value: str) -> None:
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
    def tokens(self) -> int:
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

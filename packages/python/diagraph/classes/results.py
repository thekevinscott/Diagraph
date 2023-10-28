from __future__ import annotations
from typing import Any

from .types import Node


class DiagraphTraversalResults:
    __traversal__: "DiagraphTraversal"
    __results__: dict[int, Any]

    def __init__(self, traversal):
        self.__traversal__ = traversal
        self.__results__ = {}

    def __getitem__(self, key: Node) -> Any:
        int_rep = self.__traversal__.__graph__.get_key_for_node(key)
        return self.__results__.get(int_rep)

    def __setitem__(self, key: Node, val: Any) -> Any:
        int_rep = self.__traversal__.__graph__.get_key_for_node(key)
        self.__results__[int_rep] = val

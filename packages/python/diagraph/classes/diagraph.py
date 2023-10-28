from __future__ import annotations
from typing import Callable, Optional, overload

from ..utils.build_graph import build_graph

from .graph import Graph
from .types import Node
import networkx as nx

from ..visualization import render_repr_html
from .diagraph_traversal import DiagraphTraversal
from .diagraph_node import DiagraphNode


class Diagraph:
    __graph__: Graph
    terminal_nodes: tuple[Node]
    log: Optional[Callable[[str, str, Node], None]]
    error: Optional[Callable[[str, str, Node], None]]

    def __init__(self, *terminal_nodes: Node, log=None, error=None) -> None:
        self.__graph__ = Graph(build_graph(*terminal_nodes))
        self.terminal_nodes = terminal_nodes
        self.log = log
        self.error = error

    def run(self, *args, **kwargs) -> DiagraphTraversal:
        traversal = DiagraphTraversal(self, log=self.log, error=self.error)
        traversal.run(*args, **kwargs)
        return traversal

    # def _repr_html_(self) -> str:
    #     return render_repr_html(self.dg)

    @overload
    def __getitem__(self, key: int) -> Optional[tuple[DiagraphNode]]:
        ...

    @overload
    def __getitem__(self, key: Node) -> Optional[DiagraphNode]:
        ...

    def __getitem__(self, key: Node | int) -> DiagraphNode | tuple[DiagraphNode]:
        result = self.__graph__[key]
        if isinstance(result, list):
            nodes = [DiagraphNode(self.__graph__, node) for node in result]
            return tuple(nodes)
        elif isinstance(key, Node):
            return DiagraphNode(self.__graph__, key)
        raise Exception(f"Unknown type: {type(key)}")

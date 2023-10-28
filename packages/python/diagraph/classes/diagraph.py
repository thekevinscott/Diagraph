from __future__ import annotations
from typing import Callable, Optional, overload

from .graph import Graph
from .types import Node
import networkx as nx

from ..utils import build_graph, build_nx_graph
from ..visualization import render_repr_html
from .diagraph_traversal import DiagraphTraversal
from .diagraph_node import DiagraphNode


class Diagraph:
    __graph__: Graph
    terminal_nodes: tuple[Node]

    def __init__(self, *terminal_nodes: Node) -> None:
        self.__graph__ = Graph(build_graph(*terminal_nodes))
        self.terminal_nodes = terminal_nodes

    def run(self, *args, **kwargs) -> DiagraphTraversal:
        traversal = DiagraphTraversal(self)
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

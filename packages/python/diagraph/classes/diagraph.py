from typing import Callable, Optional, overload
from .types import Node
import networkx as nx

from ..utils import build_graph, build_nx_graph
from ..visualization import render_repr_html
from .diagraph_traversal import DiagraphTraversal
from .diagraph_node import DiagraphNode


class Diagraph:
    dg: nx.DiGraph
    depth_map_by_key: dict[Node, int]
    depth_map_by_depth: dict[int, set[Node]]

    def __init__(self, *terminal_nodes: Node) -> None:
        dg, depth_map_by_key, depth_map_by_depth = build_nx_graph(*terminal_nodes)
        self.dg = dg
        self.depth_map_by_key = depth_map_by_key
        self.depth_map_by_depth = depth_map_by_depth

    def run(self, *args, **kwargs) -> DiagraphTraversal:
        return DiagraphTraversal(self, *args, **kwargs)

    def _repr_html_(self) -> str:
        return render_repr_html(self.dg)

    @overload
    def __getitem__(self, key: int) -> Optional[tuple[DiagraphNode]]:
        ...

    @overload
    def __getitem__(self, key: Node) -> Optional[DiagraphNode]:
        ...

    def __getitem__(
        self, key: Node | int
    ) -> Optional[DiagraphNode | tuple[DiagraphNode]]:
        if isinstance(key, int):
            _nodes: list[Node] = list(self.depth_map_by_depth.get(key, set()))
            if _nodes is None:
                return _nodes
            _nodes2: list[DiagraphNode] = [DiagraphNode(n, key) for n in _nodes]
            _nodes3: tuple[DiagraphNode] = tuple(_nodes2)
            return _nodes3
        elif isinstance(key, Node):
            depth = self.depth_map_by_key.get(key, None)
            if depth is None:
                return None
            return DiagraphNode(key, depth)
        else:
            raise Exception(
                f"Unknown key provided to index: {key}. You must provide a valid function or integer."
            )

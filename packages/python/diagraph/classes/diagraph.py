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
        traversal = DiagraphTraversal(self)
        traversal.run(*args, **kwargs)
        return traversal

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
        depth_map_by_depth = self.depth_map_by_depth
        depth_map_by_key = self.depth_map_by_key
        if isinstance(key, slice):
            if key.step is not None:
                raise Exception("Slicing with a step is not supported")
            start, stop = key.start, key.stop
            raise Exception("Slicing not implemented yet")
        if isinstance(key, int):
            if key < 0:
                key = max(depth_map_by_depth.keys()) + 1 + key
            nodes: list[Node] = list(depth_map_by_depth.get(key, set()))
            if nodes is None:
                return nodes
            return tuple([DiagraphNode(n, key) for n in nodes])
        elif isinstance(key, Node):
            depth = depth_map_by_key.get(key, None)
            if depth is None:
                return None
            return DiagraphNode(key, depth)
        else:
            raise Exception(
                f"Unknown key provided to index: {key}. You must provide a valid function or integer."
            )

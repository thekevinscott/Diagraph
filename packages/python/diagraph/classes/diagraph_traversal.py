from typing import Callable, Optional, Any

from ..utils import run_node
from .types import Node, Result

# from .diagraph import Diagraph
import networkx as nx
from ..visualization import render_repr_html


class DiagraphTraversal:
    diagraph: Any
    results: dict[Node, Result] = {}
    output: Optional[Result | list[Result]]

    def _repr_html_(self):
        return render_repr_html(self.diagraph.dg)

    def __init__(self, diagraph, log=None):
        self.diagraph = diagraph

    def run(self, *input_args, **kwargs):
        depth_keys = sorted(self.diagraph.depth_map_by_depth.keys())
        if len(depth_keys) == 0:
            return None

        nodes: list[Node] = []
        for depth in depth_keys:
            nodes = self.diagraph.depth_map_by_depth[depth]
            for node in nodes:
                self.results[node] = run_node(node, self.results, input_args, **kwargs)

        if nodes is None:
            return None

        results: list[Result] = []
        for node in nodes:
            results.append(self.results[node])

        if len(results) == 1:
            self.output = results[0]
        else:
            self.output = results

        return self.output

    def __getitem__(self, node_key: str) -> Optional[Callable]:
        return self.diagraph.dg.nodes[node_key]

    # def __getitem__(self, key: Node | int) -> Optional[Node]:
    #     # if key == 'output':
    #     #     return self.output
    #     depth_map_by_depth = self.diagraph.depth_map_by_depth
    #     depth_map_by_key = self.diagraph.depth_map_by_key
    #     if isinstance(key, slice):
    #         if key.step is not None:
    #             raise Exception("Slicing with a step is not supported")
    #         start, stop = key.start, key.stop
    #         raise Exception("Slicing not implemented yet")
    #     if isinstance(key, int):
    #         if key < 0:
    #             key = max(depth_map_by_depth.keys()) + 1 + key
    #         nodes: list[Node] = list(depth_map_by_depth.get(key, set()))
    #         if nodes is None:
    #             return nodes
    #         return tuple([DiagraphTraversalNode(n, key) for n in nodes])
    #     elif isinstance(key, Node):
    #         depth = depth_map_by_key.get(key, None)
    #         if depth is None:
    #             return None
    #         return DiagraphTraversalNode(key, depth)
    #     else:
    #         raise Exception(
    #             f"Unknown key provided to index: {key}. You must provide a valid function or integer."
    #         )

from __future__ import annotations
from typing import Callable, Optional, Any

from .diagraph_traversal_node import DiagraphTraversalNode

from ..utils import run_node
from .types import Node, Result

# from .diagraph import Diagraph
from .graph import Graph
import networkx as nx
from ..visualization import render_repr_html


def validate_node_ancestors(nodes: tuple[Node]):
    for node in nodes:
        for ancestor in node.ancestors:
            if ancestor.result is None:
                raise Exception(
                    "An ancestor is missing a result, run the traversal first"
                )


class DiagraphTraversalResults:
    __traversal__: Any
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


class DiagraphTraversal:
    __graph__: Graph
    terminal_nodes: tuple[Node]
    # results: dict[int, Result] = {}
    output: Optional[Result | list[Result]]
    results: DiagraphTraversalResults
    shadow_graph: dict[int, Node] = {}

    # def _repr_html_(self):
    #     return render_repr_html(self.diagraph.dg)

    def __init__(self, diagraph):
        self.__graph__ = diagraph.__graph__
        self.terminal_nodes = diagraph.terminal_nodes
        self.results = DiagraphTraversalResults(self)

    def run(self, *input_args, **kwargs):
        return self.__run_from__(0, *input_args, **kwargs)

    def __run_from__(self, key: Node | int, *input_args, **kwargs):
        node = self[key]
        if not isinstance(node, tuple):
            node = (node,)
        starting_nodes = node
        validate_node_ancestors(starting_nodes)

        next_layer = set(starting_nodes)
        ran = set()
        while next_layer:
            layer = set()
            for node in next_layer:
                fn_key = node.fn
                if fn_key not in ran:
                    fn = self.__get_fn__(fn_key)
                    self.results[fn_key] = run_node(
                        fn, self.results, *input_args, **kwargs
                    )
                    ran.add(fn_key)
                if node.children:
                    for child in node.children:
                        layer.add(child)
            if len(layer):
                next_layer = layer
            else:
                break

        results: list[Result] = [self.results[node] for node in self.terminal_nodes]

        if len(results) == 1:
            self.output = results[0]
        else:
            self.output = results

        return self.output

    def __getitem__(
        self, key: Node | int
    ) -> DiagraphTraversalNode | tuple[DiagraphTraversalNode]:
        result = self.__graph__[key]
        if isinstance(result, list):
            nodes = [DiagraphTraversalNode(self, node) for node in result]
            return tuple(nodes)
        elif isinstance(key, Node):
            # fn_key = self.__get_fn__(key)
            # print(fn_key)
            return DiagraphTraversalNode(self, key)
        raise Exception(f"Unknown type: {type(key)}")

    def __get_fn__(self, key: Node) -> Node:
        return self.shadow_graph.get(key, key)

    def __setitem__(self, old_fn_def: Node, new_fn_def: Node):
        self.shadow_graph[old_fn_def] = new_fn_def
        # self.diagraph

    #     depth_map_by_depth = self.diagraph.depth_map_by_depth
    #     depth_map_by_key = self.diagraph.depth_map_by_key
    #     depth = depth_map_by_key[old_fn_def]

    #     depth_map_by_key[new_fn_def] = depth
    #     del depth_map_by_key[old_fn_def]

    #     depth_map_by_depth[depth].remove(old_fn_def)
    #     depth_map_by_depth[depth].append(new_fn_def)

    #     for key in self.diagraph.dg.nodes():
    #         node = self.diagraph.dg.nodes()[key]
    #         if node.get("fn") == old_fn_def:
    #             node["fn"] = new_fn_def

    #     if self.results.get(old_fn_def) is not None:
    #         self.results[new_fn_def] = self.results[old_fn_def]
    #         del self.results[old_fn_def]

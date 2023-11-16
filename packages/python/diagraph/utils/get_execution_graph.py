from __future__ import annotations
from typing import Callable, Generator
from ordered_set import OrderedSet
from .get_subgraph_def import get_subgraph_def

# from packages.python.diagraph.classes.diagraph_node import DiagraphNode
# from ..classes.diagraph import Diagraph
from ..classes.graph import Graph, K

GetChildren = Callable[[K], list[K]]


def ancestor_is_upstream_dependency(
    graph: Graph, potential_upstream_dependency: K, parent: K
) -> bool:
    for ancestor in graph.out_edges(potential_upstream_dependency):
        if ancestor == parent:
            return True
        if ancestor_is_upstream_dependency(graph, ancestor, parent) is True:
            return True
    return False


def has_unexecuted_upstream_dependencies(
    graph: Graph, child: K, parent: K, seen: set[K]
) -> bool:
    for ancestor in graph.out_edges(child):
        if (
            # parent != ancestor
            ancestor_is_upstream_dependency(graph, ancestor, parent)
            and ancestor not in seen
        ):
            return True
    return False


def get_execution_graph(graph: Graph, _node_keys: list[K]) -> Generator[list[K]]:
    subgraph_def = get_subgraph_def(graph, _node_keys)
    subgraph = Graph(subgraph_def)
    nodes = subgraph.root_nodes
    yield nodes

    seen = set(nodes)

    while len(nodes):
        out_edges: OrderedSet[K] = OrderedSet()
        for key in nodes:
            for child in subgraph.in_edges(key):
                if child not in seen:
                    # have all this children's ancestors been seen?
                    # a node may have upstream dependencies that have yet to be ran.
                    # these are distinct from ancestors, who may never be ran (e.g.,
                    # we have asked to run from a specific node, or an ancestor represents
                    # a different unrelated branch)
                    valid = True
                    for ancestor in subgraph.out_edges(child):
                        if ancestor not in seen:
                            valid = False
                            break
                    # foo = has_unexecuted_upstream_dependencies(graph, child, key, seen)
                    if valid:
                        out_edges.add(child)

        if len(out_edges) == 0:
            break

        yield list(out_edges)
        for edge in out_edges:
            seen.add(edge)
        nodes = out_edges

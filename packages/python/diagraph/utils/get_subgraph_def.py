from __future__ import annotations
from typing import Optional
from ordered_set import OrderedSet

from ..classes.graph import Graph, K


def get_subgraph_def(
    graph: Graph,
    node_keys: list[K],
    seen: Optional[set] = None,
    subgraph: Optional[dict[K, OrderedSet]] = None,
) -> dict[K, OrderedSet]:
    if subgraph is None:
        subgraph = {}

    if seen is None:
        seen = set()

    for key in node_keys:
        if key not in seen:
            subgraph[key] = subgraph.get(key, OrderedSet())

            children = graph.in_edges(key)
            for child in children:
                if subgraph.get(child) is None:
                    subgraph[child] = OrderedSet()
                subgraph[child].add(key)
            subgraph = get_subgraph_def(graph, children, seen, subgraph)
            seen.add(key)

    return subgraph

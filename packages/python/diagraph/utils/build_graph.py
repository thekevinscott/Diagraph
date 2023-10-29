from typing import Any, TypeVar

from ..utils.annotations import get_annotations, get_dependency


T = TypeVar("T")


def build_graph(*_nodes: T):
    graph = {}
    seen = set()
    nodes: list[T] = list(_nodes)
    for node in nodes:
        graph[node] = graph.get(node, set())
        if node not in seen:
            seen.add(node)
            for _, val in get_annotations(node):
                dep = get_dependency(val)
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph

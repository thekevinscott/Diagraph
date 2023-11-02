from typing import TypeVar

from ..utils.annotations import get_dependencies


T = TypeVar("T")


def build_graph(*_nodes: T):
    graph = {}
    seen = set()
    nodes: list[T] = list(_nodes)
    for node in nodes:
        graph[node] = graph.get(node, set())
        if node not in seen:
            seen.add(node)
            for depends in get_dependencies(node):
                dep = depends.dependency
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph

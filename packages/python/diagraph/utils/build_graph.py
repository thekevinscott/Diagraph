import inspect
from typing import Callable, Generator
from .depends import Depends
from ordered_set import OrderedSet
from ..classes.types import Fn as Fn



def get_dependencies(node: Callable) -> Generator[Fn, None, None]:
    for val in inspect.signature(node).parameters.values():
        if isinstance(val.default, Depends):
            yield val.default.dependency


def build_graph(*_nodes: Fn) -> dict[Fn, OrderedSet[Fn]]:
    graph: dict[Fn, OrderedSet[Fn]] = {}
    seen = set()
    nodes: list[Fn] = list(_nodes)
    for node in nodes:
        if node not in graph:
            graph[node] = OrderedSet({})
        if node not in seen:
            seen.add(node)
            for dep in get_dependencies(node):
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph

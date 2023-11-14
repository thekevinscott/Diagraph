from typing import TypeVar
import inspect
from typing import Callable
from .depends import Depends
from ordered_set import OrderedSet


T = TypeVar("T")


def get_dependencies(node: Callable):
    for val in inspect.signature(node).parameters.values():
        if isinstance(val.default, Depends):
            yield val.default


def build_graph(*_nodes: T):
    graph = {}
    seen = set()
    nodes: list[T] = list(_nodes)
    for node in nodes:
        graph[node] = graph.get(node, OrderedSet())
        if node not in seen:
            seen.add(node)
            for depends in get_dependencies(node):
                dep = depends.dependency
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph

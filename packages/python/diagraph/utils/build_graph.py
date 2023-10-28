from typing import Annotated, Any
import inspect
import networkx as nx

from ..utils.annotations import get_annotations, get_dependency

from ..utils.depends import Depends
from ..classes.types import Node

T = Any
# T = TypeVar("T")


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


def build_depth_map(dg: nx.DiGraph):
    depth_map_by_key: dict[T, int] = {}
    depth_map_by_depth: dict[int, dict[T, None]] = {}
    nodes: list[tuple[T, int]] = [(n, 0) for n in dg.nodes() if dg.out_degree(n) == 0]
    i = 0
    for node, depth in nodes:
        i += 1
        depth_map_by_depth[depth] = depth_map_by_depth.get(depth, {})
        depth_map_by_key[node] = max(depth, depth_map_by_key.get(node, 0))
        # depth_map_by_depth[depth].add(node)
        for view in dg.in_edges(node):
            edge = view[0]
            nodes.append((edge, depth + 1))

    for node, depth in depth_map_by_key.items():
        depth_map_by_depth[depth][node] = None

    return {
        depth: list(depth_map_by_depth[depth].keys())
        for depth in depth_map_by_depth.keys()
    }

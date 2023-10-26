from typing import Callable
import networkx as nx
from ..decorators import is_decorated, config
from ..classes.types import Node


def build_graph(*_nodes: Node):
    graph = {}
    seen = set()
    nodes: list[Node] = list(_nodes)
    for node in nodes:
        graph[node] = graph.get(node, set())
        if node not in seen:
            seen.add(node)
            for key, val in node.__annotations__.items():
                if key != "return" and val is not str:
                    dep = val.dependency
                    if dep not in seen:
                        nodes.append(dep)

                    graph[node].add(dep)

    return graph


def build_depth_map(dg: nx.DiGraph):
    depth_map_by_key: dict[Node, int] = {}
    depth_map_by_depth: dict[int, set[Node]] = {}
    nodes: list[tuple[Node, int]] = [
        (n, 0) for n in dg.nodes() if dg.out_degree(n) == 0
    ]
    i = 0
    for node, depth in nodes:
        i += 1
        if i > 50:
            raise Exception("stop")
        depth_map_by_key[node] = min(depth, depth_map_by_key.get(node, 99999999999999))
        depth_map_by_key[node] = depth
        if depth not in depth_map_by_depth:
            depth_map_by_depth[depth] = set()
        depth_map_by_depth[depth].add(node)
        for view in dg.in_edges(node):
            edge = view[0]
            nodes.append((edge, depth + 1))
    return depth_map_by_key, depth_map_by_depth


def build_nx_graph(
    *nodes: Node,
) -> tuple[nx.DiGraph, dict[Node, int], dict[int, set[Node]]]:
    graph = build_graph(*nodes)
    dg = nx.DiGraph(graph)
    depth_map_by_key, depth_map_by_depth = build_depth_map(dg)

    return dg, depth_map_by_key, depth_map_by_depth

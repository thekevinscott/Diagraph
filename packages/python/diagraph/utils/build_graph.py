from typing import Annotated, Any
import inspect
import networkx as nx

from ..utils.annotations import get_annotations, get_dependency

from ..utils.depends import Depends
from ..classes.types import Node


def build_graph(*_nodes: Node):
    graph = {}
    seen = set()
    nodes: list[Node] = list(_nodes)
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
    depth_map_by_key: dict[Node, int] = {}
    depth_map_by_depth: dict[int, dict[Node, None]] = {}
    nodes: list[tuple[Node, int]] = [
        (n, 0) for n in dg.nodes() if dg.out_degree(n) == 0
    ]
    for node in nodes:
        print("node", node)
    print("=" * 40)
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

    return depth_map_by_key, {
        depth: list(depth_map_by_depth[depth].keys())
        for depth in depth_map_by_depth.keys()
    }


def build_nx_graph(
    *nodes: Node,
) -> tuple[nx.DiGraph, dict[Node, int], dict[int, list[Node]]]:
    graph = build_graph(*nodes)
    dg = nx.DiGraph(graph)
    depth_map_by_key, depth_map_by_depth = build_depth_map(dg)

    return dg, depth_map_by_key, depth_map_by_depth

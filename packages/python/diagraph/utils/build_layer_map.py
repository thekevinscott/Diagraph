from typing import TypeVar
import networkx as nx


T = TypeVar("T")


def build_layer_map(dg: nx.DiGraph):
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
    }, depth_map_by_key

import networkx as nx


def build_layer_map(dg: nx.DiGraph):
    # nodes: list[tuple[T, int]] = [(n, 0) for n in dg.nodes() if dg.in_degree(n) == 0]
    # depth_by_key = {}
    # max_depth = 0
    # for node, depth in nodes:
    #     print("node", node, depth)
    #     depth_by_key[node] = max(depth_by_key.get(node, 0), depth)
    #     for _, child in dg.out_edges(node):
    #         nodes.append((child, depth + 1))
    #     max_depth = max(max_depth, depth)
    # layer_map = {}
    # for node, depth in depth_by_key.items():
    #     depth = max_depth - depth
    #     layer_map[depth] = layer_map.get(depth, []) + [node]

    # sorted_layer_map = {}
    # for key in sorted(layer_map.keys()):
    #     sorted_layer_map[key] = layer_map[key]
    # return sorted_layer_map

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

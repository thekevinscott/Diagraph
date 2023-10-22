from typing import Callable
from ..decorators import is_decorated, config


def build_graph(*nodes: Callable):
    graph = {}
    seen = set()
    nodes = list(nodes)
    for node in nodes:
        if is_decorated(node) is False:
            print("is not decorated (FOR NOW, IGNORE)")
            # node = config(node)
        if graph.get(node) is None:
            graph[node] = set()
        # print(node)
        seen_node = node in seen
        # print(seen_node)
        if seen_node is False:
            seen.add(node)
            for key, val in node.__annotations__.items():
                if key != "return":
                    if val is not str:
                        dep = val.dependency
                        if (dep in seen) is False:
                            # print('add dep')
                            nodes.append(val.dependency)

                        graph[node].add(val.dependency)

    return graph

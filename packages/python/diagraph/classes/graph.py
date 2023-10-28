from typing import Any
import networkx as nx

from ..utils.build_graph import build_depth_map


class Graph:
    __G__: nx.DiGraph
    __key_to_int_representation__: dict[Any, int] = {}
    graph: dict[Any, Any]

    def __init__(self, graph: dict[Any, Any]):
        self.graph = graph
        for key, val in graph.items():
            if isinstance(key, int):
                raise Exception("Keys must not be integers")
            for value in val:
                if isinstance(value, int):
                    raise Exception("Values must not be integers")
        self.__G__ = nx.convert_node_labels_to_integers(
            nx.DiGraph(graph), label_attribute="ref"
        )

        _, depth_map_by_depth = build_depth_map(self.__G__)
        self.depth_map_by_depth = depth_map_by_depth
        for int_representation in self.__G__.nodes():
            ref = self.__G__.nodes[int_representation]["ref"]
            self.__key_to_int_representation__[ref] = int_representation

    def get_key_for_node(self, node: Any) -> int:
        return self.__key_to_int_representation__[node]

    def __get_ref__(self, key: int):
        return self.__G__.nodes[key]["ref"]

    def __getitem__(self, key: Any):
        if isinstance(key, slice):
            if key.step is not None:
                raise Exception("Slicing with a step is not supported")
            start, stop = key.start, key.stop
            raise Exception("Slicing not implemented yet")
        if isinstance(key, int):
            if key < 0:
                key = max(self.depth_map_by_depth.keys()) + 1 + key
            nodes_at_depth = self.depth_map_by_depth[key]
            return [self.__get_ref__(int_rep) for int_rep in nodes_at_depth]

        int_rep = self.__key_to_int_representation__[key]
        return self.__get_ref__(int_rep)

    def __setitem__(self, old: Any, new: Any):
        self.__key_to_int_representation__[new] = self.__key_to_int_representation__[
            old
        ]
        del self.__key_to_int_representation__[old]
        self.__G__.nodes[self.__key_to_int_representation__[new]]["ref"] = new

    def to_json(self):
        return nx.node_link_data(self.__G__)

    def in_edges(self, key: Any):
        key = self.get_key_for_node(key)
        int_representations = [i for i, _ in list(self.__G__.in_edges(key))]
        return [self.__get_ref__(i) for i in int_representations]

    def out_edges(self, key: Any):
        key = self.get_key_for_node(key)
        int_representations = [i for _, i in list(self.__G__.out_edges(key))]
        return [self.__get_ref__(i) for i in int_representations]

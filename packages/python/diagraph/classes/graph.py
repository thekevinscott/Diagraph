from __future__ import annotations
from typing import Any, Generic, TypeVar
import networkx as nx
from ..utils.build_graph import build_depth_map, build_graph

T = TypeVar("T")


class Graph(Generic[T]):
    __G__: nx.DiGraph
    __key_to_int__: dict[T, int]
    graph_def: dict[T, T]
    depth_map_by_depth: dict[int, list[T]]

    def __init__(self, graph_def: dict[T, T]):
        self.graph_def = graph_def
        self.__key_to_int__ = {}
        # for key, val in graph.items():
        #     if isinstance(key, int):
        #         raise Exception("Keys must not be integers")
        #     for value in val:
        #         if isinstance(value, int):
        #             raise Exception("Values must not be integers")
        self.__G__ = nx.convert_node_labels_to_integers(
            nx.DiGraph(self.graph_def), label_attribute="ref"
        )

        self.depth_map_by_depth = build_depth_map(self.__G__)

        for int_representation in self.__G__.nodes():
            ref = self.__G__.nodes[int_representation]["ref"]
            self.__key_to_int__[ref] = int_representation

    def get_key_for_node(self, node: T) -> int:
        return self.__key_to_int__[node]

    def get_node_for_key(self, key: int):
        return self.__G__.nodes[key]["ref"]

    def __getitem__(self, key: T):
        if isinstance(key, slice):
            if key.step is not None:
                raise Exception("Slicing with a step is not supported")
            start, stop = key.start, key.stop
            if start is not None or stop is not None:
                raise Exception("Slicing not implemented yet")
            return Graph(
                {
                    **self.graph_def,
                }
            )
        if isinstance(key, int):
            if key < 0:
                key = max(self.depth_map_by_depth.keys()) + 1 + key
            nodes_at_depth = self.depth_map_by_depth[key]
            return [self.get_node_for_key(int_rep) for int_rep in nodes_at_depth]

        int_rep = self.__key_to_int__[key]
        return self.get_node_for_key(int_rep)

    def __setitem__(self, old: T, new: T):
        # print(self.__key_to_int__)
        # print("old", old, "new", new)
        self.__key_to_int__[new] = self.__key_to_int__[old]
        del self.__key_to_int__[old]
        self.__G__.nodes[self.__key_to_int__[new]]["ref"] = new

    def to_json(self):
        return nx.node_link_data(self.__G__)

    def in_edges(self, key: T):
        key = self.get_key_for_node(key)
        int_representations = [i for i, _ in list(self.__G__.in_edges(key))]
        return [self.get_node_for_key(i) for i in int_representations]

    def out_edges(self, key: T):
        key = self.get_key_for_node(key)
        int_representations = [i for _, i in list(self.__G__.out_edges(key))]
        return [self.get_node_for_key(i) for i in int_representations]

from __future__ import annotations
from typing import Generic, TypeVar, overload
import networkx as nx

from ..utils.build_layer_map import build_layer_map

K = TypeVar("K")


class Graph(Generic[K]):
    __G__: nx.DiGraph
    __key_to_int__: dict[K, int]
    graph_def: dict[K, list[K]]
    depth_map_by_depth: dict[int, list[K]]
    depth_map_by_key: dict[K, int]

    def __init__(self, graph_def: dict[K, list[K]]):
        self.graph_def = {key: list(val) for key, val in graph_def.items()}
        self.__key_to_int__ = {}
        self.__G__ = nx.convert_node_labels_to_integers(
            nx.DiGraph(self.graph_def), label_attribute="ref"
        )

        self.depth_map_by_depth, self.depth_map_by_key = build_layer_map(self.__G__)

        for int_representation in self.__G__.nodes():
            ref = self.__G__.nodes[int_representation]["ref"]
            self.__key_to_int__[ref] = int_representation

    def get_nodes(self) -> list[K]:
        return [self.__G__.nodes[int_rep]["ref"] for int_rep in self.__G__.nodes()]

    def get_int_key_for_node(self, key: K) -> int:
        return self.__key_to_int__[key]

    def get_node_for_int_key(self, key: int) -> K:
        return self.__G__.nodes[key]["ref"]

    @overload
    def __getitem__(self, key: int) -> list[K]:
        ...

    @overload
    def __getitem__(self, key: K) -> K:
        ...

    # def __getitem__(self, key: K | int | slice):
    #     if isinstance(key, slice):
    #         if key.step is not None:
    #             raise Exception("Slicing with a step is not supported")
    #         start, stop = key.start, key.stop
    #         if start is not None or stop is not None:
    #             raise Exception("Slicing not implemented yet")
    #         return Graph(
    #             {
    #                 **self.graph_def,
    #             }
    #         )
    def __getitem__(self, key: K | int):
        if isinstance(key, int):
            if key < 0:
                key = max(self.depth_map_by_depth.keys()) + 1 + key
            nodes_at_depth: list[int] = self.depth_map_by_depth[key]
            return [self.get_node_for_int_key(int_rep) for int_rep in nodes_at_depth]

        return key

    def __setitem__(self, old: K, new: K):
        self.__key_to_int__[new] = self.__key_to_int__[old]
        del self.__key_to_int__[old]
        self.__G__.nodes[self.__key_to_int__[new]]["ref"] = new

    def to_json(self):
        return nx.node_link_data(self.__G__)

    def in_edges(self, key: K):
        key = self.get_int_key_for_node(key)
        int_representations = [i for i, _ in list(self.__G__.in_edges(key))]
        return [self.get_node_for_int_key(i) for i in int_representations]

    def out_edges(self, int_key: K):
        int_key = self.get_int_key_for_node(int_key)
        int_representations = [i for _, i in list(self.__G__.out_edges(int_key))]
        return [self.get_node_for_int_key(i) for i in int_representations]

    @property
    def root_nodes(self) -> list[K]:
        int_keys: list[int] = [
            n for n in self.__G__.nodes() if self.__G__.out_degree(n) == 0
        ]
        return [self.get_node_for_int_key(i) for i in int_keys]

    def _repr_html_(self) -> str:
        # return '''<p>HI</p>'''
        return nx.draw(self.__G__)

    def __str__(self) -> str:
        return str(self.__G__)
        # return nx.write_network_text(self.__G__)

    # return render_repr_html(self.dg)

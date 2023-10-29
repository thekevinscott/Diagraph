from __future__ import annotations
from typing import Any
from .diagraph_node import DiagraphNode
from .graph import Key


class DiagraphLayer:
    diagraph: Any
    nodes: list[DiagraphNode]
    key: int

    def __init__(self, diagraph: Any, key: int, *node_keys: Key):
        self.diagraph = diagraph
        self.nodes = []
        self.key = key
        for node in node_keys:
            self.nodes.append(DiagraphNode(self.diagraph, node))

    def __iter__(self):
        return iter(self.nodes)

    def __getitem__(self, key: Key | int | slice):
        if isinstance(key, slice):
            if key.step is not None:
                raise Exception("Slicing with a step is not supported")
            # start, stop = key.start, key.stop
            # if start is not None or stop is not None:
            raise Exception("Slicing not implemented yet")
        if isinstance(key, int):
            return self.nodes[key]

        for node in self.nodes:
            if node.key == key:
                return node
        raise Exception(f"No node for key {key}")

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, item: Key):
        for node in self.nodes:
            if node.key == item:
                return True
        return False

    def run(self, *input_args, **kwargs):
        self.diagraph.__run_from__(self.key, *input_args, **kwargs)

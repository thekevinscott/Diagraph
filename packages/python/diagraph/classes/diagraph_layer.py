from __future__ import annotations
from typing import Any
from .diagraph_node import DiagraphNode
from .graph import Key


class DiagraphLayer:
    diagraph: Any
    nodes: tuple[DiagraphNode]
    key: int

    def __init__(self, diagraph: Any, key: int, *node_keys: Key):
        self.diagraph = diagraph
        self.key = key
        nodes = []
        for node in node_keys:
            nodes.append(DiagraphNode(self.diagraph, node))
        self.nodes = tuple(nodes)

    def __iter__(self):
        return iter(self.nodes)

    def __str__(self):
        return f"DiagraphLayer({[str(n) for n in self.nodes]})"

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

    @property
    def result(self):
        results = []
        for node in self.nodes:
            results.append(self.diagraph.results[node.key])
        if len(results) == 1:
            return results[0]
        return tuple(results)

    @property
    def prompt(self):
        prompts = []
        for node in self.nodes:
            prompts.append(node.prompt)
        if len(prompts) == 1:
            return prompts[0]
        return tuple(prompts)

    @property
    def tokens(self):
        tokens = []
        for node in self.nodes:
            tokens.append(node.tokens)
        if len(tokens) == 1:
            return tokens[0]
        return tuple(tokens)

    @result.setter
    def result(self, values):
        if isinstance(values, str):
            if len(self.nodes) != 1:
                raise Exception(
                    f"You provided a string as a value but the layer has {len(self.nodes)} nodes. Setting a string value is only supported for a single node. Instead, provide a tuple of values matching of length {len(self.nodes)}"
                )
            self.diagraph.results[self.nodes[0].key] = values
        else:
            if len(self.nodes) != len(values):
                raise Exception(
                    f"Number of results ({len(values)}) does not match number of nodes ({len(self.nodes)})"
                )

            for node, value in zip(self.nodes, values):
                self.diagraph.results[node.key] = value

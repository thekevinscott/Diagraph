from __future__ import annotations
from typing import Any
from .diagraph_node import DiagraphNode
from .graph import Key


class DiagraphLayer:
    """A layer of DiagraphNodes representing a set of related nodes in a Diagraph."""

    diagraph: Any
    nodes: tuple[DiagraphNode]
    key: int

    def __init__(self, diagraph: Any, key: int, *node_keys: Key):
        """
        Initialize a DiagraphLayer.

        Args:
            diagraph (Any): The Diagraph instance that contains this layer.
            key (int): The key associated with the layer.
            *node_keys (Key): Variable number of keys representing nodes in the layer.
        """
        self.diagraph = diagraph
        self.key = key
        nodes = []
        for node in node_keys:
            nodes.append(DiagraphNode(self.diagraph, node))
        self.nodes = tuple(nodes)

    def __iter__(self):
        """
        Create an iterator for the nodes in the layer.

        Returns:
            iter: An iterator for the nodes in the layer.
        """
        return iter(self.nodes)

    def __str__(self):
        """
        Get a string representation of the DiagraphLayer.

        Returns:
            str: A string representation of the layer.
        """
        return f"DiagraphLayer({[str(n) for n in self.nodes]})"

    def __getitem__(self, key: Key | int | slice):
        """
        Get a specific node or a subset of nodes from the layer.

        Args:
            key (Key | int | slice): The key, index, or slice to access the nodes.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The requested node or nodes.
        """
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
        """
        Get the number of nodes in the layer.

        Returns:
            int: The number of nodes in the layer.
        """
        return len(self.nodes)

    def __contains__(self, item: Key):
        """
        Check if a specific node key is present in the layer.

        Args:
            item (Key): The node key to check.

        Returns:
            bool: True if the key is in the layer, False otherwise.
        """
        for node in self.nodes:
            if node.key == item:
                return True
        return False

    def run(self, *input_args, **kwargs):
        """
        Run the Diagraph starting from the nodes in this layer.

        Args:
            *input_args: Input arguments to be passed to the Diagraph.

        Returns:
            None
        """
        self.diagraph.__run_from__(self.key, *input_args, **kwargs)

    @property
    def result(self):
        """
        Get the results of the nodes in the layer.

        Returns:
            Any or tuple[Any]: The result of the nodes, either as a single value or a tuple of values.
        """
        results = []
        for node in self.nodes:
            results.append(self.diagraph.results[node.key])
        if len(results) == 1:
            return results[0]
        return tuple(results)

    @property
    def prompt(self):
        """
        Get the prompts associated with the nodes in the layer.

        Returns:
            str or tuple[str]: The prompt of the nodes, either as a single string or a tuple of strings.
        """
        prompts = []
        for node in self.nodes:
            prompts.append(node.prompt)
        if len(prompts) == 1:
            return prompts[0]
        return tuple(prompts)

    @property
    def tokens(self):
        """
        Get the number of tokens in the prompts associated with the nodes in the layer.

        Returns:
            int or tuple[int]: The number of tokens for each node's prompt.
        """
        tokens = []
        for node in self.nodes:
            tokens.append(node.tokens)
        if len(tokens) == 1:
            return tokens[0]
        return tuple(tokens)

    @result.setter
    def result(self, values):
        """
        Set the results for the nodes in the layer.

        Args:
            values (Any or tuple[Any]): The values to set as results for the nodes.

        Raises:
            Exception: If the number of values does not match the number of nodes.
        """
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

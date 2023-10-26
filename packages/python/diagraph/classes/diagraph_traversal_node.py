from __future__ import annotations
import inspect
from typing import Any

# from .diagraph_traversal import DiagraphTraversal
from .diagraph_node import DiagraphNode


class DiagraphTraversalNode(DiagraphNode):
    traversal: Any
    # DiagraphTraversal

    def __init__(self, traversal, key):
        super().__init__(traversal.__graph__, key)
        self.traversal = traversal

    def run(self, *input_args):
        self.traversal.__run_from__(self.fn, *input_args)

    def __repr__(self):
        return inspect.getsource(self.fn)

    @property
    def ancestors(self):
        return [
            DiagraphTraversalNode(self.traversal, node)
            for node in self.traversal.__graph__.out_edges(self.__key__)
        ]

    @property
    def children(self):
        return [
            DiagraphTraversalNode(self.traversal, node)
            for node in self.traversal.__graph__.in_edges(self.__key__)
        ]

    @property
    def result(self):
        return self.traversal.results[self.fn]

    @result.setter
    def result(self, value):
        self.traversal.results[self.fn] = value

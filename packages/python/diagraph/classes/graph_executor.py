import concurrent.futures
from typing import Any

from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .types import Fn


class GraphExecutor:
    executor: concurrent.futures.ThreadPoolExecutor
    seen_keys: set[Fn]
    fn: Any

    def __init__(
        self,
        starting_nodes: DiagraphNodeGroup,
        fn: Any,
        max_workers: int,
    ):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.seen_keys = set()
        self.fn = fn
        for node in starting_nodes.nodes:
            self.schedule(node)
        self.executor.shutdown(wait=True)

    def schedule(self, node: DiagraphNode) -> None:
        if node.key not in self.seen_keys:
            self.seen_keys.add(node.key)
            future = self.executor.submit(self.fn, node)
            concurrent.futures.wait([future])
            for child in node.children:
                if child.__ready__:
                    self.schedule(child)

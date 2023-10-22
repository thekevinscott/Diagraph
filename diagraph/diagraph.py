from typing import Callable, Optional
import networkx as nx

from .utils import build_graph
from .visualization import render_repr_html
from .diagraph_traversal import DiagraphTraversal

Node = Callable


class Diagraph:
    def __init__(self, *nodes: Node) -> None:
        self.dg = nx.DiGraph(build_graph(*nodes))

    def run(self, *args, **kwargs) -> DiagraphTraversal:
        return DiagraphTraversal(self, *args, **kwargs)

    def _repr_html_(self) -> str:
        return render_repr_html(self.dg)

    def __getitem__(self, node_key: str) -> Optional[Node]:
        return self.dg.nodes[node_key]

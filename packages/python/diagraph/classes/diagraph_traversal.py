from typing import Callable, Optional
import networkx as nx
from ..visualization import render_repr_html


class DiagraphTraversal:
    results = {}
    kwargs = {}

    def _repr_html_(self):
        return render_repr_html(self.template.dg)

    def __init__(self, template, *input_args, log=None, **kwargs):
        self.template = template
        self.run(*input_args)
        self.kwargs = kwargs

    def run(self, *input_args):
        # add teh ability to accept a function in input args, and automatically
        # differentiate between string input / function (node) input / array (functions argument) inputs
        # add an `only` option that will only run that specific node
        nodes = list(reversed(list(nx.topological_sort(self.template.dg))))
        if len(nodes) == 0:
            raise Exception("No graph")

        node = None

        for node in nodes:
            args = []
            for i, item in enumerate(node.__annotations__.items()):
                key, val = item
                if key != "return":
                    if val is str:
                        args.append(input_args[i])  # THIS WONT ALWAYS WORK
                    else:
                        dep = val.dependency
                        args.append(dep.result)
            node.result = node(*args, **self.kwargs)

        if node is None:
            raise Exception("No node")

        self.output = node.result
        return self.output

    def __getitem__(self, node_key: str) -> Optional[Callable]:
        return self.template.dg.nodes[node_key]

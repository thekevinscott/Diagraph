from __future__ import annotations
from typing import Callable, Optional, overload

from ..utils.annotations import get_dependency, is_annotated

from ..decorators.prompt import UserHandledException

from .results import DiagraphTraversalResults

from ..utils.validate_node_ancestors import validate_node_ancestors

from ..utils.build_graph import build_graph

from .graph import Graph
from .types import Node

from .diagraph_traversal import DiagraphTraversal
from .diagraph_node import DiagraphNode


class Diagraph:
    __graph__: Graph
    terminal_nodes: tuple[Node]
    log: Optional[Callable[[str, str, Node], None]]
    error: Optional[Callable[[str, str, Node], None]]
    output: Optional[Result | list[Result]]
    results: DiagraphTraversalResults
    __updated_refs__: dict[Node, Node]

    def __init__(self, *terminal_nodes: Node, log=None, error=None) -> None:
        self.__graph__ = Graph(build_graph(*terminal_nodes))
        self.terminal_nodes = terminal_nodes
        self.log = log
        self.error = error
        self.results = DiagraphTraversalResults(self)
        self.__updated_refs__ = {}
        self.output = None

    def run(self, *args, **kwargs) -> DiagraphTraversal:
        traversal = DiagraphTraversal(self, log=self.log, error=self.error)
        traversal.run(*args, **kwargs)
        return traversal

    # def _repr_html_(self) -> str:
    #     return render_repr_html(self.dg)

    @overload
    def __getitem__(self, key: int) -> Optional[tuple[DiagraphNode]]:
        ...

    @overload
    def __getitem__(self, key: Node) -> Optional[DiagraphNode]:
        ...

    def __getitem__(self, key: Node | int) -> DiagraphNode | tuple[DiagraphNode]:
        result = self.__graph__[key]
        if isinstance(result, list):
            nodes = [DiagraphNode(self, node, None) for node in result]
            return tuple(nodes)
        elif isinstance(key, Node):
            return DiagraphNode(self, key, None)
        raise Exception(f"Unknown type: {type(key)}")

    # def run(self, *input_args, **kwargs):
    #     return self.__run_from__(0, *input_args, **kwargs)

    def __run_from__(self, key: Node | int, *input_args, **kwargs):
        node = self[key]
        if not isinstance(node, tuple):
            node = (node,)
        starting_nodes = node
        validate_node_ancestors(starting_nodes)

        next_layer = set(starting_nodes)
        ran = set()
        try:
            while next_layer:
                layer = set()
                # results: list[Result] = []
                for node in next_layer:
                    if node not in ran:
                        ran.add(node)
                        fn_key = node.fn
                        result = self.__run_node__(node, *input_args, **kwargs)
                        self.results[fn_key] = result
                        # results.append(result)
                    if node.children:
                        for child in node.children:
                            layer.add(child)

                if len(layer):
                    next_layer = layer
                else:
                    break
        except UserHandledException:
            pass

        results = [self.results[node] for node in self.terminal_nodes]

        if len(results) == 1:
            self.output = results[0]
        else:
            self.output = results

        return self.output

    def __run_node__(self, node: Node, *input_args, **kwargs):
        args = []
        arg_index = 0
        fn = self.__updated_refs__.get(node.fn, node.fn)
        for key, val in fn.__annotations__.items():
            if key != "return":
                if is_annotated(val):
                    dep = get_dependency(val)
                    args.append(self.__get_result__(dep))
                else:
                    if arg_index > len(input_args) - 1:
                        raise Exception(f'No argument provided for "{key}"')
                    args.append(input_args[arg_index])
                    arg_index += 1
        setattr(fn, "__log__", self.log)
        setattr(fn, "__error__", self.error)
        return fn(*args, **kwargs)

    def __setitem__(self, old_fn_def: Node, new_fn_def: Node):
        self.__graph__[old_fn_def] = new_fn_def
        self.__update_ref__(old_fn_def, new_fn_def)

    def __update_ref__(self, old_fn_def: Node, new_fn_def: Node):
        self.__updated_refs__[old_fn_def] = new_fn_def

    def __get_result__(self, key: Node):
        key = self.__updated_refs__.get(key, key)
        return self.results[key]

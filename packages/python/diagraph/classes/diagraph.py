from __future__ import annotations
from typing import Any, Callable, Optional, overload
from bidict import bidict

from .diagraph_layer import DiagraphLayer

from ..utils.annotations import get_dependency, is_annotated

from ..decorators.prompt import UserHandledException

from ..utils.validate_node_ancestors import validate_node_ancestors

from ..utils.build_graph import build_graph

from .graph import Graph, Key
from .types import Fn, Result

from .diagraph_node import DiagraphNode

from .historical_bidict import HistoricalBidict


class Diagraph:
    __graph__: Graph
    terminal_nodes: tuple[Key]
    log_handler: Optional[Callable[[str, str, Key], None]]
    error_handler: Optional[Callable[[str, str, Key], None]]
    output: Optional[Result | list[Result]]
    results: HistoricalBidict[Key, Any]
    fns: HistoricalBidict[Key, Fn]
    graph_mapping: bidict[Fn, str]

    def __init__(
        self, *terminal_nodes: Key, log=None, error=None, use_string_keys=False
    ) -> None:
        graph_def = build_graph(*terminal_nodes)
        graph_mapping: dict[Fn, str] = dict()
        graph_def_keys = list(graph_def.keys())

        def get_fn_name(fn: Fn):
            if use_string_keys:
                return fn.__name__
            return fn

        for item in graph_def_keys:
            val = graph_def[item]
            graph_mapping[item] = get_fn_name(item)
            new_val = set()
            while len(val):
                _item = val.pop()
                # for _item in val:
                graph_mapping[_item] = get_fn_name(_item)
                # val.remove(_item)
                new_val.add(get_fn_name(_item))

            del graph_def[item]
            graph_def[get_fn_name(item)] = new_val
        self.graph_mapping = bidict(graph_mapping)
        self.__graph__ = Graph(graph_def)
        self.fns = HistoricalBidict()
        self.results = HistoricalBidict()

        for key in self.__graph__.get_nodes():
            self.fns[key] = self.graph_mapping.inverse[key]
        self.terminal_nodes = [
            DiagraphNode(self, get_fn_name(node)) for node in terminal_nodes
        ]
        self.log_handler = log
        self.error_handler = error
        self.output = None

    # def _repr_html_(self) -> str:
    #     return render_repr_html(self.dg)

    @overload
    def __getitem__(self, key: int) -> Optional[tuple[DiagraphNode]]:
        ...

    @overload
    def __getitem__(self, key: Fn) -> Optional[DiagraphNode]:
        ...

    def __getitem__(self, key: Fn | int) -> DiagraphNode | tuple[DiagraphNode]:
        node_keys = self.__graph__[key]
        if isinstance(node_keys, list):
            return DiagraphLayer(self, key, *node_keys)
        elif isinstance(node_keys, Fn) or isinstance(node_keys, str):
            return DiagraphNode(self, node_keys)
        raise Exception(f"Unknown type: {type(node_keys)}")

    def run(self, *input_args, **kwargs):
        return self.__run_from__(0, *input_args, **kwargs)

    def __run_from__(self, node_key: Fn | int, *input_args, **kwargs):
        nodes = self[node_key]  # nodes is a diagraph node
        if not isinstance(nodes, DiagraphLayer):
            nodes = (nodes,)
        validate_node_ancestors(nodes)

        ran = set()
        try:
            while True:
                layer = set()
                for node in nodes:
                    if node not in ran:
                        ran.add(node)
                        node.result = self.__run_node__(node, *input_args, **kwargs)
                    if node.children:
                        for child in node.children:
                            layer.add(child)
                self.set_output([node.result for node in nodes])

                if len(layer):
                    nodes = layer
                else:
                    break

            self.set_output([node.result for node in self.terminal_nodes])

        except UserHandledException:
            pass

        return self

    def set_output(self, results):
        if len(results) == 1:
            self.output = results[0]
        else:
            self.output = results

    def __run_node__(self, node: Fn, *input_args, **kwargs):
        args = []
        arg_index = 0
        fn = self.fns[node.key]
        for key, val in fn.__annotations__.items():
            if key != "return":
                if is_annotated(val):
                    dep: Fn = get_dependency(val)
                    key_for_fn = self.fns.inverse(dep)
                    args.append(self.results[key_for_fn])
                else:
                    if arg_index > len(input_args) - 1:
                        raise Exception(f'No argument provided for "{key}"')
                    args.append(input_args[arg_index])
                    arg_index += 1
        setattr(fn, "__log__", self.log_handler)
        setattr(fn, "__error__", self.error_handler)
        return fn(*args, **kwargs)

    def __setitem__(self, node_key: Key, fn: Fn):
        self.fns[node_key] = fn

    # #     self.__graph__[old_fn_def] = new_fn_def
    # #     self.__update_ref__(old_fn_def, new_fn_def)

    # # def __update_ref__(self, old_fn_def: Fn, new_fn_def: Fn):
    # #     self.__updated_refs__[old_fn_def] = new_fn_def

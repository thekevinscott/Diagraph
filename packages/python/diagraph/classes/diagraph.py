from __future__ import annotations
import inspect
from datetime import datetime
from typing import Any, Callable, Optional, overload
from bidict import bidict
from ..visualization.render_repr_html import render_repr_html
from ..llm.llm import LLM
from ..decorators.is_decorated import is_decorated

from .diagraph_layer import DiagraphLayer

from ..utils.annotations import get_dependency, is_annotated
from ..utils.depends import Depends

from ..decorators.prompt import UserHandledException, set_default_llm

from ..utils.validate_node_ancestors import validate_node_ancestors

from ..utils.build_graph import build_graph

from .graph import Graph, Key
from .types import Fn

from .diagraph_node import DiagraphNode

from .historical_bidict import HistoricalBidict

default_log_fn = None

def set_default_log(log_fn):
    global default_log_fn
    default_log_fn = log_fn


default_error_fn = None


def set_default_error(error_fn):
    global default_error_fn
    default_error_fn = error_fn


class Diagraph:
    """A directed acyclic graph (Diagraph) for managing and executing a graph of functions."""

    __graph__: Graph

    terminal_nodes: tuple[DiagraphNode]
    log_handler: Optional[Callable[[str, str, Key], None]]
    error_handler: Optional[Callable[[str, str, Key], None]]
    results: HistoricalBidict[Key, Any]
    prompts: HistoricalBidict[Key, str]
    fns: HistoricalBidict[Key, Fn]
    runs: list[Any]
    graph_mapping: bidict[Fn, str]
    llm: Optional[LLM]

    def __init__(
        self,
        *terminal_nodes: Key,
        log=None,
        error=None,
        llm=None,
        use_string_keys=False,
    ) -> None:
        """
        Initialize a Diagraph.

        Args:
            terminal_nodes: The terminal nodes of the graph.
            log (Optional[Callable[[str, str, Key], None]]): A logging function for capturing log messages.
            error (Optional[Callable[[str, str, Key], None]]): An error handling function.
            use_string_keys (bool): Whether to use string keys for functions in the graph.
        """
        graph_def = build_graph(*terminal_nodes)
        graph_mapping: dict[Fn, str | Fn] = dict()
        graph_def_keys = list(graph_def.keys())

        def get_fn_name(fn: Fn) -> str | Fn:
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
        self.prompts = HistoricalBidict()
        self.runs = []
        self.llm = llm

        for key in self.__graph__.get_nodes():
            self.fns[key] = self.graph_mapping.inverse[key]

        self.terminal_nodes = [
            DiagraphNode(self, get_fn_name(node)) for node in terminal_nodes
        ]
        self.log_handler = log or default_log_fn
        self.error_handler = error or default_error_fn

    def _repr_html_(self) -> str:
        html = render_repr_html(self)
        return html
        # return repr_
        # graph_repr = self.__graph__._repr_html_()
        # if graph_repr is not None:
        #     return graph_repr

        # return 'Empty Diagraph'

    def __str__(self) -> str:
        return str(self.__graph__)

    @overload
    def __getitem__(self, key: int) -> Optional[tuple[DiagraphNode]]:
        ...

    @overload
    def __getitem__(self, key: Fn) -> Optional[DiagraphNode]:
        ...

    def __getitem__(self, key: Fn | int) -> DiagraphNode | tuple[DiagraphNode]:
        """
        Retrieve a DiagraphNode or DiagraphLayer associated with a function or depth key.

        Args:
            key (Fn | int): A function or depth key.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The DiagraphNode or DiagraphLayer associated with the key.
        """
        node_keys = self.__graph__[key]
        if isinstance(node_keys, list):
            return DiagraphLayer(self, key, *node_keys)
        elif isinstance(node_keys, Fn) or isinstance(node_keys, str):
            return DiagraphNode(self, node_keys)
        raise Exception(f"Unknown type: {type(node_keys)}")

    def run(self, *input_args, **kwargs):
        """
        Run the Diagraph from the beginning.

        Args:
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """
        return self.__run_from__(0, *input_args, **kwargs)

    def __run_from__(self, node_key: Fn | int, *input_args, **kwargs):
        """
        Run the Diagraph from a specific node.

        Args:
            node_key (Fn | int): The node key or depth to start execution from.
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """
        run = {
            "start": datetime.now(),
            "node_key": node_key,
            "input": input_args,
            "kwargs": kwargs,
            "nodes": {},
        }
        self.runs.append(run)
        nodes = self[node_key]  # nodes is a diagraph node
        if not isinstance(nodes, DiagraphLayer):
            nodes = (nodes,)
        run["starting_nodes"] = nodes
        run["dirty"] = True
        validate_node_ancestors(nodes)
        run["dirty"] = False

        depth = node_key if isinstance(node_key, int) else nodes[0].depth
        run["starting_depth"] = depth
        run["active_depth"] = depth

        ran = set()
        try:
            while True:
                layer = []
                # for node in self[depth]:
                for node in nodes:
                    if node not in ran:
                        run["nodes"][node.key] = {
                            "depth": depth,
                            "executed": None,
                        }
                        ran.add(node)
                        if is_decorated(node.fn):
                            encountered_prompt = False
                            for r in self.__run_node__(node, *input_args, **kwargs):
                                if encountered_prompt is False:
                                    encountered_prompt = True
                                    if r is None:
                                        raise Exception(
                                            f"Prompt returned from function {node.fn.__name__} is None. This is an error, you must return a valid response for the LLM."
                                        )
                                    node.prompt = r
                                else:
                                    result = r
                        else:
                            result = self.__run_node__(node, *input_args, **kwargs)
                        run["nodes"][node.key] = {
                            "executed": datetime.now(),
                            ## TODO: This should reference the result object directly
                            "result": result,
                            "depth": depth,
                        }
                        node.result = result
                    if node.children:
                        for child in node.children:
                            if child not in layer:
                                run["nodes"][child.key] = {
                                    "executed": None,
                                    "depth": depth,
                                }
                                layer.append(child)
                run["active_depth"] = depth

                if len(layer):
                    depth += 1
                    nodes = self[depth]
                    # nodes = layer
                else:
                    break

            run["complete"] = True

        except UserHandledException:
            pass

        return self

    @property
    def result(self):
        """
        Get the results of the terminal nodes.

        Returns:
            Any or tuple[Any]: The result of the terminal nodes, either as a single value or a tuple of values.
        """
        results = []
        latest_run = self.runs[-1]
        if latest_run is None:
            raise Exception("Diagraph has not been run yet")
        if latest_run.get("complete"):
            results = [node.result for node in self.terminal_nodes]
        else:
            latest_depth = latest_run.get("active_depth")
            for node_key, node_run_value in latest_run.get("nodes").items():
                if node_run_value.get("depth") == latest_depth:
                    if node_run_value.get("executed") is None:
                        results.append(None)
                    else:
                        node = self[node_key]
                        results.append(node.result)

        if len(results) == 1:
            return results[0]
        return tuple(results)

    def __run_node__(self, node: Fn, *input_args, **kwargs):
        """
        Execute a single node in the Diagraph.

        Args:
            node (Fn): The function node to execute.
            *input_args: Input arguments to be passed to the node.

        Returns:
            Any: The result of executing the node.
        """
        args = []
        arg_index = 0
        fn = self.fns[node.key]
        # If a user has explicitly specified a dependency via an annotation, we hydrate
        # it below.
        # If an argument is _not_ specified as a dependency, pull off the next input arg
        # in order
        encountered_star = False
        for parameter in inspect.signature(fn).parameters.values():
            # Depends can be passed as Annotated[str, Depends]
            if is_annotated(parameter.annotation):
                dep: Fn = get_dependency(parameter.annotation)
                key_for_fn = self.fns.inverse(dep)
                args.append(self.results[key_for_fn])
            # Depends can be passed as arg: str = Depends(dep)
            # Regular args can be passed as :str = 'foo'
            elif (
                parameter.default is not None
                and parameter.default is not inspect._empty
            ):
                if isinstance(parameter.default, Depends):
                    dep: Fn = parameter.default.dependency
                    try:
                        key_for_fn = self.fns.inverse(dep)
                    except Exception:
                        raise Exception(
                            f"No function has been set for dep {dep}. Available functions: {self.fns}"
                        )
                    args.append(self.results[key_for_fn])
                else:
                    args.append(parameter.default)
            elif not str(parameter).startswith("*"):
                if encountered_star:
                    raise Exception(
                        "Found arguments defined after * args. Ensure *args and **kwargs come at the end of the function parameter definitions."
                    )
                if arg_index > len(input_args) - 1:
                    raise Exception(
                        f'No argument provided for "{parameter.name}" in function {fn.__name__}. This indicates you forgot to call ".run()" with sufficient arguments.'
                    )
                args.append(input_args[arg_index])
                arg_index += 1
            else:
                encountered_star = True

                if arg_index < len(input_args):
                    for arg in input_args[arg_index:]:
                        args.append(arg)

        setattr(fn, "__diagraph_log__", self.log_handler)
        setattr(fn, "__diagraph_error__", self.error_handler)
        setattr(fn, "__diagraph_llm__", self.llm)
        return fn(*args, **kwargs)

    def __setitem__(self, node_key: Key, fn: Fn):
        """
        Add a function to the Diagraph.

        Args:
            node_key (Key): The key associated with the function.
            fn (Fn): The function to add to the Diagraph.
        """
        self.fns[node_key] = fn

    @staticmethod
    def set_llm(llm: LLM):
        set_default_llm(llm)

    @staticmethod
    def set_log(log_fn: Callable):
        set_default_log(log_fn)

    @staticmethod
    def set_error(error_fn: Callable):
        set_default_error(error_fn)

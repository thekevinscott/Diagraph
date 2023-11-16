from __future__ import annotations
import inspect
from datetime import datetime
from typing import Any, Callable, Optional, overload
from bidict import bidict
from ..utils.build_parameters import build_parameters
from ..utils.get_execution_graph import get_execution_graph
from ..visualization.render_repr_html import render_repr_html
from ..llm.llm import LLM
from ..decorators.is_decorated import is_decorated
from asyncio import run, gather

from .diagraph_node_group import DiagraphNodeGroup

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
        self.results = HistoricalBidict()
        self.fns = HistoricalBidict()
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

    # def __str__(self) -> str:
    #     return str(self.__graph__)

    @overload
    def __getitem__(self, key: int) -> DiagraphNodeGroup:
        ...

    @overload
    def __getitem__(self, key: Fn) -> DiagraphNode:
        ...

    def __getitem__(self, key: Fn | int) -> DiagraphNode | DiagraphNodeGroup:
        """
        Retrieve a DiagraphNode or DiagraphLayer associated with a function or depth key.

        Args:
            key (Fn | int): A function or depth key.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The DiagraphNode or DiagraphLayer associated with the key.
        """
        node_keys = self.__graph__[key]
        if isinstance(node_keys, list):
            if isinstance(key, int):
                return DiagraphNodeGroup(self, key, *node_keys)
            raise Exception(
                f"Unexpected key when trying to build a diagraph layer: {key}"
            )
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

        run(self.__run_from__(0, *input_args, **kwargs))
        return self

    async def __run_from__(self, node_key: Fn | int, *input_args, **kwargs):
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
        if not isinstance(nodes, DiagraphNodeGroup):
            nodes = (nodes,)

        run["starting_nodes"] = nodes
        run["dirty"] = True
        validate_node_ancestors(nodes)
        run["dirty"] = False

        depth = node_key if isinstance(node_key, int) else nodes[0].depth
        run["starting_depth"] = depth
        run["active_depth"] = depth

        if isinstance(node_key, int):
            node_keys = [node.key for node in nodes.nodes]
        else:
            node_keys = [node.key for node in nodes]

        try:
            await gather(
                *[
                    self.__execute_node__(self[key], *input_args, **kwargs)
                    for keys in get_execution_graph(self.__graph__, node_keys)
                    for key in keys
                ]
            )
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
            if len(results) == 1:
                return results[0]
            return tuple(results)
        else:
            return None

    async def __execute_node__(self, node: DiagraphNode, *input_args, **kwargs):
        node.result = await self.__run_node__(node, *input_args, **kwargs)

    async def __run_node__(self, node: DiagraphNode, *input_args, **kwargs):
        """
        Execute a single node in the Diagraph.

        Args:
            node (Fn): The function node to execute.
            *input_args: Input arguments to be passed to the node.

        Returns:
            Any: The result of executing the node.
        """
        # If a user has explicitly specified a dependency via an annotation, we hydrate
        # it below.
        # If an argument is _not_ specified as a dependency, pull off the next input arg
        # in order
        fn = self.fns[node.key]

        args = build_parameters(self, fn, input_args)

        setattr(fn, "__diagraph_log__", self.log_handler)
        setattr(fn, "__diagraph_error__", self.error_handler)
        setattr(fn, "__diagraph_llm__", self.llm)
        if is_decorated(fn):
            return await fn(node, *args, **kwargs)
        else:
            if inspect.iscoroutinefunction(fn):
                return await fn(*args, **kwargs)
            else:
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

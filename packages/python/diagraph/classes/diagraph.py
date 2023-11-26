from __future__ import annotations

import concurrent.futures

# import inspect
from datetime import datetime
from typing import Any, overload

from bidict import bidict

from ..decorators.is_decorated import is_decorated
from ..decorators.prompt import set_default_llm
from ..llm.llm import LLM
from ..utils.build_graph import build_graph
from ..utils.build_parameters import build_parameters
from ..utils.get_execution_graph import get_execution_graph
from ..utils.validate_node_ancestors import validate_node_ancestors
from ..visualization.render_repr_html import render_repr_html
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .graph import Graph
from .historical_bidict import HistoricalBidict
from .ordered_set import OrderedSet
from .types import ErrorHandler, Fn, LogHandler, Result

global_log_fn: LogHandler | None = None


def set_global_log(log_fn: LogHandler) -> None:
    global global_log_fn
    global_log_fn = log_fn


global_error_fn: ErrorHandler | None = None


def set_global_error(error_fn: ErrorHandler) -> None:
    global global_error_fn
    global_error_fn = error_fn


MAX_WORKERS = 5


class Diagraph:
    """A directed acyclic graph (Diagraph) for managing
    and executing a graph of functions."""

    __graph__: Graph[Fn]

    terminal_nodes: tuple[DiagraphNode, ...]
    log_handler: LogHandler | None
    error_handler: ErrorHandler | None
    results: HistoricalBidict[Fn, Any]
    errors: HistoricalBidict[Fn, Exception]
    prompts: HistoricalBidict[Fn, str]
    fns: HistoricalBidict[Fn, Fn]
    runs: list[Any]
    graph_mapping: bidict[Fn, str]
    llm: LLM | None
    max_workers: int = MAX_WORKERS

    def __init__(
        self,
        *terminal_nodes: Fn,
        log=None,
        error=None,
        llm=None,
        use_string_keys=False,
        max_workers=MAX_WORKERS,
    ) -> None:
        """
        Initialize a Diagraph.

        Args:
            terminal_nodes: The terminal nodes of the graph.
            log (LogHandler | None): A logging function for capturing log messages.
            error (ErrorHandler | None): An error handling function.
            use_string_keys (bool): Whether to use string keys
                                    for functions in the graph.
        """
        self.max_workers = max_workers
        graph_def: dict[Fn, OrderedSet[Fn]] = build_graph(*terminal_nodes)
        graph_mapping: dict[Fn, str | Fn] = dict()
        graph_def_keys: list[Fn] = list(graph_def.keys())

        def get_fn_key(fn: Fn) -> str | Fn:
            if use_string_keys:
                return fn.__name__
            return fn

        for item in graph_def_keys:
            val = graph_def[item]
            graph_mapping[item] = get_fn_key(item)
            new_val = set()
            while len(val):
                _item = val.pop()
                # for _item in val:
                graph_mapping[_item] = get_fn_key(_item)
                # val.remove(_item)
                new_val.add(get_fn_key(_item))

            del graph_def[item]
            graph_def[get_fn_key(item)] = new_val
        self.graph_mapping = bidict(graph_mapping)
        self.__graph__ = Graph(graph_def)
        self.results = HistoricalBidict()
        self.fns = HistoricalBidict()
        self.errors = HistoricalBidict()
        self.prompts = HistoricalBidict()
        self.runs = []
        self.llm = llm

        for key in self.__graph__.get_nodes():
            self.fns[key] = self.graph_mapping.inverse[key]

        self.terminal_nodes = tuple(DiagraphNode(self, node) for node in terminal_nodes)
        self.log_handler = log or global_log_fn
        # self.error_handler = error or default_error_fn
        self.error_handler = error

    def _repr_html_(self) -> str:
        return render_repr_html(self)

    def get_children_of_node(self, node: DiagraphNode | Fn) -> list[DiagraphNode]:
        key = node.key if isinstance(node, DiagraphNode) else node
        return [DiagraphNode(self, node) for node in self.__graph__.in_edges(key)]

    def get_ancestors_of_node(self, node: DiagraphNode | Fn) -> list[DiagraphNode]:
        key = node.key if isinstance(node, DiagraphNode) else node
        return [DiagraphNode(self, node) for node in self.__graph__.out_edges(key)]

    @overload
    def __getitem__(self, key: int) -> DiagraphNodeGroup:
        ...

    @overload
    def __getitem__(self, key: Fn) -> DiagraphNode:
        ...

    def __getitem__(self, key: Fn | int) -> DiagraphNode | DiagraphNodeGroup:
        """
        Retrieve a DiagraphNode or DiagraphNodeGroup associated with a function or depth key.

        Args:
            key (Fn | int): A function or depth key.

        Returns:
            DiagraphNode or tuple[DiagraphNode]: The DiagraphNode or
            DiagraphNodeGroup associated with the key.
        """
        if isinstance(key, int):
            execution_graph = list(
                get_execution_graph(self.__graph__, self.__graph__.root_nodes),
            )

            if key < 0:
                key = len(execution_graph) + key

            node_keys = execution_graph[key]
            return DiagraphNodeGroup(self, *node_keys)
        return DiagraphNode(self, key)

    def run(self, *input_args, **kwargs) -> Diagraph:
        """
        Run the Diagraph from the beginning.

        Args:
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """

        root_nodes: list[Fn] = self.__graph__.root_nodes
        group = DiagraphNodeGroup(self, *root_nodes)
        self.__run_from__(group, *input_args, **kwargs)
        errors_encountered = self.error
        if errors_encountered is not None:
            if isinstance(errors_encountered, Exception):
                raise Exception(
                    f"Errors encountered. Call .error to see errors. {errors_encountered}",
                )
            errors_encountered = [e for e in errors_encountered if e is not None]
            if len(errors_encountered) > 0:
                raise Exception(
                    f"Errors encountered. Call .error to see errors. {errors_encountered}",
                )
        return self

    def __run_from__(
        self,
        group: DiagraphNodeGroup | DiagraphNode,
        *input_args,
        **kwargs,
    ) -> Diagraph:
        """
        Run the Diagraph from a specific node.

        Args:
            node_key (Fn | int): The node key or depth to start execution from.
            *input_args: Input arguments to be passed to the graph.

        Returns:
            Diagraph: The Diagraph instance.
        """
        starting_node_group = get_diagraph_node_group(self, group)
        run = {
            "start": datetime.now(),
            "node_group": starting_node_group,
            "input": input_args,
            "kwargs": kwargs,
            "nodes": {},
            "dirty": True,
        }
        self.runs.append(run)

        run["starting_nodes"] = starting_node_group
        validate_node_ancestors(starting_node_group)
        run["dirty"] = False

        for node_layer in get_execution_graph(self.__graph__, starting_node_group):
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers,
            ) as executor:
                executor.map(
                    lambda node_key: self.__execute_node__(
                        self[node_key],
                        input_args,
                        kwargs,
                        rerun_kwargs={},
                    ),
                    node_layer,
                )
        run["complete"] = True

        return self

    @property
    def result(self) -> Result | tuple[Result, ...] | None:
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
        return None

    @property
    def error(self) -> Exception | tuple[Exception | None, ...] | None:
        """
        Get the errors of the terminal nodes.

        Returns:
            Exception or tuple[Exception]: The errors of the terminal nodes,
            either as a single value or a tuple of values.
        """
        errors = []
        latest_run = self.runs[-1]
        if latest_run is None:
            raise Exception("Diagraph has not been run yet")

        errors = [node.error for node in self.nodes]
        if len(errors) == 0:
            return None
        if len(errors) == 1:
            return errors[0]
        return tuple(errors)
        # return None

    @property
    def nodes(self):
        return [DiagraphNode(self, node) for node in self.__graph__.nodes]

    def __execute_node__(
        self,
        node: DiagraphNode,
        input_args: tuple[Any, ...],
        input_kwargs: dict[Any, Any],
        rerun_kwargs: None | dict[Any, Any],
    ) -> None:
        # if (
        #     input_kwargs is not None
        #     and "times" in input_kwargs
        #     and input_kwargs.get("times") == 5
        # ):
        #     raise Exception("STOP IT NOT")
        try:
            # print("incoming", input_args, input_kwargs)
            node.result = self.__run_node__(node, input_args, input_kwargs)
        except Exception as e:
            # TODO: Make this a custom error
            if "Error found for " in str(e):
                return
            if "Failed to get result for " in str(e):
                return
            fn = self.fns[node.key]
            fn_error_handler = getattr(fn, "__function_error__", None)

            def rerun(**kwargs: dict[Any, Any]):
                self.__execute_node__(
                    node,
                    input_args,
                    input_kwargs,
                    rerun_kwargs=kwargs,
                )
                # TODO: Refactor or remove this
                return node.result

            for err_handler, accepts_fn in [
                (fn_error_handler, False),
                (self.error_handler, True),
                (global_error_fn, True),
            ]:
                if err_handler:
                    err_handler_args = [e, rerun]
                    if accepts_fn:
                        err_handler_args.append(fn)
                    try:
                        result = err_handler(*err_handler_args, **(rerun_kwargs or {}))
                        node.result = result
                    except Exception as raised_exception:
                        node.error = raised_exception
                    return
            # if no error functions are defined, save the error
            node.error = e

    def __run_node__(
        self,
        node: DiagraphNode,
        input_args: tuple[Any, ...],
        kwargs: dict[Any, Any],
    ) -> Result:
        """
        Execute a single node in the Diagraph.

        Returns:
            Any: The result of executing the node.
        """
        # If a user has explicitly specified a dependency via an annotation, we hydrate
        # it below.
        # If an argument is _not_ specified as a dependency, pull off the next input arg
        # in order
        fn = self.fns[node.key]

        args = build_parameters(self, fn, input_args)

        if self.log_handler:
            log_handler = self.log_handler
            fn.__diagraph_log__ = lambda event, chunk: log_handler(event, chunk, fn)
        # if self.error_handler:
        #     error_handler = self.error_handler
        #     setattr(fn, "__diagraph_error__", lambda e: error_handler(e, fn))
        fn.__diagraph_llm__ = self.llm
        if is_decorated(fn):
            return fn(node, *args, **kwargs)

        # if inspect.iscoroutinefunction(fn):
        #     return await fn(*args, **kwargs)
        # else:
        #     return fn(*args, **kwargs)
        return fn(*args, **kwargs)

    def __setitem__(self, node_key: Fn, fn: Fn) -> None:
        """
        Add a function to the Diagraph.

        Args:
            node_key (Key): The key associated with the function.
            fn (Fn): The function to add to the Diagraph.
        """
        self.fns[node_key] = fn

    @staticmethod
    def set_llm(llm: LLM) -> None:
        set_default_llm(llm)

    @staticmethod
    def set_log(log_fn: LogHandler) -> None:
        set_global_log(log_fn)

    @staticmethod
    def set_error(error_fn: ErrorHandler) -> None:
        set_global_error(error_fn)


def get_diagraph_node_group(
    diagraph: Diagraph,
    group: DiagraphNodeGroup | DiagraphNode,
) -> DiagraphNodeGroup:
    if not isinstance(group, DiagraphNodeGroup):
        return DiagraphNodeGroup(diagraph, group)
    return group

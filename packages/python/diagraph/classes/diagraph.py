from __future__ import annotations

from collections.abc import Callable

# import inspect
from typing import overload

from ..decorators.prompt import set_default_llm
from ..llm.llm import LLM
from ..utils.build_graph import build_graph_mapping
from ..utils.get_execution_graph import get_execution_graph
from ..utils.validate_node_ancestors import validate_node_ancestors
from ..visualization.render_repr_html import render_repr_html
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .diagraph_state.diagraph_state import DiagraphState
from .diagraph_state.diagraph_state_record import (
    DiagraphStateValueEmpty,
)
from .diagraph_state.types import StateValue
from .graph import Graph
from .graph_executor import GraphExecutor
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
    __state__: DiagraphState

    terminal_nodes: tuple[DiagraphNode, ...]
    log_handler: LogHandler | None
    error_handler: ErrorHandler | None
    fns: dict[Fn, Fn]
    llm: LLM | None
    max_workers: int = MAX_WORKERS
    use_string_keys: bool

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
        self.__state__ = DiagraphState()
        self.max_workers = max_workers
        self.use_string_keys = use_string_keys
        self.fns = {}
        self.llm = llm

        graph_def, self.fns = build_graph_mapping(
            *terminal_nodes,
            use_string_keys=use_string_keys,
        )
        self.__graph__ = Graph(graph_def)

        self.terminal_nodes = tuple(DiagraphNode(self, node) for node in terminal_nodes)
        self.log_handler = log or global_log_fn
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

    def __getitem__(
        self,
        key: Fn | int | tuple[Fn, ...],
    ) -> DiagraphNode | DiagraphNodeGroup:
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
        if isinstance(key, Callable):
            return DiagraphNode(self, key)

        if isinstance(key, tuple):
            return DiagraphNodeGroup(self, *key)

        raise Exception(f"Invalid key {key}")

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
        return self

    def __run_from__(
        self,
        group: DiagraphNodeGroup | DiagraphNode,
        *input_args,
        **input_kwargs,
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
        self.__state__.add_timestamp()
        run = {
            "node_group": starting_node_group,
            "input": input_args,
            "kwargs": input_kwargs,
        }
        self.__state__["run"] = run

        validate_node_ancestors(starting_node_group)

        GraphExecutor(
            self,
            DiagraphNodeGroup(
                self,
                *next(get_execution_graph(self.__graph__, starting_node_group)),
            ),
            input_args=input_args,
            input_kwargs=input_kwargs,
            max_workers=self.max_workers,
            global_error_fn=global_error_fn,
        )
        run["complete"] = True
        errors_encountered = self.error
        if errors_encountered is not None:
            if isinstance(errors_encountered, Exception):
                raise Exception(
                    f"Errors encountered. {errors_encountered} Call .error to see errors",
                )
            errors_encountered = [e for e in errors_encountered if e is not None]
            if len(errors_encountered) > 0:
                raise Exception(
                    f"Errors encountered. {errors_encountered} Call .error to see errors",
                )

        return self

    @property
    def __latest_run__(self):
        try:
            return self.__state__["run"]
        except Exception:
            raise Exception("Diagraph has not been run yet") from None

    @property
    def result(self) -> Result | tuple[Result, ...] | None:
        """
        Get the results of the terminal nodes.

        Returns:
            Any or tuple[Any]: The result of the terminal nodes, either as a single value or a tuple of values.
        """
        latest_run = self.__latest_run__
        if latest_run.get("complete") is True:
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
        try:
            assert self.__state__["run"]

            errors = []
            for node in self.nodes:
                try:
                    errors.append(node.error)
                except Exception:  # noqa: PERF203
                    errors.append(None)
            if len(errors) == 0:
                return None
            if len(errors) == 1:
                return errors[0]
            return tuple(errors)
        except Exception:
            raise Exception("Diagraph has not been run yet") from None

    @property
    def nodes(self):
        return [DiagraphNode(self, node) for node in self.__graph__.nodes]

    def __setitem__(self, node_key: Fn, fn: Fn) -> None:
        """
        Add a function to the Diagraph.

        Args:
            node_key (Key): The key associated with the function.
            fn (Fn): The function to add to the Diagraph.
        """
        self.__inc_timestamp__(DiagraphNode(self, node_key))
        self.fns[node_key] = fn

    def __inc_timestamp__(self, node: DiagraphNode):
        self.__state__.add_timestamp()

        def recurse_through_children(node: DiagraphNode, nodes: set[DiagraphNode]):
            nodes.add(node)
            for child in node.children:
                recurse_through_children(child, nodes)
            return nodes

        children = recurse_through_children(node, set())

        def clear(node: DiagraphNode) -> None:
            if node.__is_decorated__:
                self.__state__[("prompt", node.key)] = DiagraphStateValueEmpty()
            self.__state__[("result", node.key)] = DiagraphStateValueEmpty()
            self.__state__[("error", node.key)] = DiagraphStateValueEmpty()

        for child in children:
            clear(child)

    def __set_state__(self, node: DiagraphNode, key: str, value: StateValue) -> None:
        self.__inc_timestamp__(node)
        self.__state__[(key, node.key)] = value

    def __str__(self) -> str:
        """
        Get a string representation of the diagraph.

        Returns:
            str: The string representation of the diagraph.
        """

        return str(self.__graph__)

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

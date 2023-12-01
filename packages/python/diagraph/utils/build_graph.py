from __future__ import annotations

import inspect
from collections.abc import Generator

from ..classes.ordered_set import OrderedSet
from ..classes.types import Fn
from .depends import FnDependency


def get_dependencies(node: Fn) -> Generator[Fn, None, None]:
    """
    Extracts dependencies from the default values of a function's parameters.

    Parameters:
    - node (Fn): The function from which to extract dependencies.

    Yields:
    Generator[Fn, None, None]: A generator of functions representing the dependencies.
    """
    for val in inspect.signature(node).parameters.values():
        if isinstance(val.default, FnDependency):
            yield val.default.dependency


def build_graph(*_nodes: Fn) -> dict[Fn, OrderedSet[Fn]]:
    """
    Builds a dependency graph for a set of functions.

    Parameters:
    - *_nodes (Fn): Variable-length argument list of functions to include in the graph.

    Returns:
    dict[Fn, OrderedSet[Fn]]: A dictionary representing the dependency graph,
    where keys are functions and values are their dependencies.
    """
    graph: dict[Fn, OrderedSet[Fn]] = {}
    seen = set()
    nodes: list[Fn] = list(_nodes)
    for node in nodes:
        if node not in graph:
            graph[node] = OrderedSet()
        if node not in seen:
            seen.add(node)
            for dep in get_dependencies(node):
                if dep not in seen:
                    nodes.append(dep)

                graph[node].add(dep)

    return graph


def build_graph_mapping(*terminal_nodes: Fn, use_string_keys=False):
    graph_def: dict[Fn, OrderedSet[Fn]] = build_graph(*terminal_nodes)
    # graph_mapping: dict[Fn, str | Fn] = dict()
    graph_def_keys: list[Fn] = list(graph_def.keys())
    fns = {}

    def get_fn_key(fn: Fn) -> str | Fn:
        if use_string_keys:
            return fn.__name__
        return fn

    for item in graph_def_keys:
        fns[get_fn_key(item)] = item
        val = graph_def[item]
        # graph_mapping[item] = get_fn_key(item)
        new_val = set()
        while len(val):
            _item = val.pop()
            # for _item in val:
            # graph_mapping[_item] = get_fn_key(_item)
            # val.remove(_item)
            new_val.add(get_fn_key(_item))

        del graph_def[item]
        graph_def[item] = new_val
    return graph_def, fns

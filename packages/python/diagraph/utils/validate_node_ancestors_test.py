import pytest
from typing import Annotated

from .depends import Depends
from ..classes.diagraph import Diagraph
from .validate_node_ancestors import validate_node_ancestors


def describe_validate_node_ancestors():
    def test_it_validates_empty_ancestors():
        def d0a():
            return "d0a"

        diagraph = Diagraph(d0a)
        starting_nodes = tuple(diagraph[0])
        validate_node_ancestors(starting_nodes)

    def test_it_validates_a_single_empty_ancestor():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        diagraph = Diagraph(d1)
        starting_nodes = (diagraph[d1],)
        with pytest.raises(Exception):
            validate_node_ancestors(starting_nodes)

    def test_it_validates_a_single_filled_ancestor():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        diagraph = Diagraph(d1)
        diagraph[d0].result = "foo"
        starting_nodes = (diagraph[d1],)
        validate_node_ancestors(starting_nodes)

    def test_it_validates_a_single_filled_ancestor_and_ignores_previous():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d1].result = "foo"
        starting_nodes = (diagraph[d2],)
        validate_node_ancestors(starting_nodes)

    def test_it_validates_multiple_ancestors():
        def d0():
            return "d0"

        def d1():
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)], d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d1].result = "foo"
        starting_nodes = (diagraph[d2],)
        with pytest.raises(Exception):
            validate_node_ancestors(starting_nodes)
        diagraph[d0].result = "foo"
        validate_node_ancestors(starting_nodes)

    def test_it_validates_multiple_connected_ancestors():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)], d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d0].result = "foo"
        starting_nodes = (diagraph[d2],)
        with pytest.raises(Exception):
            validate_node_ancestors(starting_nodes)
        diagraph[d1].result = "foo"
        validate_node_ancestors(starting_nodes)

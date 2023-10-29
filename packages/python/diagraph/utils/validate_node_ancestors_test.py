import pytest
from typing import Annotated


from .depends import Depends
from ..classes.diagraph import Diagraph
from .validate_node_ancestors import validate_node_ancestors


def describe_validate_node_ancestors():
    def test_it_validates_empty_ancestors():
        def d0a():
            return "d0a"

        nodes = Diagraph(d0a)[0]
        validate_node_ancestors(nodes)

    def test_it_validates_a_single_empty_ancestor():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        nodes = Diagraph(d1)[1]
        with pytest.raises(Exception):
            validate_node_ancestors(nodes)

    def test_it_validates_a_single_filled_ancestor():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        diagraph = Diagraph(d1)
        diagraph[d0].result = "foo"
        validate_node_ancestors(diagraph[1])

    def test_it_validates_a_single_filled_ancestor_and_ignores_previous():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d1].result = "foo"
        validate_node_ancestors(diagraph[2])

    def test_it_validates_multiple_ancestors():
        def d0():
            return "d0"

        def d1():
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)], d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d1].result = "foo"
        layer = diagraph[1]
        with pytest.raises(Exception):
            validate_node_ancestors(layer)
        diagraph[d0].result = "foo"

        validate_node_ancestors(layer)

    def test_it_validates_multiple_connected_ancestors():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)], d1: Annotated[str, Depends(d1)]):
            return "d2"

        diagraph = Diagraph(d2)
        diagraph[d0].result = "foo"
        layer = diagraph[2]
        with pytest.raises(Exception):
            validate_node_ancestors(layer)
        diagraph[d1].result = "foo"
        validate_node_ancestors(layer)

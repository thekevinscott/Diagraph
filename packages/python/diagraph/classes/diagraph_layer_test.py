from typing import Annotated

from .diagraph import Diagraph

from ..utils.depends import Depends
from .diagraph_layer import DiagraphLayer


def describe_diagraph_layer():
    def test_it_instantiates():
        DiagraphLayer(Diagraph())

    def test_it_iterates_through_nodes():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)]):
            return "d2"

        for node in Diagraph(d1, d2)[1]:
            assert node.key in [d1, d2]

    def test_it_can_index_into_a_node():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)]):
            return "d2"

        diagraph = Diagraph(d1, d2)
        assert diagraph[1][0].key == d1
        assert diagraph[1][1].key == d2

    def test_it_can_return_len():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)]):
            return "d2"

        diagraph = Diagraph(d1, d2)
        assert len(diagraph[0]) == 1
        assert len(diagraph[1]) == 2

    def test_it_can_return_in():
        def d0():
            return "d0"

        def d1(d0: Annotated[str, Depends(d0)]):
            return "d1"

        def d2(d0: Annotated[str, Depends(d0)]):
            return "d2"

        layer = Diagraph(d1, d2)[1]
        assert d0 not in layer
        assert d1 in layer
        assert d2 in layer

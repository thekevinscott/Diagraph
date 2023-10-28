import inspect
from typing import Annotated
from .diagraph import Diagraph
from .diagraph_node import DiagraphNode
from ..utils.depends import Depends
from ..decorators import prompt


def describe_instantiation():
    def test_it_instantiates_empty_diagraph():
        diagraph = Diagraph()

    def test_it_instantiates_a_single_item_diagraph():
        def foo():
            return "foo"

        diagraph = Diagraph(foo)


def describe_nodes():
    def test_it_gets_back_a_node_wrapper_for_a_function():
        def foo():
            return "foo"

        diagraph = Diagraph(foo)

        node = diagraph[foo]
        assert isinstance(node, DiagraphNode)
        assert node.fn == foo


def describe_indexing():
    def test_it_gets_back_a_node_wrapper_for_an_index():
        def foo():
            return "foo"

        def bar(foo: Annotated[str, Depends(foo)]):
            return "bar"

        def baz(bar: Annotated[str, Depends(bar)]):
            return "baz"

        diagraph = Diagraph(baz)

        node = diagraph[0]
        assert isinstance(node, tuple)
        assert node[0].fn == foo

        node = diagraph[2]
        assert isinstance(node, tuple)
        assert node[0].fn == baz

        node = diagraph[-1]
        assert isinstance(node, tuple)
        assert node[0].fn == baz

    def test_it_gets_back_a_tuple_for_parallels():
        def l0():
            return "foo"

        def l1_l(l0: Annotated[str, Depends(l0)]):
            return "bar"

        def l1_r(l0: Annotated[str, Depends(l0)]):
            return "baz"

        def l2(
            l1_l: Annotated[str, Depends(l1_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            return "qux"

        diagraph = Diagraph(l2)

        def check_tuple(key):
            nodes = diagraph[key]
            assert isinstance(nodes, tuple) and len(nodes) == 2
            return set([n.fn for n in nodes])

        assert check_tuple(1) == {l1_l, l1_r}
        assert check_tuple(-2) == {l1_l, l1_r}

    def test_it_gets_back_a_tuple_for_parallels_by_specifying_either_node_as_key():
        def l0():
            return "foo"

        def l1_l(l0: Annotated[str, Depends(l0)]):
            return "bar"

        def l1_r(l0: Annotated[str, Depends(l0)]):
            return "baz"

        def l2(
            l1_l: Annotated[str, Depends(l1_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            return "qux"

        diagraph = Diagraph(l2)

        assert diagraph[l1_l].fn == l1_l
        assert diagraph[l1_r].fn == l1_r

    def test_a_complicated_tree():
        def l0():
            pass

        def l1_l(l0: Annotated[str, Depends(l0)]):
            pass

        def l1_r(l0: Annotated[str, Depends(l0)]):
            pass

        def l2_l(
            l1_l: Annotated[str, Depends(l1_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            pass

        def l2_r(l1_r: Annotated[str, Depends(l1_r)]):
            pass

        def l3_l(
            l2_l: Annotated[str, Depends(l2_l)],
            l1_r: Annotated[str, Depends(l1_r)],
            l0: Annotated[str, Depends(l0)],
        ):
            pass

        def l4(
            l3_l: Annotated[str, Depends(l3_l)],
            l1_r: Annotated[str, Depends(l1_r)],
            l2_r: Annotated[str, Depends(l2_r)],
        ):
            pass

        diagraph = Diagraph(l4)

        # assert diagraph.dg.nodes()

        def check_node(key):
            node = diagraph[key]
            assert node is not None
            assert isinstance(node, DiagraphNode)
            return node.fn

        def check_tuple(key):
            nodes = diagraph[key]
            assert nodes is not None
            assert isinstance(nodes, tuple)
            return tuple([n.fn for n in nodes])

        for node in [l0, l1_l, l1_r, l2_l, l2_r, l3_l, l4]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (4, (l4,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)

        for index, nodes in [
            (-5, (l0,)),
            (-4, (l1_l, l1_r)),
            (-3, (l2_l, l2_r)),
            (-2, (l3_l,)),
            (-1, (l4,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)

    def test_a_complicated_tree_with_multiple_terminal_points():
        def l0():
            pass

        def l1_l(l0: Annotated[str, Depends(l0)]):
            pass

        def l1_r(l0: Annotated[str, Depends(l0)]):
            pass

        def l2_l(l1_l: Annotated[str, Depends(l1_l)]):
            pass

        def l2_r(l1_r: Annotated[str, Depends(l1_r)]):
            pass

        def l3_l(
            l2_l: Annotated[str, Depends(l2_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            pass

        diagraph = Diagraph(l3_l, l2_r)

        def check_node(key):
            node = diagraph[key]
            assert node is not None
            assert isinstance(node, DiagraphNode)
            return node.fn

        def check_tuple(key):
            nodes = diagraph[key]
            assert nodes is not None
            assert isinstance(nodes, tuple)
            return tuple([n.fn for n in nodes])

        for node in [l0, l1_l, l1_r, l2_l, l3_l, l2_r]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)

        for index, nodes in [
            (-4, (l0,)),
            (-3, (l1_l, l1_r)),
            (-2, (l2_l, l2_r)),
            (-1, (l3_l,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)

    def test_a_complicated_tree_with_multiple_origin_points():
        def l0_l():
            pass

        def l0_r():
            pass

        def l1_l(l0_l: Annotated[str, Depends(l0_l)]):
            pass

        def l1_r(l0_r: Annotated[str, Depends(l0_r)]):
            pass

        def l2(
            l1_l: Annotated[str, Depends(l1_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            pass

        diagraph = Diagraph(l2)

        def check_node(key):
            node = diagraph[key]
            assert node is not None
            assert isinstance(node, DiagraphNode)
            return node.fn

        def check_tuple(key):
            nodes = diagraph[key]
            assert nodes is not None
            assert isinstance(nodes, tuple)
            return tuple([n.fn for n in nodes])

        for node in [l0_l, l0_r, l1_l, l1_r, l2]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0_l, l0_r)),
            (1, (l1_l, l1_r)),
            (2, (l2,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)

        for index, nodes in [
            (-3, (l0_l, l0_r)),
            (-2, (l1_l, l1_r)),
            (-1, (l2,)),
        ]:
            assert set(check_tuple(index)) == set(nodes)


# def describe_slicing():
#     def test_it_can_slice():
#         def l0():
#             return "foo"

#         def l1(l0: Annotated[str, Depends(l0)]):
#             return "bar"

#         def l2(l1: Annotated[str, Depends(l1)]):
#             return "baz"

#         diagraph = Diagraph(l2)
#         sliced_diagraph = diagraph[1:2]

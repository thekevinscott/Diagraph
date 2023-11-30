from unittest.mock import patch

import pytest

from ..decorators.prompt import prompt
from ..llm.llm import LLM
from ..llm.openai_llm import OpenAI
from ..utils.depends import Depends
from .diagraph import Diagraph
from .diagraph_node import DiagraphNode
from .diagraph_node_group import DiagraphNodeGroup
from .types import Fn


def describe_instantiation():
    def test_it_instantiates_empty_diagraph():
        Diagraph()

    def test_it_instantiates_a_single_item_diagraph():
        def foo():
            return "foo"

        Diagraph(foo)


# def describe_nodes():
#     def test_it_gets_back_a_node_wrapper_for_a_function():
#         def foo():
#             return "foo"

#         diagraph = Diagraph(foo, use_string_keys=True)

#         node = diagraph["foo"]
#         assert isinstance(node, DiagraphNode)
#         assert node.fn == foo


def describe_indexing():
    def test_it_gets_back_a_node_wrapper_for_an_index():
        def foo():
            return "foo"

        def bar(foo: str = Depends(foo)):
            return "bar"

        def baz(bar: str = Depends(bar)):
            return "baz"

        diagraph = Diagraph(baz)

        assert isinstance(diagraph[0], DiagraphNodeGroup)
        assert diagraph[0][0].fn == foo
        assert isinstance(diagraph[2], DiagraphNodeGroup)
        assert diagraph[2][0].fn == baz
        assert isinstance(diagraph[-1], DiagraphNodeGroup)
        assert diagraph[-1][0].fn == baz

    def test_it_gets_back_a_tuple_for_parallels():
        def l0():
            return "foo"

        def l1_l(l0: str = Depends(l0)):
            return "bar"

        def l1_r(l0: str = Depends(l0)):
            return "baz"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return "qux"

        diagraph = Diagraph(l2)

        def check_tuple(key):
            nodes = diagraph[key]
            assert isinstance(nodes, DiagraphNodeGroup)
            assert len(nodes) == 2
            return set([n.fn for n in nodes])

        assert check_tuple(1) == {l1_l, l1_r}
        assert check_tuple(-2) == {l1_l, l1_r}

    def test_it_gets_back_a_tuple_for_parallels_by_specifying_either_node_as_key():
        def l0():
            return "foo"

        def l1_l(l0: str = Depends(l0)):
            return "bar"

        def l1_r(l0: str = Depends(l0)):
            return "baz"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return "qux"

        diagraph = Diagraph(l2)

        assert diagraph[l1_l].fn == l1_l
        assert diagraph[l1_r].fn == l1_r

    def test_a_complicated_tree():
        def l0():
            pass

        def l1_l(l0: str = Depends(l0)):
            pass

        def l1_r(l0: str = Depends(l0)):
            pass

        def l2_l(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            pass

        def l2_r(l1_r: str = Depends(l1_r)):
            pass

        def l3_l(
            l2_l: str = Depends(l2_l),
            l1_r: str = Depends(l1_r),
            l0: str = Depends(l0),
        ):
            pass

        def l4(
            l3_l: str = Depends(l3_l),
            l1_r: str = Depends(l1_r),
            l2_r: str = Depends(l2_r),
        ):
            pass

        diagraph = Diagraph(l4)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l2_r, l3_l, l4]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (4, (l4,)),
            (-5, (l0,)),
            (-4, (l1_l, l1_r)),
            (-3, (l2_l, l2_r)),
            (-2, (l3_l,)),
            (-1, (l4,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_a_complicated_tree_with_multiple_terminal_points():
        def l0():
            pass

        def l1_l(l0: str = Depends(l0)):
            pass

        def l1_r(l0: str = Depends(l0)):
            pass

        def l2_l(l1_l: str = Depends(l1_l)):
            pass

        def l2_r(l1_r: str = Depends(l1_r)):
            pass

        def l3_l(l2_l: str = Depends(l2_l), l1_r: str = Depends(l1_r)):
            pass

        diagraph = Diagraph(l3_l, l2_r)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l3_l, l2_r]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (-4, (l0,)),
            (-3, (l1_l, l1_r)),
            (-2, (l2_l, l2_r)),
            (-1, (l3_l,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_a_complicated_tree_with_multiple_origin_points():
        def l0_l():
            pass

        def l0_r():
            pass

        def l1_l(l0_l: str = Depends(l0_l)):
            pass

        def l1_r(l0_r: str = Depends(l0_r)):
            pass

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            pass

        diagraph = Diagraph(l2)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [l0_l, l0_r, l1_l, l1_r, l2]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (0, (l0_l, l0_r)),
            (1, (l1_l, l1_r)),
            (2, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

        for index, nodes in [
            (-3, (l0_l, l0_r)),
            (-2, (l1_l, l1_r)),
            (-1, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(diagraph, index)

    def test_it_can_index_into_a_triangle():
        def d0():
            pass

        def d1a(d0: str = Depends(d0)):
            pass

        def d1b(d0: str = Depends(d0)):
            pass

        diagraph = Diagraph(d1a, d1b)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0, d1a, d1b]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (d0,),
            ),
            (
                1,
                (
                    d1a,
                    d1b,
                ),
            ),
            (
                -2,
                (d0,),
            ),
            (
                -1,
                (
                    d1a,
                    d1b,
                ),
            ),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer

    def test_it_can_index_into_a_reverse_triangle():
        def d0a():
            pass

        def d0b():
            pass

        def d1(d0a: str = Depends(d0a), db0: str = Depends(d0b)):
            pass

        diagraph = Diagraph(d1)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0a, d0b, d1]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (
                    d0a,
                    d0b,
                ),
            ),
            (1, (d1,)),
            (
                -2,
                (
                    d0a,
                    d0b,
                ),
            ),
            (-1, (d1,)),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer

    def test_it_can_index_into_a_deep_reverse_triangle():
        def d0a():
            pass

        def d0b():
            pass

        def d1a(d0a: str = Depends(d0a)):
            pass

        def d1b(d0b: str = Depends(d0b)):
            pass

        def d2(d1a: str = Depends(d1a), d1b: str = Depends(d1b)):
            pass

        diagraph = Diagraph(d2)

        def check_node(diagraph, key):
            node = diagraph[key]
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(diagraph, key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphNodeGroup)
            return layer

        for node in [d0a, d0b, d1a, d1b, d2]:
            assert check_node(diagraph, node) == node

        for index, nodes in [
            (
                0,
                (
                    d0a,
                    d0b,
                ),
            ),
            (
                1,
                (
                    d1a,
                    d1b,
                ),
            ),
            (2, (d2,)),
            (
                -3,
                (
                    d0a,
                    d0b,
                ),
            ),
            (
                -2,
                (
                    d1a,
                    d1b,
                ),
            ),
            (-1, (d2,)),
        ]:
            layer = get_layer(diagraph, index)
            for node in nodes:
                assert node in layer


def describe_run():
    def test_it_can_run_a_single_fn(mocker):
        mock_instance = mocker.Mock()

        def d0():
            print("d0")
            return mock_instance()

        diagraph = Diagraph(d0)

        assert mock_instance.call_count == 0
        diagraph.run()
        assert mock_instance.call_count == 1

    def test_it_can_run_a_single_dependency(mocker):
        d0_mock = mocker.Mock()
        d0_mock.return_value = "d0"

        def d0():
            return d0_mock()

        d1_mock = mocker.Mock()
        d1_mock.return_value = "d1"

        def d1(d0: str = Depends(d0)):
            return d1_mock(d0)

        diagraph = Diagraph(d1)

        assert d0_mock.call_count == 0
        assert d1_mock.call_count == 0
        diagraph.run()
        assert d0_mock.call_count == 1
        assert d1_mock.call_count == 1
        d1_mock.assert_called_with(d0_mock.return_value)

    def test_it_can_run_two_dependencies(mocker):
        d0_mock = mocker.Mock()
        d0_mock.return_value = "d0"

        def d0():
            return d0_mock()

        d1_mock = mocker.Mock()
        d1_mock.return_value = "d1"

        def d1(d0: str = Depends(d0)):
            return d1_mock(d0)

        d2_mock = mocker.Mock()
        d2_mock.return_value = "d2"

        def d2(d1: str = Depends(d1)):
            return d2_mock(d1)

        diagraph = Diagraph(d2)

        assert d0_mock.call_count == 0
        assert d1_mock.call_count == 0
        assert d2_mock.call_count == 0
        diagraph.run()
        assert d0_mock.call_count == 1
        assert d1_mock.call_count == 1
        assert d2_mock.call_count == 1
        d1_mock.assert_called_with(d0_mock.return_value)
        d2_mock.assert_called_with(d1_mock.return_value)

    def describe_concurrency():
        @patch("time.sleep", return_value=None)
        def test_it_runs_functions_concurrently(patched_time_sleep):
            import time

            def a():
                time.sleep(999)
                return "a"

            def b():
                time.sleep(2)
                return "b"

            def c():
                return "c"

            assert Diagraph(a, b, c).run().result == ("a", "b", "c")
            assert patched_time_sleep.call_count == 2

        @patch("time.sleep", return_value=None)
        def test_it_runs_prompt_functions_concurrently(patched_time_sleep):
            import time

            class MockLLM(LLM):
                times: int
                error: bool

                def __init__(self, times=0, error=False, **kwargs):
                    self.times = times
                    self.kwargs = kwargs
                    self.error = error

                def run(self, prompt, log, model=None, stream=None, **kwargs):
                    response = ""
                    kwargs = {
                        **self.kwargs,
                        **kwargs,
                        "model": model,
                    }
                    response = ""
                    if self.error:
                        raise Exception("test error")
                    log("start", None)

                    for i in range(self.times):
                        i = f"{i}"
                        response += i
                        log("data", i)
                    log("end", None)
                    return response

            @prompt
            def a():
                time.sleep(1)
                return "a"

            @prompt
            def b():
                return "b"

            assert Diagraph(a, b, llm=MockLLM(times=3)).run().result == ("012", "012")

        @patch("time.sleep", return_value=None)
        def test_it_runs_prompt_with_argument_functions_concurrently(
            patched_time_sleep,
        ):
            import time

            class MockLLM(LLM):
                times: int
                error: bool

                def __init__(self, times=0, error=False, **kwargs):
                    self.times = times
                    self.kwargs = kwargs
                    self.error = error

                def run(self, prompt, log, model=None, stream=None, **kwargs):
                    response = ""
                    kwargs = {
                        **self.kwargs,
                        **kwargs,
                        "model": model,
                    }
                    response = ""
                    if self.error:
                        raise Exception("test error")
                    log("start", None)

                    for i in range(self.times):
                        i = f"{i}"
                        response += i
                        log("data", i)
                    log("end", None)
                    return response

            mock_llm_a = MockLLM(times=2)

            @prompt(log=None, llm=mock_llm_a)
            def a():
                time.sleep(999)
                return "a"

            @prompt(log=None, llm=mock_llm_a)
            def b():
                return "b"

            assert Diagraph(a, b).run().result == ("01", "01")

    def test_it_calls_functions_in_order():
        def l0():
            return "foo"

        def l1(l0: str = Depends(l0)):
            return f"{l0}bar"

        def l2(l1: str = Depends(l1)):
            return f"{l1}baz"

        assert Diagraph(l2).run().result == "foobarbaz"

    def test_it_can_get_results_for_non_prompt_functions():
        def l0():
            return "foo"

        def l1(l0: str = Depends(l0)):
            return f"{l0}bar"

        def l2(l1: str = Depends(l1)):
            return f"{l1}baz"

        diagraph = Diagraph(l2)
        assert diagraph.run().result == "foobarbaz"
        assert diagraph[0].result == "foo"
        assert diagraph[1].result == "foobar"
        assert diagraph[2].result == "foobarbaz"

    def describe_a_complicated_graph():
        @pytest.mark.parametrize(
            ("terminal_nodes", "assertions"),
            [
                (
                    "d3a",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2d",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2c",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 1),
                    ),
                ),
                (
                    "d2b",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d2a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1c",
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1b",
                    (
                        ("d0b", 1),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 1),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d1a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d0b",
                    (
                        ("d0b", 1),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 0),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    "d0a",
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 0),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d0a", "d1a"),
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 0),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d0a", "d1a", "d2a"),
                    (
                        ("d0b", 0),
                        ("d1c", 0),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 0),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 0),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2d"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 0),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d3a"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 0),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c", "d3a"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 0),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
                (
                    ("d2a", "d2b", "d2c", "d3a", "d1b"),
                    (
                        ("d0b", 1),
                        ("d1c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                    ),
                ),
            ],
        )
        def test_it_runs_the_whole_graph(mocker, terminal_nodes, assertions):
            d0a_mock = mocker.Mock(id="d0")
            d0a_mock.return_value = "d0"

            def d0a():
                return d0a_mock()

            d1a_mock = mocker.Mock(id="d1a")
            d1a_mock.return_value = "d1a"

            def d1a(d0a=Depends(d0a)):
                return d1a_mock()

            d0b_mock = mocker.Mock(id="d0b")
            d0b_mock.return_value = "d0b"

            def d0b():
                return d0b_mock()

            d1b_mock = mocker.Mock(id="d1b")
            d1b_mock.return_value = "d1b"

            def d1b(d0b=Depends(d0b)):
                return d1b_mock()

            d1c_mock = mocker.Mock(id="d1c")
            d1c_mock.return_value = "d1c"

            def d1c(d0b=Depends(d0b)):
                return d1c_mock()

            d2a_mock = mocker.Mock(id="d2a")
            d2a_mock.return_value = "d2a"

            def d2a(d1a=Depends(d1a)):
                return d2a_mock()

            d2b_mock = mocker.Mock(id="d2b")
            d2b_mock.return_value = "d2b"

            def d2b(d1a=Depends(d1a), d1c=Depends(d1c)):
                return d2b_mock()

            d2c_mock = mocker.Mock(id="d2c")
            d2c_mock.return_value = "d2c"

            def d2c(d1c=Depends(d1c)):
                return d2c_mock()

            d2d_mock = mocker.Mock(id="d2d")
            d2d_mock.return_value = "d2d"

            def d2d(d1c=Depends(d1c)):
                return d2d_mock()

            d3a_mock = mocker.Mock(id="d3a")
            d3a_mock.return_value = "d3a"

            def d3a(d2d=Depends(d2d)):
                return d3a_mock()

            mocks: dict[str, mocker.Mock] = {
                "d0b": d0b_mock,
                "d1c": d1c_mock,
                "d2d": d2d_mock,
                "d3a": d3a_mock,
                "d0a": d0a_mock,
                "d1a": d1a_mock,
                "d1b": d1b_mock,
                "d2a": d2a_mock,
                "d2b": d2b_mock,
                "d2c": d2c_mock,
            }

            nodes: dict[str, Fn] = {
                "d0b": d0b,
                "d1c": d1c,
                "d2d": d2d,
                "d3a": d3a,
                "d0a": d0a,
                "d1a": d1a,
                "d1b": d1b,
                "d2a": d2a,
                "d2b": d2b,
                "d2c": d2c,
            }

            for key, expectation in assertions:
                expectation = 0
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            if isinstance(terminal_nodes, tuple):
                terminal_nodes = tuple([nodes[node] for node in terminal_nodes])
            else:
                terminal_nodes = tuple([nodes[terminal_nodes]])

            Diagraph(*terminal_nodes).run()
            for key, expectation in assertions:
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

        @pytest.mark.parametrize(
            ("starting_nodes", "assertions"),
            [
                (
                    "d0a",
                    (
                        ("d0a", 2),
                        ("d0b", 1),
                        ("d1a", 2),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d0b",
                    (
                        ("d0a", 1),
                        ("d0b", 2),
                        ("d1a", 1),
                        ("d1b", 2),
                        ("d1c", 2),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 2),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d1a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 2),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d1b",
                    (
                        ("d0b", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 2),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d1c",
                    (
                        ("d0b", 1),
                        ("d0a", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 2),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 2),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d2a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 2),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2b",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 2),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2c",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 2),
                        ("d2d", 1),
                        ("d3a", 1),
                    ),
                ),
                (
                    "d2d",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 2),
                        ("d3a", 2),
                    ),
                ),
                (
                    "d3a",
                    (
                        ("d0a", 1),
                        ("d0b", 1),
                        ("d1a", 1),
                        ("d1b", 1),
                        ("d1c", 1),
                        ("d2a", 1),
                        ("d2b", 1),
                        ("d2c", 1),
                        ("d2d", 1),
                        ("d3a", 2),
                    ),
                ),
                # (
                #     ["d3a", "d2b"],
                #     (
                #         ("d0a", 1),
                #         ("d0b", 1),
                #         ("d1a", 1),
                #         ("d1b", 1),
                #         ("d1c", 1),
                #         ("d2a", 1),
                #         ("d2b", 2),
                #         ("d2c", 1),
                #         ("d2d", 1),
                #         ("d3a", 2),
                #     ),
                # ),
            ],
        )
        def test_it_runs_the_whole_graph_with_cached_data(
            mocker,
            starting_nodes,
            assertions,
        ):
            d0a_mock = mocker.Mock(id="d0")
            d0a_mock.return_value = "d0"

            def d0a():
                return d0a_mock()

            d1a_mock = mocker.Mock(id="d1a")
            d1a_mock.return_value = "d1a"

            def d1a(d0a=Depends(d0a)):
                return d1a_mock()

            d0b_mock = mocker.Mock(id="d0b")
            d0b_mock.return_value = "d0b"

            def d0b():
                return d0b_mock()

            d1b_mock = mocker.Mock(id="d1b")
            d1b_mock.return_value = "d1b"

            def d1b(d0b=Depends(d0b)):
                return d1b_mock()

            d1c_mock = mocker.Mock(id="d1c")
            d1c_mock.return_value = "d1c"

            def d1c(d0b=Depends(d0b)):
                return d1c_mock()

            d2a_mock = mocker.Mock(id="d2a")
            d2a_mock.return_value = "d2a"

            def d2a(d1a=Depends(d1a)):
                return d2a_mock()

            d2b_mock = mocker.Mock(id="d2b")
            d2b_mock.return_value = "d2b"

            def d2b(d1a=Depends(d1a), d1c=Depends(d1c)):
                return d2b_mock()

            d2c_mock = mocker.Mock(id="d2c")
            d2c_mock.return_value = "d2c"

            def d2c(d1c=Depends(d1c)):
                return d2c_mock()

            d2d_mock = mocker.Mock(id="d2d")
            d2d_mock.return_value = "d2d"

            def d2d(d1c=Depends(d1c)):
                return d2d_mock()

            d3a_mock = mocker.Mock(id="d3a")
            d3a_mock.return_value = "d3a"

            def d3a(d2d=Depends(d2d)):
                return d3a_mock()

            mocks: dict[str, mocker.Mock] = {
                "d0b": d0b_mock,
                "d1c": d1c_mock,
                "d2d": d2d_mock,
                "d3a": d3a_mock,
                "d0a": d0a_mock,
                "d1a": d1a_mock,
                "d1b": d1b_mock,
                "d2a": d2a_mock,
                "d2b": d2b_mock,
                "d2c": d2c_mock,
            }

            nodes: dict[str, Fn] = {
                "d0b": d0b,
                "d1c": d1c,
                "d2d": d2d,
                "d3a": d3a,
                "d0a": d0a,
                "d1a": d1a,
                "d1b": d1b,
                "d2a": d2a,
                "d2b": d2b,
                "d2c": d2c,
            }

            for key, _ in assertions:
                expectation = 0
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            dg = Diagraph(*tuple(nodes.values())).run()

            g = {}
            for key, val in dg.__graph__.graph_def.items():
                g[key.__name__] = [v.__name__ for v in val]
            print(g)

            for key, _ in assertions:
                expectation = 1
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e

            print("------ ")
            dg[nodes[starting_nodes]].run()
            print("------ post run, assert that all are as expected -----")

            for key, expectation in assertions:
                try:
                    assert mocks[key].call_count == expectation
                except Exception as e:
                    print(
                        f'for key "{key}": expected call count {expectation}, got {mocks[key].call_count}',
                    )
                    raise e


def describe_inputs():
    def test_it_calls_functions_in_a_diamond():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2(l1_l: str = Depends(l1_l), l1_r: str = Depends(l1_r)):
            return f"{l1_l}{l1_r}l2"

        assert Diagraph(l2).run().result == "l0l1_ll0l1_rl2"

    def test_it_calls_functions_in_a_wider_diamond():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_c(l0: str = Depends(l0)):
            return f"{l0}l1_c"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2(
            l1_l: str = Depends(l1_l),
            l1_c: str = Depends(l1_c),
            l1_r: str = Depends(l1_r),
        ):
            return f"{l1_l}{l1_c}{l1_r}l2"

        assert Diagraph(l2).run().result == "l0l1_ll0l1_cl0l1_rl2"

    def test_it_calls_functions_with_multiple_results():
        def l0():
            return "l0"

        def l1_l(l0: str = Depends(l0)):
            return f"{l0}l1_l"

        def l1_r(l0: str = Depends(l0)):
            return f"{l0}l1_r"

        def l2_l(l1_l: str = Depends(l1_l)):
            return f"{l1_l}l2_l"

        def l2_r(l1_r: str = Depends(l1_r)):
            return f"{l1_r}l2_r"

        result = Diagraph(l2_l, l2_r).run().result
        assert result is not None
        assert result[0] == "l0l1_ll2_l"
        assert result[1] == "l0l1_rl2_r"

    def test_it_calls_functions_with_multiple_inputs():
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: str = Depends(d0a)):
            return f"{i}d1a"

        def d1b(i: str = Depends(d0b)):
            return f"{i}d1b"

        def d2(a: str = Depends(d1a), b: str = Depends(d1b)):
            return f"{a}{b}d2"

        assert Diagraph(d2).run().result == "d0ad1ad0bd1bd2"

    def test_it_calls_functions_with_multiple_inputs_and_results():
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: str = Depends(d0a)):
            return f"{i}-d1a"

        def d1b(i: str = Depends(d0b)):
            return f"{i}-d1b"

        def d2(a: str = Depends(d1a), b: str = Depends(d1b)):
            return f"{a}-{b}-d2"

        def d3a(a: str = Depends(d2)):
            return f"{a}-d3a"

        def d3b(a: str = Depends(d2)):
            return f"{a}-d3b"

        result = Diagraph(d3a, d3b).run().result
        assert result is not None
        assert result[0] == "d0a-d1a-d0b-d1b-d2-d3a"
        assert result[1] == "d0a-d1a-d0b-d1b-d2-d3b"

    def test_it_passes_input():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(i: str = Depends(d0)):
            return f"{i}-d1a"

        def d1b(i: str = Depends(d0)):
            return f"{i}-d1b"

        def d2(i1: str = Depends(d1a), i2: str = Depends(d1b)):
            return f"{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_d0-d1a-foo_d0-d1b-d2"

    def test_it_passes_default_inputs():
        def d0(input: str = "foo"):
            return f"d0:{input}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run().result == "d1:d0:foo"

    def test_it_passes_multiple_default_inputs():
        def d0(foo: str = "foo", bar: str = "bar"):
            return f"d0:{foo}-{bar}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run().result == "d1:d0:foo-bar"

    def test_it_passes_mixed_default_and_non_inputs():
        def d0(foo: str, bar: str = "bar"):
            return f"d0:{foo}-{bar}"

        def d1(i0: str = Depends(d0)):
            return f"d1:{i0}"

        assert Diagraph(d1).run("baz").result == "d1:d0:baz-bar"

    def test_it_passes_input_to_each_fn():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1b"

        def d2(
            input: str,
            i1: str = Depends(d1a),
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_passes_input_at_end_of_args():
        def d0(input: str):
            return f"d0:{input}"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"d1a:{input}-{d0}"

        def d1b(
            d0: str = Depends(d0),
            input: str = "",
        ):
            return f"d1b:{input}-{d0}"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input}-{d1a}-{d1b}"

        dg = Diagraph(d2).run("foo")
        assert dg[d0].result == "d0:foo"
        assert dg[d1a].result == f"d1a:foo-{dg[d0].result}"
        assert dg[d1b].result == f"d1b:foo-{dg[d0].result}"
        assert dg[d2].result == f"d2:foo-{dg[d1a].result}-{dg[d1b].result}"
        assert dg.result == f"d2:foo-{dg[d1a].result}-{dg[d1b].result}"

    def describe_kwargs():
        def test_it_avoids_a_kwargs_complaint_when_using_default():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1).result
                == 'Inputs: "input1" "1" some-default'
            )

        def test_it_avoids_a_kwargs_complaint_when_passed_as_an_arg():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1, "foobar").result
                == 'Inputs: "input1" "1" foobar'
            )

        def test_it_avoids_a_kwargs_complaint_when_supplied_as_kwarg():
            def foo(input1: str, input2: int, keyword_arg="some-default"):
                return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

            assert (
                Diagraph(foo).run("input1", 1, keyword_arg="foobar").result
                == 'Inputs: "input1" "1" foobar'
            )

    def test_it_passes_input_mixed_all_over_the_args():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(
            i: str = Depends(d0),
            input: str = "",
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").result == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_ignores_excess_args():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: str = Depends(d0)):
            return f"{input}_{i}-d1a"

        def d1b(
            input: str,
            i: str = Depends(d0),
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert (
            Diagraph(d2).run("foo", "bar", "baz").result
            == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"
        )

    def test_it_passes_multiple_inputs():
        def d0(input_1: str):
            return f"{input_1}_d0"

        def d1a(input_1: str, i: str = Depends(d0), input_2: str = ""):
            return f"{input_1}_{i}-d1a_{input_2}"

        def d1b(
            i: str = Depends(d0),
            input_1: str = "",
        ):
            return f"{input_1}_{i}-d1b"

        def d2(
            i1: str = Depends(d1a),
            input_1: str = "",
            input_2: str = "",
            i2: str = Depends(d1b),
        ):
            return f"{input_1}_{i1}-{i2}-d2_{input_2}"

        assert (
            Diagraph(d2).run("foo", "bar").result
            == "foo_foo_foo_d0-d1a_bar-foo_foo_d0-d1b-d2_bar"
        )

    def test_it_passes_untyped_inputs():
        def d0(input1, input2: str, input3):
            return f"d0:{input1}+{input2}+{input3}"

        def d1a(input1, d0: str = Depends(d0), input2=""):
            return f"d1a:{input1}+{input2}+{d0}"

        def d1b(input1, d0: str = Depends(d0), input2="", input3=""):
            return f"d1b:{input1}+{input2}+{d0}"

        def d2(
            d1a: str = Depends(d1a),
            input1="",
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input1}+{d1a}+{d1b}"

        d0_result = "d0:foo+1+1.5"
        assert (
            Diagraph(d2).run("foo", 1, 1.5).result
            == f"d2:foo+d1a:foo+1+{d0_result}+d1b:foo+1+{d0_result}"
        )

    def test_it_passes_mixed_type_inputs():
        def join_list(input: list[int]):
            return "|".join([str(i) for i in input])

        def join_tuple(input: tuple):
            return ",".join(input)

        def d0(input1: str, input2: list[int], input3: tuple[str]):
            return f"d0:{input1}+{join_list(input2)}+{join_tuple(input3)}"

        def d1a(input1, d0: str = Depends(d0), input2=""):
            return f"d1a:{input1}+{join_list(input2)}+{d0}"

        def d1b(input1, d0: str = Depends(d0), _input2="", input3=""):
            return f"d1b:{input1}+{join_tuple(input3)}+{d0}"

        def d2(
            d1a: str = Depends(d1a),
            input1="",
            d1b: str = Depends(d1b),
        ):
            return f"d2:{input1}+{d1a}+{d1b}"

        arg2 = [1, 2, 3]
        arg3 = ("a", "b")

        d0_result = f"d0:foo+{join_list(arg2)}+{join_tuple(arg3)}"
        d1a_result = f"d1a:foo+{join_list(arg2)}+{d0_result}"
        d1b_result = f"d1b:foo+{join_tuple(arg3)}+{d0_result}"
        assert (
            Diagraph(d2).run("foo", arg2, arg3).result
            == f"d2:foo+{d1a_result}+{d1b_result}"
        )

    def test_it_passes_star_args():
        def d0(*args):
            args = "|".join(args)
            return f"d0:{args}"

        assert Diagraph(d0).run("foo", "bar", "baz").result == "d0:foo|bar|baz"

        def d1(*args, foo: str):
            args = "|".join(args)
            return f"d1:{args}"

        with pytest.raises(
            Exception,
            match="Errors encountered",
        ):
            dg = Diagraph(d1).run("foo", "bar", "baz")
            assert dg.result is None
            assert "Found arguments defined after * args" in str(dg[d1].error)

        def d2(foo, *args):
            args = "|".join(args)
            return f"d2:{foo}|{args}"

        assert Diagraph(d2).run("foo", "bar", "baz").result == "d2:foo|bar|baz"

        def d3(foo, bar, *args):
            return f"d3:{foo}|{args[0]}"

        assert Diagraph(d3).run("foo", "bar", "baz").result == "d3:foo|baz"

    def test_it_passes_starstar_kwargs():
        def d0(**kwargs):
            args = "|".join(kwargs.values())
            return f"d0:{args}"

        assert (
            Diagraph(d0).run(foo="foo", bar="bar", baz="baz").result == "d0:foo|bar|baz"
        )

    def describe_real_world_example():
        def test_it_raises_if_returning_non_from_a_prompt():
            def fake_run(self, string, stream=None, **kwargs):
                return string + "_"

            with patch.object(
                OpenAI,
                "run",
                fake_run,
            ):

                @prompt
                def fn():
                    return None

                with pytest.raises(
                    Exception,
                    match="Errors encountered",
                ):
                    dg = Diagraph(fn).run()
                    assert dg.result is None
                    assert "unsupported operand type(s) for +" in str(dg[fn].error)

        def test_it_does_a_real_world_example_with_prompt_fn():
            def fake_run(self, string, stream=None, **kwargs):
                return string + "_"

            with patch.object(
                OpenAI,
                "run",
                fake_run,
            ):

                @prompt
                def tell_me_a_joke():
                    return "joke"

                @prompt
                def explanation(joke: str = Depends(tell_me_a_joke)) -> str:
                    return f"{joke} explain"

                @prompt
                def improvement(
                    joke: str = Depends(tell_me_a_joke),
                    explanation: str = Depends(explanation),
                ) -> str:
                    return f"{joke} {explanation} improve"

                diagraph = Diagraph(improvement).run()
                assert diagraph.result == "joke_ joke_ explain_ improve_"
                assert diagraph[tell_me_a_joke].result == "joke_"
                assert diagraph[explanation].result == "joke_ explain_"
                assert diagraph[improvement].result == diagraph.result
                assert diagraph[0].result == "joke_"
                assert diagraph[1].result == "joke_ explain_"
                assert diagraph[2].result == diagraph.result
                assert diagraph[-3].result == "joke_"
                assert diagraph[-2].result == "joke_ explain_"
                assert diagraph[-1].result == diagraph.result
                assert diagraph[tell_me_a_joke].prompt == "joke"
                assert diagraph[explanation].prompt == "joke_ explain"
                assert diagraph[improvement].prompt == "joke_ joke_ explain_ improve"
                assert diagraph[0].prompt == "joke"
                assert diagraph[1].prompt == "joke_ explain"
                assert diagraph[2].prompt == "joke_ joke_ explain_ improve"
                assert diagraph[-3].prompt == "joke"
                assert diagraph[-2].prompt == "joke_ explain"
                assert diagraph[-1].prompt == "joke_ joke_ explain_ improve"


def describe_running_from_an_index():
    def test_it_throws_if_running_from_an_index_not_yet_run(mocker):
        def l0():
            return "l0"

        def l1(l0=Depends(l0)):
            return "l1"

        def l2(l1=Depends(l1)):
            return "l2"

        # some_mock=mocker.create_autospec(some)
        # some_mock(1)

        diagraph = Diagraph(l2)

        with pytest.raises(
            Exception,
            match="An ancestor is missing a result, run the traversal first",
        ):
            diagraph[l1].run("foobar")

    def test_it_runs_from_the_first_function_if_specified(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d0].run("foo")
        assert diagraph.result == "foo_foo_foo_d0-d1-d2"

    def test_it_runs_from_the_second_function_if_results_are_present(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1].run("bar")
        assert diagraph.result == "bar_bar_foo_d0-d1-d2"

    def test_it_runs_from_the_left_of_a_diamond(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
            input: str = "",
        ):
            return f"{d1a}*{d1b}*d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1a].run("bar")
        assert diagraph.result == "*".join(
            [
                "bar_foo_d0-d1a",
                "foo_foo_d0-d1b",
                "d2_bar",
            ],
        )

    def test_it_runs_from_the_first_index_if_provided(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            d1: str = Depends(d1),
            input: str = "",
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)
        diagraph[0].run("foo")
        assert diagraph.result == "foo_foo_foo_d0-d1-d2"


def describe_replay():
    def test_it_gets_result_from_a_node():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return f"{d1a}_{d1b}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        assert diagraph[d1a].result == "foo_foo_d0-d1a"

    def test_it_allows_execution_from_final_node_if_previous_result_is_explicitly_set():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(input: str, d1: str = Depends(d1)):
            return f"{d1}-d2-{input}"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.result == "newresult-d2-bar"

    def test_it_modifies_result():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.result == "bar_newresult-d2"

    def test_it_modifies_result_and_can_replay_in_a_diamond():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1b"

        def d2(
            input: str,
            d1a: str = Depends(d1a),
            d1b: str = Depends(d1b),
        ):
            return "*".join(
                [
                    d1a,
                    d1b,
                    "d2",
                    input,
                ],
            )

        diagraph = Diagraph(d2).run("foo")

        diagraph[d0].result = "newresult"

        diagraph[d1a].run("bar")

        assert diagraph.result == "*".join(
            [
                "bar_newresult-d1a",
                "foo_foo_d0-d1b",
                "d2",
                "bar",
            ],
        )

    def test_it_modifies_prompt_and_can_replay():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.result == "bar_newfnbar-d1-d2_bar"

    def test_it_modifies_prompt_and_can_replay_multiple_times():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: str = Depends(d0)):
            return f"{input}_{d0}-d1"

        def d2(
            input: str,
            d1: str = Depends(d1),
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.result == "bar_newfnbar-d1-d2_bar"

        def new_fn2(input: str):
            return f"newfn2{input}"

        diagraph[d0] = new_fn2

        assert diagraph.run("bar").result == "bar_newfn2bar-d1-d2_bar"


# def describe_slicing():
#     def test_it_can_slice():
#         def l0():
#             return "foo"

#         def l1(l0: str = Depends(l0)):
#             return "bar"

#         def l2(l1: str = Depends(l1)):
#             return "baz"

#         diagraph = Diagraph(l2)
#         sliced_diagraph = diagraph[1:2]


def describe_prompt():
    def test_it_calls_a_prompt():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0(input: str) -> str:
                return input

            input = "foo"
            diagraph = Diagraph(d0).run(input)
            assert diagraph[d0].prompt == f"{input}"
            assert diagraph[d0].result == f"{input}_"

    def test_it_raises_if_calling_prompt_on_non_decorated_function():
        def d0(input: str) -> str:
            return input

        input = "foo"
        diagraph = Diagraph(d0).run(input)
        prompt = None
        with pytest.raises(
            Exception,
            match="This function has not been decorated with @prompt",
        ):
            prompt = diagraph[d0].prompt
        assert prompt is None

    def test_it_calls_a_prompt_on_layer():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0(input: str) -> str:
                return input

            @prompt
            def d1a(d0: str = Depends(d0)) -> str:
                return f"d1a:{d0}"

            @prompt
            def d1b(d0: str = Depends(d0)) -> str:
                return f"d1b:{d0}"

            input = "foo"
            diagraph = Diagraph(d1a, d1b).run(input)
            assert diagraph[0].prompt == f"{input}"
            assert diagraph[0].result == f"{input}_"
            assert diagraph[1].prompt == (f"d1a:{input}_", f"d1b:{input}_")
            assert diagraph[1].result == (f"d1a:{input}__", f"d1b:{input}__")

    def test_it_calls_a_prompt_on_single_layer():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0a(input: str) -> str:
                return input

            @prompt
            def d0b(input: str) -> str:
                return input

            input = "foo"
            diagraph = Diagraph(d0a, d0b).run(input)
            assert diagraph[0].prompt == (f"{input}", f"{input}")
            assert diagraph[0].result == (f"{input}_", f"{input}_")

    def test_it_stores_non_string_responses_from_prompts():
        def fake_run(self, input, stream=None, **kwargs):
            return "foobar"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def fn_int():
                return 1

            @prompt
            def fn_float():
                return 1.5

            @prompt
            def fn_list():
                return [1, 2, 3]

            @prompt
            def fn_tuple():
                return (1, 2, 3)

            @prompt
            def fn_set():
                return {1, 2, 3}

            class MockClass:
                pass

            @prompt
            def fn_class():
                return MockClass

            mock_class = MockClass()

            @prompt
            def fn_class_instance():
                return mock_class

            diagraph = Diagraph(
                fn_int,
                fn_float,
                fn_list,
                fn_tuple,
                fn_set,
                fn_class,
                fn_class_instance,
            ).run()
            assert diagraph[fn_int].prompt == 1
            assert diagraph[fn_float].prompt == 1.5
            assert diagraph[fn_list].prompt == [1, 2, 3]
            assert diagraph[fn_tuple].prompt == (1, 2, 3)
            assert diagraph[fn_set].prompt == {1, 2, 3}
            assert diagraph[fn_class].prompt == MockClass
            assert diagraph[fn_class_instance].prompt == mock_class


def describe_tokens():
    def test_it_calls_tokens():
        def fake_run(self, string, stream=None, **kwargs):
            return string + "_"

        with patch.object(
            OpenAI,
            "run",
            fake_run,
        ):

            @prompt
            def d0(input: str) -> str:
                return input

            input = "foo bar"
            diagraph = Diagraph(d0).run(input)
            assert diagraph[d0].tokens == 2


def test_it_calls_tokens_on_layer():
    def fake_run(self, string, stream=None, **kwargs):
        return string + "_"

    with patch.object(
        OpenAI,
        "run",
        fake_run,
    ):

        @prompt
        def d0(input: str) -> str:
            return input

        @prompt
        def d1a(d0: str = Depends(d0)) -> str:
            return f"d1a {d0}"

        @prompt
        def d1b(d0: str = Depends(d0)) -> str:
            return f"d1b {d0}"

        input = "foo bar"
        print("1")
        diagraph = Diagraph(d1a, d1b).run(input)
        print("2")
        assert diagraph[0].tokens == 2
        assert diagraph[1].tokens == (6, 6)


def test_it_calls_tokens_on_single_layer():
    def fake_run(self, string, stream=None, **kwargs):
        return string + "_"

    with patch.object(
        OpenAI,
        "run",
        fake_run,
    ):

        @prompt
        def d0a(input: str) -> str:
            return input

        @prompt
        def d0b(input: str) -> str:
            return input

        input = "foo bar"
        diagraph = Diagraph(d0a, d0b).run(input)
        assert diagraph[0].tokens == (2, 2)


def describe_llm():
    class MockLLM(LLM):
        times: int
        error: bool

        def __init__(self, times=0, error=False, **kwargs):
            self.times = times
            self.kwargs = kwargs
            self.error = error

        def run(self, prompt, log, model=None, stream=None, **kwargs):
            response = ""
            kwargs = {
                **self.kwargs,
                **kwargs,
                "model": model,
            }
            response = ""
            if self.error:
                raise Exception("test error")
            log("start", None)

            for i in range(self.times):
                i = f"{i}"
                response += i
                log("data", i)
            log("end", None)
            return response

    def test_it_sets_a_function_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_sets_a_default_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=times))

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_sets_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=times)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_default_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=0)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_diagraph_and_global_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=0)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_overrides_a_global_llm_from_a_diagraph_llm(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_llm(MockLLM(times=0))

        @prompt()
        def fn():
            return "test prompt"

        Diagraph(fn, log=log, llm=MockLLM(times=times)).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

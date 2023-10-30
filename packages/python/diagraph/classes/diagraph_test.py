from typing import Annotated
import pytest

from .diagraph_layer import DiagraphLayer
from .diagraph import Diagraph
from .diagraph_node import DiagraphNode
from ..utils.depends import Depends
from ..decorators.prompt import prompt


def describe_instantiation():
    def test_it_instantiates_empty_diagraph():
        Diagraph()

    def test_it_instantiates_a_single_item_diagraph():
        def foo():
            return "foo"

        Diagraph(foo)


def describe_nodes():
    def test_it_gets_back_a_node_wrapper_for_a_function():
        def foo():
            return "foo"

        diagraph = Diagraph(foo, use_string_keys=True)

        node = diagraph["foo"]
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

        assert isinstance(diagraph[0], DiagraphLayer) and diagraph[0][0].fn == foo
        assert isinstance(diagraph[2], DiagraphLayer) and diagraph[2][0].fn == baz
        assert isinstance(diagraph[-1], DiagraphLayer) and diagraph[-1][0].fn == baz

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
            assert isinstance(nodes, DiagraphLayer) and len(nodes) == 2
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
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphLayer)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l2_r, l3_l, l4]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
            (4, (l4,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)

        for index, nodes in [
            (-5, (l0,)),
            (-4, (l1_l, l1_r)),
            (-3, (l2_l, l2_r)),
            (-2, (l3_l,)),
            (-1, (l4,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)

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
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphLayer)
            return layer

        for node in [l0, l1_l, l1_r, l2_l, l3_l, l2_r]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0,)),
            (1, (l1_l, l1_r)),
            (2, (l2_l, l2_r)),
            (3, (l3_l,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)

        for index, nodes in [
            (-4, (l0,)),
            (-3, (l1_l, l1_r)),
            (-2, (l2_l, l2_r)),
            (-1, (l3_l,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)

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
            assert isinstance(node, DiagraphNode)
            return node.fn

        def get_layer(key):
            layer = diagraph[key]
            assert isinstance(layer, DiagraphLayer)
            return layer

        for node in [l0_l, l0_r, l1_l, l1_r, l2]:
            assert check_node(node) == node

        for index, nodes in [
            (0, (l0_l, l0_r)),
            (1, (l1_l, l1_r)),
            (2, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)

        for index, nodes in [
            (-3, (l0_l, l0_r)),
            (-2, (l1_l, l1_r)),
            (-1, (l2,)),
        ]:
            for node in nodes:
                assert node in get_layer(index)


def describe_run():
    def test_it_can_run_a_single_fn(mocker):
        d0 = mocker.stub()
        d0.__name__ = "d0"

        diagraph = Diagraph(d0)

        assert d0.call_count == 0
        diagraph.run()
        assert d0.call_count == 1

    def test_it_can_run_a_single_dependency(mocker):
        l0 = mocker.stub()
        l0.return_value = "l0"
        l1 = mocker.stub()
        l1.return_value = "l1"
        l1.__annotations__ = {"l0": Annotated[str, Depends(l0)]}

        diagraph = Diagraph(l1)

        assert l0.call_count == 0
        assert l1.call_count == 0
        diagraph.run()
        assert l0.call_count == 1
        assert l1.call_count == 1
        l1.assert_called_with(l0.return_value)

    def test_it_can_run_two_dependencies(mocker):
        l0 = mocker.stub()
        l0.return_value = "l0"
        l1 = mocker.stub()
        l1.return_value = "l1"
        l2 = mocker.stub()
        l2.return_value = "l2"
        l1.__annotations__ = {"l0": Annotated[str, Depends(l0)]}
        l2.__annotations__ = {"l1": Annotated[str, Depends(l1)]}

        diagraph = Diagraph(l2)

        assert l0.call_count == 0
        assert l1.call_count == 0
        assert l2.call_count == 0
        diagraph.run()
        assert l0.call_count == 1
        assert l1.call_count == 1
        assert l2.call_count == 1
        l1.assert_called_with(l0.return_value)
        l2.assert_called_with(l1.return_value)

    def test_it_calls_functions_in_order(mocker):
        def l0():
            return "foo"

        def l1(l0: Annotated[str, Depends(l0)]):
            return f"{l0}bar"

        def l2(l1: Annotated[str, Depends(l1)]):
            return f"{l1}baz"

        assert Diagraph(l2).run().output == "foobarbaz"


def describe_inputs():
    def test_it_calls_functions_in_a_diamond(mocker):
        def l0():
            return "l0"

        def l1_l(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_l"

        def l1_r(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_r"

        def l2(
            l1_l: Annotated[str, Depends(l1_l)], l1_r: Annotated[str, Depends(l1_r)]
        ):
            return f"{l1_l}{l1_r}l2"

        assert Diagraph(l2).run().output == "l0l1_ll0l1_rl2"

    def test_it_calls_functions_in_a_wider_diamond(mocker):
        def l0():
            return "l0"

        def l1_l(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_l"

        def l1_c(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_c"

        def l1_r(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_r"

        def l2(
            l1_l: Annotated[str, Depends(l1_l)],
            l1_c: Annotated[str, Depends(l1_c)],
            l1_r: Annotated[str, Depends(l1_r)],
        ):
            return f"{l1_l}{l1_c}{l1_r}l2"

        assert Diagraph(l2).run().output == "l0l1_ll0l1_cl0l1_rl2"

    def test_it_calls_functions_with_multiple_outputs(mocker):
        def l0():
            return "l0"

        def l1_l(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_l"

        def l1_r(l0: Annotated[str, Depends(l0)]):
            return f"{l0}l1_r"

        def l2_l(l1_l: Annotated[str, Depends(l1_l)]):
            return f"{l1_l}l2_l"

        def l2_r(l1_r: Annotated[str, Depends(l1_r)]):
            return f"{l1_r}l2_r"

        output = Diagraph(l2_l, l2_r).run().output
        assert output is not None
        assert output[0] == "l0l1_ll2_l"
        assert output[1] == "l0l1_rl2_r"

    def test_it_calls_functions_with_multiple_inputs(mocker):
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: Annotated[str, Depends(d0a)]):
            return f"{i}d1a"

        def d1b(i: Annotated[str, Depends(d0b)]):
            return f"{i}d1b"

        def d2(a: Annotated[str, Depends(d1a)], b: Annotated[str, Depends(d1b)]):
            return f"{a}{b}d2"

        assert Diagraph(d2).run().output == "d0ad1ad0bd1bd2"

    def test_it_calls_functions_with_multiple_inputs_and_outputs(mocker):
        def d0a():
            return "d0a"

        def d0b():
            return "d0b"

        def d1a(i: Annotated[str, Depends(d0a)]):
            return f"{i}-d1a"

        def d1b(i: Annotated[str, Depends(d0b)]):
            return f"{i}-d1b"

        def d2(a: Annotated[str, Depends(d1a)], b: Annotated[str, Depends(d1b)]):
            return f"{a}-{b}-d2"

        def d3a(a: Annotated[str, Depends(d2)]):
            return f"{a}-d3a"

        def d3b(a: Annotated[str, Depends(d2)]):
            return f"{a}-d3b"

        output = Diagraph(d3a, d3b).run().output
        assert output is not None
        assert output[0] == "d0a-d1a-d0b-d1b-d2-d3a"
        assert output[1] == "d0a-d1a-d0b-d1b-d2-d3b"

    def test_it_passes_input(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(i: Annotated[str, Depends(d0)]):
            return f"{i}-d1a"

        def d1b(i: Annotated[str, Depends(d0)]):
            return f"{i}-d1b"

        def d2(i1: Annotated[str, Depends(d1a)], i2: Annotated[str, Depends(d1b)]):
            return f"{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").output == "foo_d0-d1a-foo_d0-d1b-d2"

    def test_it_passes_input_to_each_fn(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: Annotated[str, Depends(d0)]):
            return f"{input}_{i}-d1a"

        def d1b(input: str, i: Annotated[str, Depends(d0)]):
            return f"{input}_{i}-d1b"

        def d2(
            input: str,
            i1: Annotated[str, Depends(d1a)],
            i2: Annotated[str, Depends(d1b)],
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_passes_input_at_end_of_args(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(i: Annotated[str, Depends(d0)], input: str):
            return f"{input}_{i}-d1a"

        def d1b(
            i: Annotated[str, Depends(d0)],
            input: str,
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: Annotated[str, Depends(d1a)],
            i2: Annotated[str, Depends(d1b)],
            input: str,
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_passes_input_mixed_all_over_the_args(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: Annotated[str, Depends(d0)]):
            return f"{input}_{i}-d1a"

        def d1b(
            i: Annotated[str, Depends(d0)],
            input: str,
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: Annotated[str, Depends(d1a)],
            input: str,
            i2: Annotated[str, Depends(d1b)],
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert Diagraph(d2).run("foo").output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

    def test_it_ignores_excess_args(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, i: Annotated[str, Depends(d0)]):
            return f"{input}_{i}-d1a"

        def d1b(
            i: Annotated[str, Depends(d0)],
            input: str,
        ):
            return f"{input}_{i}-d1b"

        def d2(
            i1: Annotated[str, Depends(d1a)],
            input: str,
            i2: Annotated[str, Depends(d1b)],
        ):
            return f"{input}_{i1}-{i2}-d2"

        assert (
            Diagraph(d2).run("foo", "bar", "baz").output
            == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"
        )

    def test_it_passes_multiple_inputs(mocker):
        def d0(input_1: str):
            return f"{input_1}_d0"

        def d1a(input_1: str, i: Annotated[str, Depends(d0)], input_2: str):
            return f"{input_1}_{i}-d1a_{input_2}"

        def d1b(
            i: Annotated[str, Depends(d0)],
            input_1: str,
        ):
            return f"{input_1}_{i}-d1b"

        def d2(
            i1: Annotated[str, Depends(d1a)],
            input_1: str,
            input_2: str,
            i2: Annotated[str, Depends(d1b)],
        ):
            return f"{input_1}_{i1}-{i2}-d2_{input_2}"

        assert (
            Diagraph(d2).run("foo", "bar").output
            == "foo_foo_foo_d0-d1a_bar-foo_foo_d0-d1b-d2_bar"
        )

    def test_it_does_a_real_world_example(mocker):
        class MockLLM:
            def run(self, string, log, stream=None, **kwargs):
                return string

        @prompt(llm=MockLLM())
        def tell_me_a_joke():
            return "joke"

        @prompt(llm=MockLLM())
        def explanation(joke: Annotated[str, Depends(tell_me_a_joke)]) -> str:
            return f"{joke} explain"

        @prompt(llm=MockLLM())
        def improvement(
            joke: Annotated[str, Depends(tell_me_a_joke)],
            explanation: Annotated[str, Depends(explanation)],
        ) -> str:
            return f"{joke} {explanation} improve"

        assert Diagraph(improvement).run().output == "joke joke explain improve"


def describe_running_from_an_index():
    def test_it_throws_if_running_from_an_index_not_yet_run(mocker):
        l0 = mocker.stub()
        l0.return_value = "l0"
        l1 = mocker.stub()
        l1.return_value = "l1"
        l2 = mocker.stub()
        l2.return_value = "l2"
        l1.__annotations__ = {"l0": Annotated[str, Depends(l0)]}
        l2.__annotations__ = {"l1": Annotated[str, Depends(l1)]}

        with pytest.raises(Exception):
            diagraph = Diagraph(l2)
            diagraph[l1].run("foobar")

    def test_it_runs_from_the_first_function_if_specified(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d0].run("foo")
        assert diagraph.output == "foo_foo_foo_d0-d1-d2"

    def test_it_runs_from_the_second_function_if_results_are_present(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1].run("bar")
        assert diagraph.output == "bar_bar_foo_d0-d1-d2"

    def test_it_runs_from_the_left_of_a_diamond(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1b"

        def d2(
            d1a: Annotated[str, Depends(d1a)],
            d1b: Annotated[str, Depends(d1b)],
            input: str,
        ):
            return f"{d1a}_{d1b}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        diagraph[d1a].run("bar")
        assert diagraph.output == "bar_foo_d0-d1a_foo_foo_d0-d1b-d2_bar"

    def test_it_runs_from_the_first_index_if_provided(mocker):
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)
        diagraph[0].run("foo")
        assert diagraph.output == "foo_foo_foo_d0-d1-d2"


def describe_replay():
    def test_it_gets_result_from_a_node():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1b"

        def d2(
            d1a: Annotated[str, Depends(d1a)],
            d1b: Annotated[str, Depends(d1b)],
            input: str,
        ):
            return f"{d1a}_{d1b}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        assert diagraph[d1a].result == "foo_foo_d0-d1a"

    def test_it_allows_execution_from_final_node_if_previous_result_is_explicitly_set():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(d1: Annotated[str, Depends(d1)], input: str):
            return f"{d1}-d2-{input}"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.output == "newresult-d2-bar"

    def test_it_modifies_result():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{input}_{d1}-d2"

        diagraph = Diagraph(d2)

        diagraph[d1].result = "newresult"

        diagraph[d2].run("bar")
        assert diagraph.output == "bar_newresult-d2"

    def test_it_modifies_result_and_can_replay_in_a_diamond():
        def d0(input: str):
            return f"{input}_d0"

        def d1a(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1a"

        def d1b(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1b"

        def d2(
            d1a: Annotated[str, Depends(d1a)],
            d1b: Annotated[str, Depends(d1b)],
            input: str,
        ):
            return "*".join(
                [
                    d1a,
                    d1b,
                    "d2",
                    input,
                ]
            )

        diagraph = Diagraph(d2).run("foo")

        diagraph[d0].result = "newresult"

        diagraph[d1a].run("bar")

        assert diagraph.output == "*".join(
            [
                "bar_newresult-d1a",
                "foo_foo_d0-d1b",
                "d2",
                "bar",
            ]
        )

    def test_it_modifies_prompt_and_can_replay():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.output == "bar_newfnbar-d1-d2_bar"

    def test_it_modifies_prompt_and_can_replay_multiple_times():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(
            d1: Annotated[str, Depends(d1)],
            input: str,
        ):
            return f"{d1}-d2_{input}"

        diagraph = Diagraph(d2).run("foo")

        def new_fn(input: str):
            return f"newfn{input}"

        diagraph[d0] = new_fn

        diagraph.run("bar")
        assert diagraph.output == "bar_newfnbar-d1-d2_bar"

        def new_fn2(input: str):
            return f"newfn2{input}"

        diagraph[d0] = new_fn2

        assert diagraph.run("bar").output == "bar_newfn2bar-d1-d2_bar"


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

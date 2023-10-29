from typing import Annotated
import pytest
from .diagraph import Diagraph
from .diagraph_traversal import DiagraphTraversal, validate_node_ancestors
from ..utils.depends import Depends


def describe_run():
    def test_it_can_run_a_single_fn(mocker):
        d0 = mocker.stub()

        diagraph = Diagraph(d0)
        traversal = DiagraphTraversal(diagraph)

        assert d0.call_count == 0
        traversal.run()
        assert d0.call_count == 1

    def test_it_can_run_a_single_dependency(mocker):
        l0 = mocker.stub()
        l0.return_value = "l0"
        l1 = mocker.stub()
        l1.return_value = "l1"
        l1.__annotations__ = {"l0": Annotated[str, Depends(l0)]}

        diagraph = Diagraph(l1)

        traversal = DiagraphTraversal(diagraph)

        assert l0.call_count == 0
        assert l1.call_count == 0
        traversal.run()
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

        traversal = DiagraphTraversal(diagraph)

        assert l0.call_count == 0
        assert l1.call_count == 0
        assert l2.call_count == 0
        traversal.run()
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

        diagraph = Diagraph(l2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        assert traversal.output == "foobarbaz"


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

        diagraph = Diagraph(l2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        assert traversal.output == "l0l1_ll0l1_rl2"

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

        diagraph = Diagraph(l2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        assert traversal.output == "l0l1_ll0l1_cl0l1_rl2"

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

        diagraph = Diagraph(l2_l, l2_r)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        output = traversal.output
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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        output = traversal.output
        assert output == "d0ad1ad0bd1bd2"

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

        diagraph = Diagraph(d3a, d3b)

        traversal = DiagraphTraversal(diagraph)

        traversal.run()
        output = traversal.output
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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo")
        assert traversal.output == "foo_d0-d1a-foo_d0-d1b-d2"

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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo")
        assert traversal.output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo")
        assert traversal.output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo")
        assert traversal.output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo", "bar", "baz")
        assert traversal.output == "foo_foo_foo_d0-d1a-foo_foo_d0-d1b-d2"

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

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal.run("foo", "bar")
        assert traversal.output == "foo_foo_foo_d0-d1a_bar-foo_foo_d0-d1b-d2_bar"


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

        diagraph = Diagraph(l2)

        traversal = DiagraphTraversal(diagraph)

        with pytest.raises(Exception):
            traversal[l1].run("foobar")

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

        traversal = DiagraphTraversal(diagraph)
        traversal[d0].run("foo")
        assert traversal.output == "foo_foo_foo_d0-d1-d2"

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

        traversal = Diagraph(d2).run("foo")

        traversal[d1].run("bar")
        assert traversal.output == "bar_bar_foo_d0-d1-d2"

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

        traversal = Diagraph(d2).run("foo")

        traversal[d1a].run("bar")
        assert traversal.output == "bar_foo_d0-d1a_foo_foo_d0-d1b-d2_bar"

    # def test_it_runs_from_the_first_index_if_provided(mocker):
    #     def d0(input: str):
    #         return f"{input}_d0"

    #     def d1(input: str, d0: Annotated[str, Depends(d0)]):
    #         return f"{input}_{d0}-d1"

    #     def d2(
    #         d1: Annotated[str, Depends(d1)],
    #         input: str,
    #     ):
    #         return f"{input}_{d1}-d2"

    #     diagraph = Diagraph(d2)

    #     traversal = DiagraphTraversal(diagraph)
    #     traversal[0].run("foo")
    #     assert traversal.output == "foo_foo_foo_d0-d1-d2"


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

        traversal = Diagraph(d2).run("foo")

        assert traversal[d1a].result == "foo_foo_d0-d1a"

    def test_it_allows_execution_from_final_node_if_previous_result_is_explicitly_set():
        def d0(input: str):
            return f"{input}_d0"

        def d1(input: str, d0: Annotated[str, Depends(d0)]):
            return f"{input}_{d0}-d1"

        def d2(d1: Annotated[str, Depends(d1)], input: str):
            return f"{d1}-d2-{input}"

        diagraph = Diagraph(d2)

        traversal = DiagraphTraversal(diagraph)

        traversal[d1].result = "newresult"

        traversal[d2].run("bar")
        assert traversal.output == "newresult-d2-bar"

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

        traversal = DiagraphTraversal(diagraph)

        traversal[d1].result = "newresult"

        traversal[d2].run("bar")
        assert traversal.output == "bar_newresult-d2"

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

        traversal = Diagraph(d2).run("foo")

        traversal[d0].result = "newresult"

        traversal[d1a].run("bar")

        assert traversal.output == "*".join(
            [
                "bar_newresult-d1a",
                "foo_foo_d0-d1b",
                "d2",
                "bar",
            ]
        )

    # def test_it_modifies_prompt_and_can_replay():
    #     def d0(input: str):
    #         return f"{input}_d0"

    #     def d1(input: str, d0: Annotated[str, Depends(d0)]):
    #         return f"{input}_{d0}-d1"

    #     def d2(
    #         d1: Annotated[str, Depends(d1)],
    #         input: str,
    #     ):
    #         return f"{d1}-d2_{input}"

    #     traversal = Diagraph(d2).run("foo")

    #     def new_fn(input: str):
    #         return f"newfn{input}"

    #     traversal[d0] = new_fn

    #     traversal.run("bar")
    #     assert traversal.output == "bar_newfnbar-d1-d2_bar"

    # def test_it_modifies_prompt_and_can_replay_multiple_times():
    #     def d0(input: str):
    #         return f"{input}_d0"

    #     def d1(input: str, d0: Annotated[str, Depends(d0)]):
    #         return f"{input}_{d0}-d1"

    #     def d2(
    #         d1: Annotated[str, Depends(d1)],
    #         input: str,
    #     ):
    #         return f"{d1}-d2_{input}"

    #     traversal = Diagraph(d2).run("foo")

    #     def new_fn(input: str):
    #         return f"newfn{input}"

    #     traversal[d0] = new_fn

    #     traversal.run("bar")
    #     assert traversal.output == "bar_newfnbar-d1-d2_bar"

    #     def new_fn2(input: str):
    #         return f"newfn2{input}"

    #     # traversal[new_fn] = new_fn2
    #     traversal[d0] = new_fn2

    #     traversal.run("bar")
    #     assert traversal.output == "bar_newfn2bar-d1-d2_bar"

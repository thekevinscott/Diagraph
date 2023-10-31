from typing import Annotated
from .build_graph import build_graph
from .depends import Depends


def test_returns_an_empty_graph():
    assert build_graph() == {}


def test_returns_a_single_node_graph_and_ignores_return_key():
    def foo() -> str:
        return "foo"

    assert build_graph(foo) == {foo: set()}


def test_works_with_a_stub(mocker):
    mock_instance = mocker.Mock()

    def stub():
        return mock_instance()

    assert build_graph(stub) == {stub: set()}


def test_returns_a_linear_graph():
    def foo():
        return "foo"

    def bar(foo_arg: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo_arg}"

    assert build_graph(bar) == {foo: set(), bar: {foo}}


def test_returns_a_multistep_linear_graph():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(bar: Annotated[str, Depends(bar)]) -> str:
        return f"baz: {bar}"

    assert build_graph(baz) == {foo: set(), bar: {foo}, baz: {bar}}


def test_returns_an_interconnected_graph():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        foo: Annotated[str, Depends(foo)], bar: Annotated[str, Depends(bar)]
    ) -> str:
        return f"baz: {foo} {bar}"

    assert build_graph(baz) == {foo: set(), bar: {foo}, baz: {foo, bar}}


def test_returns_a_very_interconnected_graph():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        foo: Annotated[str, Depends(foo)], bar: Annotated[str, Depends(bar)]
    ) -> str:
        return f"baz: {foo} {bar}"

    def qux(
        foo: Annotated[str, Depends(foo)], baz: Annotated[str, Depends(baz)]
    ) -> str:
        return f"qux: {foo} {baz}"

    assert build_graph(qux) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
        qux: {foo, baz},
    }


def test_handles_multiple_node_args():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        foo: Annotated[str, Depends(foo)], bar: Annotated[str, Depends(bar)]
    ) -> str:
        return f"baz: {foo} {bar}"

    def qux(
        foo: Annotated[str, Depends(foo)], bar: Annotated[str, Depends(bar)]
    ) -> str:
        return f"qux: {foo} {bar}"

    assert build_graph(baz, qux) == {
        foo: set(),
        bar: {foo},
        baz: {foo, bar},
        qux: {foo, bar},
    }


def test_ignores_message_order():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        bar: Annotated[str, Depends(bar)], foo: Annotated[str, Depends(foo)]
    ) -> str:
        return f"baz: {foo} {bar}"

    assert build_graph(baz) == {foo: set(), bar: {foo}, baz: {foo, bar}}


def test_it_handles_strings_at_beginning():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        string_arg: str,
        bar: Annotated[str, Depends(bar)],
        foo: Annotated[str, Depends(foo)],
    ) -> str:
        return f"baz: {string_arg} {foo} {bar}"

    assert build_graph(baz) == {foo: set(), bar: {foo}, baz: {foo, bar}}


def test_it_handles_strings_at_end():
    def foo():
        return "foo"

    def bar(foo: Annotated[str, Depends(foo)]) -> str:
        return f"bar: {foo}"

    def baz(
        bar: Annotated[str, Depends(bar)],
        foo: Annotated[str, Depends(foo)],
        string_arg: str,
    ) -> str:
        return f"baz: {string_arg} {foo} {bar}"

    assert build_graph(baz) == {foo: set(), bar: {foo}, baz: {foo, bar}}

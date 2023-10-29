from typing import Annotated

from .depends import Depends

from .annotations import get_annotations, get_dependency, is_annotated


def describe_is_annotated():
    def test_it_returns_true_if_annotation():
        assert is_annotated(Annotated[int, "test"]) is True

    def test_it_returns_false_if_not_annotation():
        assert is_annotated("hi") is False


def describe_get_annotations():
    def test_it_gets_annotations():
        def fn(a: Annotated[int, "a"], b: Annotated[str, "b"]):
            return a

        assert list(get_annotations(fn)) == [
            ("a", Annotated[int, "a"]),
            ("b", Annotated[str, "b"]),
        ]


def describe_get_dependency():
    def test_it_gets_dependency():
        def foo():
            return "foo"

        assert get_dependency(Annotated[str, Depends(foo)]) == foo

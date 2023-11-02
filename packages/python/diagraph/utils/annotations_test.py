from typing import Annotated

from .depends import Depends

from .annotations import get_dependencies, get_dependency, is_annotated


def describe_is_annotated():
    def test_it_returns_true_if_annotation():
        assert is_annotated(Annotated[int, "test"]) is True

    def test_it_returns_false_if_not_annotation():
        assert is_annotated("hi") is False


def describe_get_dependencies():
    def test_it_gets_dependencies():
        def fn(a: Annotated[int, Depends(1)], b: Annotated[str, Depends("b")]):
            return a

        dependencies = [d.dependency for d in list(get_dependencies(fn))]
        assert dependencies== [
                1,'b',
        ]


    def test_it_gets_dependencies_with_default_syntax():
        def fn(a: int = Depends(1), b: str = Depends("b")):
            return a

        dependencies = [d.dependency for d in list(get_dependencies(fn))]
        assert dependencies== [
                1,'b',
        ]


def describe_get_dependency():
    def test_it_gets_dependency():
        def foo():
            return "foo"

        assert get_dependency(Annotated[str, Depends(foo)]) == foo

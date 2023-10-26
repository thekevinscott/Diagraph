from .depends import Depends

# def test_returns_an_empty_graph():
# assert build_graph() == {}


def test_depends_gets_dependency():
    def foo():
        return "foo"

    d = Depends(foo)

    assert d.dependency == foo


def test_depends_defines_repr():
    def foo():
        return "foo"

    d = Depends(foo)

    assert str(d) == "Depends(foo)"

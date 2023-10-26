import inspect
from .diagraph import Diagraph
from .diagraph_node import DiagraphNode
from ..utils.depends import Depends
from ..decorators import prompt


# def test_it_instantiates_empty_diagraph():
#     diagraph = Diagraph()


# def test_it_instantiates_a_single_item_diagraph():
#     def foo():
#         return "foo"

#     diagraph = Diagraph(foo)


# def test_it_gets_back_a_node_wrapper_for_a_function():
#     def foo():
#         return "foo"

#     diagraph = Diagraph(foo)

#     node = diagraph[foo]
#     assert node is not None
#     assert isinstance(node, DiagraphNode)
#     assert node.__fn__ == foo


# def test_it_gets_back_a_string_representation_of_a_node():
#     def foo():
#         return "foo"

#     diagraph = Diagraph(foo)

#     node = diagraph[foo]
#     assert node is not None
#     assert isinstance(node, DiagraphNode)
#     assert str(node) == inspect.getsource(foo)


# def test_it_gets_back_a_node_wrapper_for_an_index():
#     def foo():
#         return "foo"

#     def bar(foo: Depends(foo)):
#         return "bar"

#     def baz(bar: Depends(bar)):
#         return "baz"

#     diagraph = Diagraph(baz)

#     node = diagraph[0]
#     assert node is not None
#     assert isinstance(node, DiagraphNode)
#     assert node.__fn__ == foo

#     node = diagraph[2]
#     assert node is not None
#     assert isinstance(node, DiagraphNode)
#     assert node.__fn__ == baz

#     node = diagraph[-1]
#     assert node is not None
#     assert isinstance(node, DiagraphNode)
#     assert node.__fn__ == baz


# # def test_it_gets_back_a_tuple_for_parallels():
# #     def foo():
# #         return "foo"

# #     def bar(foo: Depends(foo)):
# #         return "bar"

# #     def baz(foo: Depends(foo)):
# #         return "baz"

# #     def qux(bar: Depends(bar), baz: Depends(baz)):
# #         return "qux"

# #     diagraph = Diagraph(qux)

# #     node = diagraph[1]
# #     assert node is not None
# #     assert type(node) is tuple
# #     assert len(node) == 2
# #     assert node[0].node == bar
# #     assert node[1].node == baz

# #     node = diagraph[-2]
# #     assert node is not None
# #     assert type(node) is tuple
# #     assert len(node) == 2
# #     assert node[0].node == bar
# #     assert node[1].node == baz

# # def test_it_gets_back_a_tuple_for_parallels_by_specifying_either_node_as_key():
# #     def foo():
# #         return "foo"

# #     def bar(foo: Depends(foo)):
# #         return "bar"

# #     def baz(foo: Depends(foo)):
# #         return "baz"

# #     def qux(bar: Depends(bar), baz: Depends(baz)):
# #         return "qux"

# #     diagraph = Diagraph(qux)

# #     node = diagraph[bar]
# #     assert node is not None
# #     assert type(node) is tuple
# #     assert len(node) == 2
# #     assert node[0].node == bar
# #     assert node[1].node == baz

# #     node = diagraph[baz]
# #     assert node is not None
# #     assert type(node) is tuple
# #     assert len(node) == 2
# #     assert node[0].node == bar
# #     assert node[1].node == baz


def test_a_complicated_tree():
    def l0():
        pass

    def l1_l(l0: Depends(l0)):
        pass

    def l1_r(l0: Depends(l0)):
        pass

    def l2_l(l1_l: Depends(l1_l), l1_r: Depends(l1_r)):
        pass

    def l2_r(l1_r: Depends(l1_r)):
        pass

    def l3_l(l2_l: Depends(l2_l), l1_r: Depends(l1_r), l0: Depends(l0)):
        pass

    def l4(l3_l: Depends(l3_l), l1_r: Depends(l1_r), l2_r: Depends(l2_r)):
        pass

    diagraph = Diagraph(l4)

    # assert diagraph.dg.nodes()

    def check_node(key):
        node = diagraph[key]
        assert node is not None
        assert isinstance(node, DiagraphNode)
        return node.__fn__

    def check_tuple(key):
        nodes = diagraph[key]
        assert nodes is not None
        assert isinstance(nodes, tuple)
        return tuple([n.__fn__ for n in nodes])

    for node in [l0, l1_l, l1_r, l2_l, l2_r, l3_l, l4]:
        assert check_node(node) == node

    for index, nodes in [
        (0, (l0,)),
        (1, (l1_l, l1_r)),
        # (2, (l2_l, l2_r)),
    ]:
        print(nodes)
        print(check_tuple(index))
        assert check_tuple(index) == nodes
    # assert check_tuple(1) == (l1_l, l1_r)
    # assert check_tuple(2) == (l2_l, l2_r)
    # assert check_node(3) == l3_l
    # assert check_node(4) == l4

    # assert check_node(-5) == l0
    # assert check_tuple(-4) == (l1_l, l1_r)
    # assert check_tuple(-3) == (l2_l, l2_r)
    # assert check_node(-2) == l3_l
    # assert check_node(-1) == l4


# # def test_a_complicated_tree_with_multiple_origin_points():
# pass

# # def test_a_complicated_tree_with_multiple_terminal_points():
# #     def l0():
# #         pass

# #     def l1_l(l0: Depends(l0)):
# #         pass

# #     def l1_r(l0: Depends(l0)):
# #         pass

# #     def l2_l(l1_l: Depends(l1_l)):
# #         pass

# #     def l3_l(l2_l: Depends(l2_l), l1_r: Depends(l1_r)):
# #         pass

# #     def l3_r(l1_r: Depends(l1_r)):
# #         pass

# #     diagraph = Diagraph(l3_l, l3_r)


# def test_it_calls_a_prompt():
#     @prompt
#     def tell_me_a_joke(input: str) -> str:
#         return f"Computer! Tell me a joke about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert node.prompt() == "Computer! Tell me a joke about {input}."


# def test_it_calls_a_prompt_with_an_argument():
#     @prompt
#     def tell_me_a_joke(input: str, joke_string: str) -> str:
#         return f"Computer! Tell me a {joke_string} about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert node.prompt("foo", "jokey") == "Computer! Tell me a jokey about foo."


# def test_it_calls_a_prompt_with_a_named_argument():
#     @prompt
#     def tell_me_a_joke(input: str, joke_string: str) -> str:
#         return f"Computer! Tell me a {joke_string} about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert (
#         node.prompt(input="foo", joke_string="jokey")
#         == "Computer! Tell me a jokey about foo."
#     )


# def test_it_calls_tokens():
#     @prompt
#     def tell_me_a_joke(input: str) -> str:
#         return f"Computer! Tell me a joke about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert node.tokens() == 8


# def test_it_calls_tokens_with_an_argument():
#     @prompt
#     def tell_me_a_joke(input: str) -> str:
#         return f"Computer! Tell me a joke about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert node.tokens("tomatoes") == 9


# def test_it_calls_tokens_with_named_arguments():
#     @prompt
#     def tell_me_a_joke(input: str, joke_string: str) -> str:
#         return f"Computer! Tell me a {joke_string} about {input}."

#     node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
#     assert node is not None
#     assert type(node) != tuple
#     assert isinstance(node, DiagraphNode)
#     assert node.tokens(joke_string="jokey", input="foo") == 10

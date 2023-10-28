from ..decorators import prompt
from .diagraph_node import DiagraphNode
from .diagraph import Diagraph


def describe_prompt():
    def test_it_calls_a_prompt():
        @prompt
        def tell_me_a_joke(input: str) -> str:
            return f"Computer! Tell me a joke about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert node.prompt() == "Computer! Tell me a joke about {input}."

    def test_it_calls_a_prompt_with_an_argument():
        @prompt
        def tell_me_a_joke(input: str, joke_string: str) -> str:
            return f"Computer! Tell me a {joke_string} about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert node.prompt("foo", "jokey") == "Computer! Tell me a jokey about foo."

    def test_it_calls_a_prompt_with_a_named_argument():
        @prompt
        def tell_me_a_joke(input: str, joke_string: str) -> str:
            return f"Computer! Tell me a {joke_string} about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert (
            node.prompt(input="foo", joke_string="jokey")
            == "Computer! Tell me a jokey about foo."
        )


def describe_tokens():
    def test_it_calls_tokens():
        @prompt
        def tell_me_a_joke(input: str) -> str:
            return f"Computer! Tell me a joke about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert node.tokens() == 8

    def test_it_calls_tokens_with_an_argument():
        @prompt
        def tell_me_a_joke(input: str) -> str:
            return f"Computer! Tell me a joke about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert node.tokens("tomatoes") == 9

    def test_it_calls_tokens_with_named_arguments():
        @prompt
        def tell_me_a_joke(input: str, joke_string: str) -> str:
            return f"Computer! Tell me a {joke_string} about {input}."

        node = Diagraph(tell_me_a_joke)[tell_me_a_joke]
        assert node.tokens(joke_string="jokey", input="foo") == 10

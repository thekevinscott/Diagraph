import pytest
from unittest.mock import patch
from .openai_llm import DEFAULT_MODEL, OpenAI, cast_to_input


def describe_cast_to_input():
    def test_it_casts_to_parsed_input():
        assert cast_to_input("foo") == [{"role": "user", "content": "foo"}]

    def test_it_returns_if_not_a_string():
        input = [{"role": "user", "content": "foo"}]
        assert cast_to_input(input) == input


def mock_openai_return_value(times=1):
    return iter(
        [
            {
                "id": "chatcmpl-8F67ICEUxk7Xqjy2qdGv5gx5mj0Bm",
                "object": "chat.completion.chunk",
                "created": 1698609124,
                "model": "gpt-3.5-turbo-0613",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"role": "assistant", "content": f"{i}"},
                        "finish_reason": None,
                    }
                ],
            }
            for i in range(times)
        ]
    )


def describe_openai_llm():
    def test_it_instantiates():
        OpenAI()

    def test_it_runs():
        def handle_log(event, data):
            pass

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value()
            assert OpenAI().run("foo", log=handle_log) == "0"

    def test_it_passes_kwargs_and_parses_string_by_default():
        def handle_log(event, data):
            pass

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value()
            OpenAI().run("foo", log=handle_log, foo="foo")
            create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model=DEFAULT_MODEL,
                foo="foo",
                stream=True,
            )

    def test_it_accepts_alternate_models():
        def handle_log(event, data):
            pass

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value()
            OpenAI(model="gpt-foo").run("foo", log=handle_log)
            create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-foo",
                stream=True,
            )

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value()
            OpenAI().run("foo", log=handle_log, model="gpt-bar")
            create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-bar",
                stream=True,
            )

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value()
            OpenAI(model="gpt-foo").run("foo", log=handle_log, model="gpt-bar")
            create.assert_called_with(
                messages=[{"role": "user", "content": "foo"}],
                model="gpt-bar",
                stream=True,
            )

    def describe_logs():
        def test_it_does_not_call_start_if_encountering_an_error(mocker):
            handle_log = mocker.stub()

            with patch("openai.ChatCompletion.create") as create:
                create.side_effect = Exception("wruh wroh")
                with pytest.raises(Exception):
                    OpenAI(model="gpt-foo").run("foo", log=handle_log)
                assert handle_log.call_count == 0

        def test_it_calls_all_events(mocker):
            handle_log = mocker.stub()

            with patch("openai.ChatCompletion.create") as create:
                create.return_value = mock_openai_return_value(3)
                OpenAI(model="gpt-foo").run("foo", log=handle_log)

                handle_log.assert_any_call("start", None)
                handle_log.assert_any_call("data", "0")
                handle_log.assert_any_call("data", "1")
                handle_log.assert_any_call("data", "2")
                handle_log.assert_any_call("end", None)

    def test_it_returns_content_response(mocker):
        handle_log = mocker.stub()

        with patch("openai.ChatCompletion.create") as create:
            create.return_value = mock_openai_return_value(3)
            assert OpenAI(model="gpt-foo").run("foo", log=handle_log) == "012"


# # except openai.error.Timeout as e:
# #   # Handle timeout error, e.g. retry or log
# #   print(f"OpenAI API request timed out: {e}")
# #   pass
# # except openai.error.APIError as e:
# #   # Handle API error, e.g. retry or log
# #   print(f"OpenAI API returned an API Error: {e}")
# #   pass
# # except openai.error.APIConnectionError as e:
# #   # Handle connection error, e.g. check network or log
# #   print(f"OpenAI API request failed to connect: {e}")
# #   pass
# # except openai.error.InvalidRequestError as e:
# #   # Handle invalid request error, e.g. validate parameters or log
# #   print(f"OpenAI API request was invalid: {e}")
# #   pass
# # except openai.error.AuthenticationError as e:
# #   # Handle authentication error, e.g. check credentials or log
# #   print(f"OpenAI API request was not authorized: {e}")
# #   pass
# # except openai.error.PermissionError as e:
# #   # Handle permission error, e.g. check scope or log
# #   print(f"OpenAI API request was not permitted: {e}")
# #   pass
# # except openai.error.RateLimitError as e:
# #   # Handle rate limit error, e.g. wait or log
# #   print(f"OpenAI API request exceeded rate limit: {e}")
# #   pass

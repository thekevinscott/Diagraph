import pytest
from unittest.mock import patch



def describe_openai_llm():
    class MockAsyncOpenAI:
        def __init__(self, times = 1):
            class FakeGenerator:
                def __init__(self, times):
                    self.times = times
                    self.current_i = 0

                async def __anext__(self):
                    current_i = self.current_i
                    if self.times <= current_i:
                        raise StopAsyncIteration  # raise at end of iteration
                    class Delta:
                        content = f'{current_i}'
                    class Choice:
                        delta = Delta()
                    class ChatCompletion:
                        choices = [Choice]
                        
                    self.current_i += 1
                    return ChatCompletion()

                def __aiter__(self):
                    return self

            class Completions:
                async def create(self, **kwargs):
                    return FakeGenerator(times)

            class Chat:
                completions = Completions()

            self.chat = Chat()

    with patch("openai.AsyncOpenAI", MockAsyncOpenAI):
        def describe_cast_to_input():
            def test_it_casts_to_parsed_input():
                with patch("diagraph.llm.openai_llm.AsyncOpenAI", MockAsyncOpenAI):
                    from .openai_llm import cast_to_input
                    assert cast_to_input("foo") == [{"role": "user", "content": "foo"}]

            def test_it_returns_if_not_a_string():
                with patch("diagraph.llm.openai_llm.AsyncOpenAI", MockAsyncOpenAI):
                    from .openai_llm import cast_to_input
                    input = [{"role": "user", "content": "foo"}]
                    assert cast_to_input(input) == input


    def test_it_instantiates():
        from .openai_llm import OpenAI
        OpenAI()

    @pytest.mark.asyncio
    async def test_it_runs():
        def handle_log(event, data):
            pass

        with patch("diagraph.llm.openai_llm.AsyncOpenAI", MockAsyncOpenAI):
            from .openai_llm import OpenAI
            # create.return_value = mock_openai_return_value()
            assert await OpenAI().run("foo", log=handle_log) == "0"

        # @pytest.mark.asyncio
        # async def test_it_passes_kwargs_and_parses_string_by_default():
        #     def handle_log(event, data):
        #         pass

        #     with patch("diagraph.llm.openai_llm.AsyncOpenAI", MockAsyncOpenAI):
        #         from .openai_llm import OpenAI, DEFAULT_MODEL
        #         await OpenAI().run("foo", log=handle_log, foo="foo")
        #         # create.assert_called_with(
        #         #     messages=[{"role": "user", "content": "foo"}],
        #         #     model=DEFAULT_MODEL,
        #         #     foo="foo",
        #         #     stream=True,
        #         # )

    #     @pytest.mark.asyncio
    #     async def test_it_accepts_alternate_models():
    #         def handle_log(event, data):
    #             pass

    #         with patch("openai.resources.chat.Completions.create") as create:
    #             create.return_value = mock_openai_return_value()
    #             await OpenAI(model="gpt-foo").run("foo", log=handle_log)
    #             create.assert_called_with(
    #                 messages=[{"role": "user", "content": "foo"}],
    #                 model="gpt-foo",
    #                 stream=True,
    #             )

    #         with patch("openai.resources.chat.Completions.create") as create:
    #             create.return_value = mock_openai_return_value()
    #             await OpenAI().run("foo", log=handle_log, model="gpt-bar")
    #             create.assert_called_with(
    #                 messages=[{"role": "user", "content": "foo"}],
    #                 model="gpt-bar",
    #                 stream=True,
    #             )

    #         with patch("openai.resources.chat.Completions.create") as create:
    #             create.return_value = mock_openai_return_value()
    #             await OpenAI(model="gpt-foo").run("foo", log=handle_log, model="gpt-bar")
    #             create.assert_called_with(
    #                 messages=[{"role": "user", "content": "foo"}],
    #                 model="gpt-bar",
    #                 stream=True,
    #             )

    #     def describe_logs():
    #         @pytest.mark.asyncio
    #         async def test_it_does_not_call_start_if_encountering_an_error(mocker):
    #             handle_log = mocker.stub()

    #             with patch("openai.resources.chat.Completions.create") as create:
    #                 create.side_effect = Exception("wruh wroh")
    #                 with pytest.raises(Exception):
    #                     await OpenAI(model="gpt-foo").run("foo", log=handle_log)
    #                 assert handle_log.call_count == 0

    #         @pytest.mark.asyncio
    #         async def test_it_calls_all_events(mocker):
    #             handle_log = mocker.stub()

    #             with patch("openai.resources.chat.Completions.create") as create:
    #                 create.return_value = mock_openai_return_value(3)
    #                 await OpenAI(model="gpt-foo").run("foo", log=handle_log)

    #                 handle_log.assert_any_call("start", None)
    #                 handle_log.assert_any_call("data", "0")
    #                 handle_log.assert_any_call("data", "1")
    #                 handle_log.assert_any_call("data", "2")
    #                 handle_log.assert_any_call("end", None)

    #     @pytest.mark.asyncio
    #     async def test_it_returns_content_response(mocker):
    #         handle_log = mocker.stub()

    #         with patch("openai.resources.chat.Completions.create") as create:
    #             create.return_value = mock_openai_return_value(3)
    #             assert await OpenAI(model="gpt-foo").run("foo", log=handle_log) == "012"


    # # # except openai.error.Timeout as e:
    # # #   # Handle timeout error, e.g. retry or log
    # # #   print(f"OpenAI API request timed out: {e}")
    # # #   pass
    # # # except openai.error.APIError as e:
    # # #   # Handle API error, e.g. retry or log
    # # #   print(f"OpenAI API returned an API Error: {e}")
    # # #   pass
    # # # except openai.error.APIConnectionError as e:
    # # #   # Handle connection error, e.g. check network or log
    # # #   print(f"OpenAI API request failed to connect: {e}")
    # # #   pass
    # # # except openai.error.InvalidRequestError as e:
    # # #   # Handle invalid request error, e.g. validate parameters or log
    # # #   print(f"OpenAI API request was invalid: {e}")
    # # #   pass
    # # # except openai.error.AuthenticationError as e:
    # # #   # Handle authentication error, e.g. check credentials or log
    # # #   print(f"OpenAI API request was not authorized: {e}")
    # # #   pass
    # # # except openai.error.PermissionError as e:
    # # #   # Handle permission error, e.g. check scope or log
    # # #   print(f"OpenAI API request was not permitted: {e}")
    # # #   pass
    # # # except openai.error.RateLimitError as e:
    # # #   # Handle rate limit error, e.g. wait or log
    # # #   print(f"OpenAI API request exceeded rate limit: {e}")
    # # #   pass

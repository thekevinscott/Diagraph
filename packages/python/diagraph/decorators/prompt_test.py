import pytest
from typing import Annotated
from ..classes.diagraph import Diagraph
from ..utils.depends import Depends
from .prompt import prompt


class MockLLM:
    times: int
    error: bool

    def __init__(self, times=0, error=False, **kwargs):
        self.times = times
        self.kwargs = kwargs
        self.error = error

    def run(self, prompt, log, model=None, stream=None, **kwargs):
        response = ""
        kwargs = {
            **self.kwargs,
            **kwargs,
            "model": model,
        }
        response = ""
        if self.error:
            raise Exception("test error")
        log("start", None)

        for i in range(self.times):
            i = f"{i}"
            response += i
            log("data", i)
        log("end", None)
        return response


def describe_logs():
    def test_it_handles_logs_for_a_diagraph(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn, log=log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_it_handles_logs_for_a_fn(mocker):
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)


def describe_errors():
    def test_it_handles_errors(mocker):
        handle_errors = mocker.stub()

        @prompt(llm=MockLLM(error=True))
        def fn():
            return "test prompt"

        Diagraph(fn, error=handle_errors).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert handle_errors.call_args_list[0][0][1] == fn
        assert len(handle_errors.call_args_list[0][0]) == 2

    def test_it_handles_errors_at_a_function_level(mocker):
        handle_errors = mocker.stub()

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert len(handle_errors.call_args_list[0][0]) == 1

    def test_it_halts_execution_on_error_and_raises_without_handler():
        @prompt(llm=MockLLM())
        def fn():
            return "fn"

        @prompt(llm=MockLLM(error=True))
        def bar(fn: Annotated[str, Depends(fn)]):
            return "bar"

        with pytest.raises(Exception):
            assert Diagraph(bar).run().result == "fn"

    def test_it_halts_execution_on_error_and_does_not_raise_without_handler(mocker):
        handle_errors = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def fn():
            return "prompt"

        @prompt(llm=MockLLM(error=True))
        def bar(fn: Annotated[str, Depends(fn)]):
            return "bar"

        diagraph = Diagraph(bar, error=handle_errors).run()
        assert diagraph.result == "012"
        assert handle_errors.call_count == 1

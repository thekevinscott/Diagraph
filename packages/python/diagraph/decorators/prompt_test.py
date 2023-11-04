import pytest
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

    def test_it_can_set_a_default_log(mocker):
        log = mocker.stub()

        times = 3

        Diagraph.set_log(log)

        @prompt(llm=MockLLM(times=times))
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None, fn)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i, fn)
        log.assert_any_call("end", None, fn)

    def test_a_default_log_fn_can_be_overridden_at_the_diagraph_level(mocker):
        default_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(default_log)

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
        assert default_log.call_count == 0

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

    def test_a_diagraph_log_fn_can_be_overridden_at_the_function_level(mocker):
        diagraph_log = mocker.stub()
        log = mocker.stub()

        times = 3

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn, log=diagraph_log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)
        assert diagraph_log.call_count == 0

    def test_a_global_log_fn_can_be_overridden_at_the_function_level(mocker):
        global_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(global_log)

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
        assert global_log.call_count == 0

    def test_a_global_and_diagraph_log_fn_can_be_overridden_at_the_function_level(
        mocker,
    ):
        global_log = mocker.stub()
        diagraph_log = mocker.stub()
        log = mocker.stub()

        times = 3

        Diagraph.set_log(global_log)

        @prompt(llm=MockLLM(times=times), log=log)
        def fn():
            return "test prompt"

        Diagraph(fn, log=diagraph_log).run()

        assert log.call_count == 2 + times
        log.assert_any_call("start", None)
        for i in range(times):
            i = f"{i}"
            log.assert_any_call("data", i)
        log.assert_any_call("end", None)
        assert global_log.call_count == 0
        assert diagraph_log.call_count == 0


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

    def test_it_can_set_a_global_error_handler(mocker):
        handle_errors = mocker.stub()

        Diagraph.set_error(handle_errors)

        @prompt(llm=MockLLM(error=True))
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert handle_errors.call_args_list[0][0][1] == fn
        assert len(handle_errors.call_args_list[0][0]) == 2

    def test_a_diagraph_error_handler_overrides_a_global_error_handler(mocker):
        global_handle_errors = mocker.stub()
        handle_errors = mocker.stub()

        Diagraph.set_error(global_handle_errors)

        @prompt(llm=MockLLM(error=True))
        def fn():
            return "test prompt"

        Diagraph(fn, error=handle_errors).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert handle_errors.call_args_list[0][0][1] == fn
        assert len(handle_errors.call_args_list[0][0]) == 2
        assert global_handle_errors.call_count == 0

    def test_it_handles_errors_at_a_function_level(mocker):
        handle_errors = mocker.stub()

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert len(handle_errors.call_args_list[0][0]) == 1

    def test_it_handles_errors_at_a_function_level_and_overrides_global_error_fn(
        mocker,
    ):
        global_handle_errors = mocker.stub()
        handle_errors = mocker.stub()

        Diagraph.set_error(global_handle_errors)

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "test prompt"

        Diagraph(fn).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert len(handle_errors.call_args_list[0][0]) == 1
        assert global_handle_errors.call_count == 0

    def test_it_handles_errors_at_a_function_level_and_overrides_global_and_diagraph_error_fn(
        mocker,
    ):
        global_handle_errors = mocker.stub()
        diagraph_handle_errors = mocker.stub()
        handle_errors = mocker.stub()

        Diagraph.set_error(global_handle_errors)

        @prompt(llm=MockLLM(error=True), error=handle_errors)
        def fn():
            return "test prompt"

        Diagraph(fn, error=diagraph_handle_errors).run()

        assert handle_errors.call_count == 1
        assert isinstance(handle_errors.call_args_list[0][0][0], Exception)
        assert len(handle_errors.call_args_list[0][0]) == 1
        assert global_handle_errors.call_count == 0
        assert diagraph_handle_errors.call_count == 0

    def test_it_halts_execution_on_error_and_raises_without_handler():
        @prompt(llm=MockLLM())
        def fn():
            return "fn"

        @prompt(llm=MockLLM(error=True))
        def bar(fn: str = Depends(fn)):
            return "bar"

        with pytest.raises(Exception):
            assert Diagraph(bar).run().result == "fn"

    def test_it_halts_execution_on_error_and_does_not_raise_without_handler(mocker):
        handle_errors = mocker.stub()

        @prompt(llm=MockLLM(times=3))
        def fn():
            return "prompt"

        @prompt(llm=MockLLM(error=True))
        def bar(fn: str = Depends(fn)):
            return "bar"

        diagraph = Diagraph(bar, error=handle_errors).run()
        assert diagraph.result == "012"
        assert handle_errors.call_count == 1

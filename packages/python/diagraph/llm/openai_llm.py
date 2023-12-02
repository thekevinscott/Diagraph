from collections.abc import Awaitable
from typing import Any

from openai import AsyncOpenAI
from openai import OpenAI as SyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..classes.types import FunctionLogHandler
from .llm import LLM


def cast_to_input(
    prompt_str: str | list[ChatCompletionMessageParam] | dict[str, Any],
) -> list[ChatCompletionMessageParam]:
    if isinstance(prompt_str, str):
        return [{"role": "user", "content": prompt_str}], None
    if isinstance(prompt_str, dict):
        return prompt_str.get("messages"), prompt_str.get("functions")
    return prompt_str, None


DEFAULT_MODEL = "gpt-3.5-turbo"


class OpenAI(LLM):
    __aclient__: AsyncOpenAI | None = None
    __client__: SyncOpenAI | None = None
    kwargs: dict[Any, Any]
    api_key: None | str

    def __init__(self, api_key=None, **kwargs) -> None:
        self.api_key = api_key
        self.kwargs = kwargs

    @property
    def aclient(self) -> AsyncOpenAI:
        aclient = self.__aclient__
        if aclient is None:
            aclient = AsyncOpenAI(api_key=self.api_key)
            self.__aclient__ = aclient

        return aclient

    @property
    def client(self) -> SyncOpenAI:
        client = self.__client__
        if client is None:
            client = SyncOpenAI(api_key=self.api_key)
            self.__client__ = client

        return client

    def run(
        self,
        prompt: str | list[ChatCompletionMessageParam] | dict[str, Any],
        log: FunctionLogHandler,
        model=None,
        **kwargs,
    ) -> Awaitable[Any]:
        client = self.client
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages, functions = cast_to_input(prompt)

        response = ""
        if "stream" in kwargs:
            del kwargs["stream"]
        kwargs = {
            **self.kwargs,
            **kwargs,
            "stream": True,
            "model": model,
            "messages": messages,
        }
        if functions is not None:
            kwargs["functions"] = functions
        started = False
        for resp in client.chat.completions.create(**kwargs):
            if started is False:
                log("start", None)
                started = True
            choices = resp.choices
            choice = choices[0]
            delta = choice.delta
            content = delta.content
            if content:
                response += content
                log("data", content)
        log("end", None)
        return response

    # async def arun(
    #     self,
    #     prompt: str | list[ChatCompletionMessageParam],
    #     log: FunctionLogHandler,
    #     model=None,
    #     **kwargs,
    # ) -> Awaitable[Any]:
    #     client = self.aclient
    #     model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
    #     messages = cast_to_input(prompt)

    #     response = ""
    #     if "stream" in kwargs:
    #         del kwargs["stream"]
    #     kwargs = {
    #         **self.kwargs,
    #         **kwargs,
    #         "stream": True,
    #         "model": model,
    #         "messages": messages,
    #     }
    #     started = False
    #     r = await client.chat.completions.create(**kwargs)
    #     async for resp in r:
    #         if started is False:
    #             log("start", None)
    #             started = True
    #         choices = resp.choices
    #         choice = choices[0]
    #         delta = choice.delta
    #         content = delta.content
    #         if content:
    #             response += content
    #             log("data", content)
    #     log("end", None)
    #     return response

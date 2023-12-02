from typing import Any

from openai import AsyncOpenAI
from openai import OpenAI as SyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from ..classes.types import FunctionLogHandler
from .llm import LLM


def cast_to_input(
    prompt_str: str | list[ChatCompletionMessageParam] | dict[str, Any],
) -> tuple[list[ChatCompletionMessageParam], dict[str, Any]]:
    if isinstance(prompt_str, str):
        return [{"role": "user", "content": prompt_str}], {}
    if isinstance(prompt_str, dict):
        prompt_str = {**prompt_str}
        messages = prompt_str.get("messages")
        del prompt_str["messages"]

        return messages, prompt_str
    return prompt_str, {}


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
    ) -> str | dict[str, str]:
        client = self.client
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages, rest = cast_to_input(prompt)

        response: dict[str, str] = {}
        if "stream" in kwargs:
            del kwargs["stream"]
        kwargs = {
            **self.kwargs,
            **kwargs,
            "stream": True,
            "model": model,
            "messages": messages,
        }
        for key in rest.keys():
            kwargs[key] = rest[key]
        started = False
        for resp in client.chat.completions.create(**kwargs):
            if started is False:
                log("start", None)
                started = True
            choices = resp.choices
            choice = choices[0]
            delta = choice.delta
            delta = delta.model_dump(exclude_unset=True)
            response = build_dict(response, delta)
        log("end", None)

        # TODO: Remove this block once we have return type coercion.
        # LLM should not alter the response, that should be the provenance
        # of the return type.
        if len(response.keys()) == 1:
            if "content" not in response:
                raise Exception(f"Unknown key found: {response.keys()}")
            return response["content"]
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


RecursiveDict = dict[str, str | dict[str, str]]


def build_dict(response: RecursiveDict, delta: RecursiveDict):
    for key in delta.keys():
        if delta.get(key) is not None:
            if type(delta[key]) is str:
                if response.get(key) is None:
                    response[key] = ""
                response[key] += delta[key]
            else:
                if response.get(key) is None:
                    response[key] = {}
                response[key] = build_dict(response[key], delta[key])
    return response

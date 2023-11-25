from typing import Any, Awaitable, Optional
from openai import AsyncOpenAI, OpenAI as SyncOpenAI
from openai.types.chat import ChatCompletionMessageParam


from ..classes.types import FunctionLogHandler
from .llm import LLM


def cast_to_input(
    prompt_str: str | list[ChatCompletionMessageParam],
) -> list[ChatCompletionMessageParam]:
    if isinstance(prompt_str, str):
        return [{"role": "user", "content": prompt_str}]
    return prompt_str


DEFAULT_MODEL = "gpt-3.5-turbo"


class OpenAI(LLM):
    __aclient__: Optional[AsyncOpenAI] = None
    __client__: Optional[SyncOpenAI] = None
    kwargs: dict[Any, Any]

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    @property
    def aclient(self) -> AsyncOpenAI:
        aclient = self.__aclient__
        if aclient is None:
            aclient = AsyncOpenAI()
            self.__aclient__ = aclient

        return aclient

    @property
    def client(self) -> SyncOpenAI:
        print("SyncOpenAI", SyncOpenAI)
        client = self.__client__
        if client is None:
            client = SyncOpenAI()
            self.__client__ = client

        return client

    def run(
        self,
        prompt: str | list[ChatCompletionMessageParam],
        log: FunctionLogHandler,
        model=None,
        stream=None,
        **kwargs,
    ) -> Awaitable[Any]:
        client = self.client
        print("client", client)
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages = cast_to_input(prompt)

        response = ""
        kwargs = {
            **self.kwargs,
            **kwargs,
            "stream": True,
            "model": model,
            "messages": messages,
        }
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

    async def arun(
        self,
        prompt: str | list[ChatCompletionMessageParam],
        log: FunctionLogHandler,
        model=None,
        stream=None,
        **kwargs,
    ) -> Awaitable[Any]:
        client = self.aclient
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages = cast_to_input(prompt)

        response = ""
        kwargs = {
            **self.kwargs,
            **kwargs,
            "stream": True,
            "model": model,
            "messages": messages,
        }
        started = False
        r = await client.chat.completions.create(**kwargs)
        async for resp in r:
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

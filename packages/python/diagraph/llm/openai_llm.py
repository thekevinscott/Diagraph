from typing import Any, Callable, Optional
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam
from .llm import LLM



def cast_to_input(prompt_str: str | list[ChatCompletionMessageParam]) -> list[ChatCompletionMessageParam]:
    if isinstance(prompt_str, str):
        return [{"role": "user", "content": prompt_str}]
    return prompt_str


DEFAULT_MODEL = "gpt-3.5-turbo"

Log = Callable[[str, str | None], None]


class OpenAI(LLM):
    __aclient__: Optional[AsyncOpenAI] = None
    kwargs: dict[Any, Any]

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @property
    def client(self) -> AsyncOpenAI:
        aclient = self.__aclient__
        if aclient is None:
            aclient = AsyncOpenAI()
            self.__aclient__ = aclient

        return aclient

    async def run(self, prompt: str | list[ChatCompletionMessageParam], log: Log, model=None, stream=None, **kwargs):
        client = self.client
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages = cast_to_input(prompt)

        response = ""
        kwargs = {
            **self.kwargs,
            **kwargs,
            'stream': True,
            'model': model,
            'messages': messages,
        }
        started = False
        async for resp in await client.chat.completions.create(
            **kwargs
        ):
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

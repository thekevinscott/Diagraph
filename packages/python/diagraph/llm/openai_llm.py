from typing import Any, Callable
import openai
from .llm import LLM


def cast_to_input(prompt):
    if isinstance(prompt, str):
        return [{"role": "user", "content": prompt}]
    return prompt


DEFAULT_MODEL = "gpt-3.5-turbo"

Log = Callable[[str, str], None]


class OpenAI(LLM):
    kwargs: dict[Any, Any]

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, prompt, log: Log, model=None, stream=None, **kwargs):
        model = model if model else self.kwargs.get("model", DEFAULT_MODEL)
        messages = cast_to_input(prompt)

        response = ""
        kwargs = {
            **self.kwargs,
            **kwargs,
            "model": model,
        }
        started = False
        for resp in openai.ChatCompletion.create(
            messages=messages, stream=True, **kwargs
        ):
            if started is False:
                log("start", None)
                started = True
            choices = resp.get("choices")
            choice = choices[0]
            delta = choice.get("delta")
            content = delta.get("content")
            if content:
                response += content
                log("data", content)
        log("end", None)
        return response

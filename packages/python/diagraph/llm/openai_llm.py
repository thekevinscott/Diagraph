import openai
from .llm import LLM


def cast_to_input(prompt):
    if type(prompt) == str:
        return [{"role": "user", "content": prompt}]
    return prompt


DEFAULT_MODEL = "gpt-3.5-turbo"


class OpenAI(LLM):
    kwargs = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def run(self, prompt, model=None, stream=None, **kwargs):
        model = model if model else self.kwargs.get("model")
        if model is None:
            model = DEFAULT_MODEL
        print("Using model", model)
        messages = cast_to_input(prompt)

        response = ""
        print("Response: ", end="")
        kwargs = {
            **self.kwargs,
            **kwargs,
            "model": model,
        }
        for resp in openai.ChatCompletion.create(
            messages=messages, stream=True, **kwargs
        ):
            choices = resp.get("choices")
            choice = choices[0]
            delta = choice.get("delta")
            content = delta.get("content")
            if content:
                response += content
                print(content, end="")
        print("\n")
        return response

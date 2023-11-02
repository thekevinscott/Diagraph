---
sidebar_position: 3
---

# Prompts

Functions are primarily used for interacting with an LLM. There's a decorator, `prompt`, for this purpose. Decorating a Python function with `@prompt` gives it super powers.

```python
from diagraph import Diagraph, prompt

@prompt
def tell_me_a_joke(input: str) -> str:
    return 'Computer! Tell me a joke about {input}.'

dg = Diagraph(tell_me_a_joke).run('tomatoes')
print(dg.result)  # Why did the tomato turn red? Because it saw the salad dressing!
```

Here, Diagraph automatically calls OpenAI and returns the result.

You can see the prompt that was passed:

```python
print(dg[tell_me_a_joke].prompt) # Computer! tell me a joke about tomatoes
```

You can also access the original function:

```python
print(dg[tell_me_a_joke].fn) # tell_me_a_joke
```

Or the tokens of the prompt:

```python
print(dg[tell_me_a_joke].tokens) # 8
```


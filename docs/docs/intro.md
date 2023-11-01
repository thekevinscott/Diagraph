---
sidebar_position: 1
---

# Introduction

```python live
from typing import Annotated
from diagraph import Diagraph, prompt, Depends, OpenAI

# @prompt(llm=OpenAI(model='gpt-4'))
def tell_me_a_joke(about):
    return f'Computer! Tell me a joke about {about}.'

# @prompt(llm=OpenAI(model='gpt-4'))
def explanation(joke: Annotated[str, Depends(tell_me_a_joke)]) -> str:
    return f'Explain why the joke "{joke}" is funny.'

def handle_log(event, data, fn):
    if event == 'start':
        print('*' * 20, fn.__name__, '*' * 20)
    elif event == 'end':
        print(f'\n')        
    else:
        print(data, end='')

diagraph = Diagraph(explanation, log=handle_log).run('tomatoes')
diagraph.result

```

Diagraph is a graph for representing LLM interactions.

## Housekeeping

Some housekeeping notes about these docs.

### Live Code Snippets

Throughout the docs, you will see code snippets like the below:

```python live
import time
def foo():
  for i in range(10):
    print(i) # this will get logged the right hand logs pane
    time.sleep(0.1)
  return 'foo' # this will get logged to the bottom output pane

foo()
```

Code snippets are editable and can be executed with the `Run` button.

Code snippets run in [pyodide](https://pyodide.org/en/stable/), which is an entirely clientside Python environment so. Everything runs in your browser.

To return to the original code snippet after you've made an edit, hit the `Reload` button:

<sl-icon-button disabled name="arrow-clockwise" label="Reload Code Snippet"></sl-icon-button>

### LLM

The default LLM in Diagraph is OpenAI. However, the docs use a clientside LLM called Vicuna-7b.

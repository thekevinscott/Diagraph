---
sidebar_position: 3
---

# Getting Started

## Installation

```bash
pip install diagraph[openai]
```

Diagraph ships with a number of optional dependencies, dependencing on what LLMs you want to use. They include:

* `diagraph[all]` - all connectors
* `diagraph[openai]` - `openai` connectors
* `diagraph` - no connectors (appropriate for custom LLMs written by you)

## Quickstart

```python
import openai

openai.api_key = 'sk-<OPENAI_TOKEN>'

from diagraph import Diagraph, prompt, Depends

@prompt
def tell_me_a_joke(topic: str):
  return f'Tell me a funny joke about {topic}'

@prompt
def explain_that_joke(the_joke: str = Depends(tell_me_a_joke)):
  return f'Explain why the following joke is funny: {the_joke}'

dg = Diagraph(explain_that_joke)

print(dg.run('drummers').result)
# > The joke "drummers" is a play on words and relies on the double meaning of the word "drummers."

print(dg[tell_me_a_joke].result)
# > Why don't drummers drink coffee? Because it always gets them in a jam!
```

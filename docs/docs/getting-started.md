---
sidebar_position: 2
---

# Getting Started

## Installation

```
pip install diagraph
```

## Quick Start

```python
from diagraph import Diagraph, Depends, prompt, llm

openai.api_key = 'sk-<OPENAI_TOKEN>'

@prompt
def tell_me_a_joke():
  return 'Computer! Tell me a joke about tomatoes.'

def explanation(joke: Depends(tell_me_a_joke)) -> str:
  return openai.completion(f'Explain why the joke "{joke}" is funny.')

print(Diagraph(explanation).run().result)
# 'The joke is a play on words and concepts. There are two main ideas that make it humorous...
```

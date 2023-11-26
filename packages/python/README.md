# Diagraph

Diagraph represents Large Language Model (LLM) interactions as a graph, which makes it easy to build, edit, and re-execute a chain of structured dialogues.

Key features:

- **Code Faster & Save Money:** Diagraph's ability to cache and replay specific parts of your code saves on execution time and reduces prompt costs.
- **Quick Iteration:** Edit interactions on the fly. Rewrite the LLM's results as well as the functions.
- **Easy Refactoring:** Specify a function's dependencies as parameters for clean, readable, and _refactorable_ code.
- **Bring Your Own Code:** Use any LLM or set of tools you want. Diagraph operates on top of plain Python functions.
- **Visualize The System:** Get a straightforward view of your graph with a built-in Jupyter visualization tool.
- **Concurrency:** Interactions that can be run in parallel, _should_ be run in parallel. Get this behavior for free.
- **Result coercion:** (_under development_) LLMs don't always respond how you need. Automatically coerce the results you need from the LLM's response.

## Requirements

Python 3.10+

## Installation

```bash
pip install diagraph
```

## Quickstart

```python
from diagraph import Diagraph, Depends, prompt, llm

openai.api_key = 'sk-<OPENAI_TOKEN>'

@prompt
def tell_me_a_joke():
  return 'Computer! Tell me a joke about tomatoes.'

@prompt
def explanation(joke: str = Depends(tell_me_a_joke)) -> str:
  return f'Explain why the joke "{joke}" is funny.'

dg = Diagraph(explanation).run()
print(dg.result) # 'The joke is a play on words and concepts. There are two main ideas that make it humorous...
dg
```

![Quickstart visualization](https://raw.githubusercontent.com/thekevinscott/Diagraph/main/assets/quickstart.png)

## Usage

[See the usage guide](https://github.com/thekevinscott/Diagraph/blob/main/docs/usage.md).

## License

[MIT](https://github.com/thekevinscott/Diagraph/blob/main/LICENSE)

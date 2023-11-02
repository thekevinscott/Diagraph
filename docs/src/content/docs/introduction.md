---
sidebar_position: 1
---

# Introduction

Diagraph is a tool for orchestrating and iterating on interactions with language models like GPT-4. It assumes the concept of a static graph of interactions and simplifies the process of managing complex interactions with these models. This guide will walk you through the usage of Diagraph for creating and executing interaction graphs.

## Motivation

Diagraph was born out of a desire for a straightforward tool for orchestrating LLM interactions. It aims to simplify the DX without getting in the way.

Diagraph adheres to these principles:

1. Bring Your Own Code - Choose the tools that work for you. Maybe you want to use the `openai` package directly, or you prefer `POST`ing requests to a custom server. It's up to you.
2. Abstract the Graph - Declare dependencies within functions, and Diagraph automatically manages the execution order, parallelization, and error handling. This makes refactoring interactions a breeze and avoids pointless bugs around execution order.
3. Time Travel - Diagraph allows you to inspect and replay interactions from specific points in time. No need to rerun an entire sequence if you need to make adjustments or explore different scenarios. Save money and time.
4. Logs & Parsing - Diagraph provides a consistent approach to handling LLM output. It manages responses, including parsing, synchronous and asynchronous handling, and streaming, removing the drudgery of interacting with LLMs.
5. Visualizations - It can be difficult to grok a complex interaction. Diagraph offers various integrated approaches to visualization:

## Housekeeping

Some housekeeping notes about these docs.

### Live Code Snippets

Throughout the docs, you will see code snippets like the below:

```python preview
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

<!-- <code-button .hotkeys=${['ctrl', 'r']} >
  <sl-icon slot="prefix" name="arrow-clockwise"></sl-icon>
  Reset
</code-button> -->

### LLM

The default LLM in Diagraph is OpenAI. However, the docs use a clientside LLM called Vicuna-7b.

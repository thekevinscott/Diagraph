# Diagraph

A graph for representing LLM interactions.

**This document is _aspirational_; not all functionality has been implemented yet. Diagraph is very much in alpha development**.

## Installation

```
pip install diagraph
```

## Quick Start

```python
import openai
from diagraph import Diagraph, Depends, prompt

openai.api_key = 'sk-<OPENAI_TOKEN>'

def tell_me_a_joke():
  return prompt('Computer! Tell me a joke about tomatoes.')

def explanation(joke: Depends(tell_me_a_joke)) -> str:
  return openai.completion(f'Explain why the given joke is funny: {joke}')

Diagraph(explanation).run().output # Oh I'll tell you
```

## Usage

Start with a function:

```python
def tell_me_a_joke():
  return openai.completion('Computer! Tell me a joke about tomatoes.')

print(tell_me_a_joke()) # Why did the tomato turn red? Because it saw the salad dressing!
```

This is a normal function, but as soon as you wrap it in a Diagraph it gets super powers.

```python
from diagraph import Diagraph

def tell_me_a_joke()
  return openai.completion('Computer! Tell me a joke about tomatoes.')

diagraph = Diagraph(tell_me_a_joke)
```

Single node graphs aren't very useful on their own. Let's demonstrate by defining a graph of interactions that are connected. This example asks for a joke, explains the joke, then tries to make it funnier:

```python
def tell_me_a_joke():
  return openai.completion('Computer! Tell me a joke about tomatoes.')

def explanation(joke: Depends(tell_me_a_joke)) -> str:
  return openai.completion(f'Explain why the given joke is funny: {joke}')

def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> str:
  return openai.completion(f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?')

diagraph = Diagraph(improvement)
```

A Diagraph always receives the terminal node as the argument. (You can have multiple terminal nodes; pass them all in.)

`Depends` indicates to Diagraph that a function has a dependency on another function. Diagraph automatically crawls your function dependencies and builds a graph:

<GRAPH>

_Proposal_: `Depends` should take an optional parameter that defines how the response should be parsed. That way, the function can return an `openai.completion` object, but downstream functions can automatically receive a `str` or whatever format they desire.

You can run a diagraph with `.run()`:

```python
traversal = diagraph.run()
print(traversal.output) # Why did the tomato turn red? Because it saw the salad dressing!
```

A Diagraph is a static representation of the interaction template. Think of it as a recipe.

A Traversal is an execution of that template. Think of it as a meal. A diagraph is a relationship between functions - functions can be LLM interactions, or tool use, or just regular functions - whereas a traversal is that interaction executed, and contains the composed prompts as well as the results.

You can index into a Diagraph:

```python
diagraph[0] # tell_me_a_joke
```

If numeric indices don't float your boat, the functions themselves are valid keys:

```python
diagraph[tell_me_a_joke] # tell_me_a_joke
```

The same is true for a traversal:

```python
traversal[tell_me_a_joke] # tell_me_a_joke
```

In a traversal, you can get the prompt, result, and tokens:

```python
print(traversal[tell_me_a_joke].prompt) # "Computer! 
print(traversal[tell_me_a_joke].result) # "Computer! 
print(traversal[tell_me_a_joke].tokens) # 1234
```

You can also slice a diagraph or traversal:

```python
traversal[0:-1]
```

You can also use functions for slicing:

```python
traversal[tell_me_a_joke:-1]
```

You can also call `len`:

```python
len(traversal) # 3
```

In the case of multiple functions representing a parallel step in the graph, either function can be used as an index.

### Return types

You can do automatic return type validation:

```python
from pydantic import BaseModel

class ImprovementReturnType(BaseModel):
  message: str

def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> ImprovementReturnType:
  return openai.completion(f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?')
```

### Errors

You can handle errors with a decorator:

```python
@error(lambda e: print(e))
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> ImprovementReturnType:
  return openai.completion(f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?')
```

### Time Travel

A traversal contains the whole history of your interaction.

This means you can rerun graphs from an intermediary point:

```python
traversal.run(explanation)

# _or_

traversal[explanation].run()
```

When re-running part of a graph, all upstream nodes remain cached, whereas all downstream nodes are re-executed. Alternatively, you can run a single node by passing the `only` flag:

```python
traversal.run(explanation, only=True)

# _or_

traversal[explanation].run(only=True)
```

In this case, only the `explanation` function will be executed; however, all downstream node caches will be cleared. If you would like to preserve state, make a copy of the traversal with `traversal[:]` prior to execution.

### Control Flows

Diagraphs are meant for statically analyzable interactions. They're not intended to support more complicated control flows like if/else statements, while loops, etc.

Since they're all normal functions, you can implement such behavior yourself:

```python
def the_joke_maker():
  def tell_me_a_joke():
    return openai.completion('Computer! Tell me a joke about tomatoes.')

  def explanation(joke: Depends(tell_me_a_joke)) -> str:
    return openai.completion(f'Explain why the given joke is funny: {joke}')

  def is_it_funny(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> str:
    return openai.completion(f'The given joke is "{joke}". An explanation of the joke is "{explanation}". Is it funny to a kindergartner?')

  diagraph = Diagraph(improvement)
  is_funny = False
  traversal = None
  while is_funny is False:
    if traversal is None:
      traversal = diagraph.run()
    else:
      traversal.run(tell_me_a_joke)
    is_funny = traversal.output

  return traversal[tell_me_a_joke].output
```

You can in turn wrap this function into a Diagraph:

```python
def shakespearify(joke: Depends(the_joke_maker)) -> str:
  return openai.completion(f'rewrite this as shakespeare: {joke}')

Diagraph(shakespearify)
```

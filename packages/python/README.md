# Diagraph

A graph for representing LLM interactions.

> This document is _aspirational_; not all functionality has been implemented yet. Diagraph is very much in alpha development.

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

print(Diagraph(explanation).run().result) # 'The joke is a play on words and concepts. There are two main ideas that make it humorous...
```

## Usage

Start with a function:

```python
def tell_me_a_joke():
  return openai.completion([{ "role": "user", "content": 'Computer! Tell me a joke about tomatoes.' }])

print(tell_me_a_joke()) # Why did the tomato turn red? Because it saw the salad dressing!
```

Diagraph takes functions as arguments.

```python
from diagraph import Diagraph

def tell_me_a_joke():
  return openai.completion('Computer! Tell me a joke about tomatoes.')

diagraph = Diagraph(tell_me_a_joke)
```

Your final function should be the argument.

You can index into a diagraph with the function:

```python
diagraph[tell_me_a_joke]

> def tell_me_a_joke():
>   return openai.completion('Computer! Tell me a joke about tomatoes.')
```

We'll discuss indexing and slicing later.

### `@prompt`

Decorating the function with `@prompt` gives it super powers.

You can leverage the `@prompt` decorator as an alternative to calling your LLM directly (like done above with `openai.completion`). When decorated with a `@prompt` your functions sproutes additional metadata.

#### `.prompt`

You can get back information on the prompt for a function:

```python
from diagraph import Diagraph, prompt

@prompt
def tell_me_a_joke(input: str) -> str:
  return 'Computer! Tell me a joke about {input}.'

diagraph = Diagraph(tell_me_a_joke)
print(diagraph[tell_me_a_joke].prompt()) 
# 'Computer! Tell me a joke about {input}.'
```

You can pass arguments to `prompt()` to get a parsed prompt:

```python
print(diagraph[tell_me_a_joke].prompt('tomatoes')) 
# 'Computer! Tell me a joke about tomatoes.'
```

You can pass keyword arguments too, in case you have multiple string arguments and don't want to remember the defined order:

```python
print(diagraph[tell_me_a_joke].prompt(input='tomatoes')) 
# 'Computer! Tell me a joke about tomatoes.'
```

#### `.tokens`

You can also get token information for the prompt. If you run without an argument it will return token information sans string replacements:

```python
print(diagraph[tell_me_a_joke].tokens()) # 7
```

You can provide arguments to get tokens for the parsed string:

```python
print(diagraph[tell_me_a_joke].tokens(input='tomatoes')) # 8
```

## Building a Graph

Diagraphs are intended for multi-step LLM interactions. Let's demonstrate by defining a graph of dependent interactions.

This example asks for a joke, explains the joke, then tries to make it funnier:

```python
@prompt
def tell_me_a_joke():
  return 'Computer! Tell me a joke about tomatoes.'

@prompt
def explanation(joke: Depends(tell_me_a_joke)) -> str:
  return f'Explain why the given joke is funny: {joke}'

@prompt
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> str:
  return f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?'

diagraph = Diagraph(improvement)
```

A Diagraph always receives the final function (referred to as the terminal node) as the argument. (You can pass multiple functions, each a terminal node.)

You define your dependency as a type with `Depends`. `Depends` indicates to Diagraph that a function has a dependency on another function. Diagraph automatically crawls your function dependencies and builds a graph:

<IMAGE_OF_GRAPH>

You can run a diagraph with `.run()`:

```python
traversal = diagraph.run()
print(traversal.result) # Why did the tomato turn red? Because it saw the salad dressing!
```

A Diagraph is a static representation of the interaction template. Think of it as a recipe.

A Traversal is an execution of that template. Think of it as a cooked meal. A diagraph is a relationship between functions - functions can be LLM interactions, or tool use, or just regular functions - whereas a traversal is that interaction executed, and contains the composed prompts as well as the results.

### Indices and Slicing

#### Indexing

You can index into a Diagraph:

```python
diagraph[0] # (tell_me_a_joke, )
```

Using an integer index returns a `tuple` representing all nodes for a specific depth (or `None`, if an invalid integer). Diagraph automatically hoists nodes to the top of the graph and executes them greedily and in parallel.

You can also index with negative numbers:

```python
diagraph[-1] # returns a tuple of terminal nodes
```

You can also index with a function:

```python
diagraph[tell_me_a_joke] # tell_me_a_joke
```

Using a function index always returns a `DiagraphNode` representing the function. 

A `DiagraphNode` decorates the function with additional properties, including `.prompt` and `.tokens` (if the function has been decorated with `@prompt`) as well as `.result` (if within an executed Traversal).

The same indexing strategies work for a Traversal:

```python
traversal[tell_me_a_joke] # tell_me_a_joke
```

In a traversal, you can get the result for a specific function:

```python
print(traversal[tell_me_a_joke].tokens) # 1234
```

#### Slicing

You can also slice a diagraph or traversal:

```python
traversal[1:] # Give me the graph without the first layer of nodes
```

You can also use functions for slicing:

```python
traversal[tell_me_a_joke:-1]
```

Functions and integers slicing work slightly differently.

If you slice with two functions, you get a subgraph for the graph connecting the two nodes.

<EXAMPLE_IMAGE>

If you slice with two integers, you get all the layers for those depths:

<EXAMPLE_IMAGE>

You can use a combination of function and integer in your slice. So for example:

<EXAMPLE_IMAGE>

#### `length`
You can also call `len`:

```python
len(traversal) # 3
```

`len` will get back the total number of layers, _not_ the total number of nodes. If you want the total number of nodes, do:

```python
len(traversal.nodes)
```

### Return types

You can do automatic return type validation:

```python
from pydantic import BaseModel

class ImprovementReturnType(BaseModel):
  message: str

@prompt
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> ImprovementReturnType:
  return f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?'
```

Responses are automatically parsed in the following manner:

- `str`: Returns the LLM response as plain text
- PydanticModel - returns a structured response, likely a response from a `functions` call. (If there is additional content, that will be ignored)
- tuple(Optional[str], Optional[PydanticModel]) - Both content and function call, if they are present.

Responses can also be _functions_:

```python
from pydantic import BaseModel

def is_it_text(joke: str):
  if isinstance(joke, str):
    return joke

  raise Exception('Invalid input!')

@prompt
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> is_it_text:
  return f'The given joke is "{joke}".
```

Return types can themselves be calls to an LLM, and will be automatically rolled up into the Diagraph:

```python
from pydantic import BaseModel

def raise_if_not_funny(is_funny: str):
  if [is_funny not in ['yes', 'no']]:
    raise Exception('Invalid Response')

  if is_funny == 'no':
    raise Exception('Not funny')

  pass

@prompt
def is_it_funny(joke: str) -> raise_if_not_funny:
  return 'Is this joke funny? Respond with yes or no: {joke}'

@prompt
def joke() -> is_it_funny:
  return f'Tell me a joke'
```

You can use `@Depends` in a return type; Diagraph will build the graph and raise if the graph cannot be solved.

### Errors

You can handle errors with a decorator:

```python
def error_handler(error):
  pass

@prompt(error=error_handler)
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> ImprovementReturnType:
  return f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?'
```

An `error` can be of the following types:

- `ReturnTypeValidationFailure` - the return type could not be satisfied

### Logs

You can handle streaming logs as an argument to `@prompt`:

```python
@prompt(log=lambda event, chunk, fn: print(chunk))
def improvement(joke: Depends(tell_me_a_joke), explanation: Depends(explanation)) -> ImprovementReturnType:
  return f'The given joke is "{joke}". An explanation of the joke is "{explanation}". What would make the joke funnier?'
```

- `event` is an enum that can be `start`, `data`, or `end`.
- `chunk` is the bit of text returned from the LLM. Will be None for `start` and `end`.
- `fn` is the node being operated upon.

### Time Travel & Replay

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

In this case, only the `explanation` function will be executed; however, all downstream node caches will be cleared. 

`run()` returns a new instance of a traversal:

```
traversal2 = traversal[explanation].run()
```

You can also specify indices:

```python
traversal[-2].run()
```

This will re-execute all nodes for a given depth.

### Control Flows

Diagraphs are meant for statically analyzable interactions. They're not intended to support more complicated control flows like if/else statements, while loops, etc.

However, since everything is just a Python function, you can implement such behavior yourself:

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

## Changing LLM model

```python
gpt4 = OpenAI(model='gpt-4', temperature=0.2)

@prompt(llm=gpt4)
def fn():
  return 'tell me a joke'
```

## Integrations

- Weights & Biases
- Mermaidjs
- Magnetic
- Marvin
- LLM (Simon's library)
- Langchain
- LlamaIndex


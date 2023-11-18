# Usage

This is a guide on how to use Diagraph.

## Building a Diagraph

Every Diagraph starts with a function:

```python
from diagraph import Diagraph
def foo():
  return 'foo'

Diagraph(foo)
```

### Function Dependencies

To express a dependency, specify it with `Depends`:

```python
from diagraph import Diagraph, Depends
def foo():
  return 'foo'

def bar(foo = Depends(foo)):
  return 'bar'

Diagraph(bar)
```

You pass in the _terminal_ node(s) in the chain to the `Diagraph`.

![Example of a foo-bar diagraph](https://raw.githubusercontent.com/thekevinscott/Diagraph/main/assets/foobar.png)

## Running a Diagraph

Run a Diagraph by calling `.run()`:

```python
dg = Diagraph(bar)
dg.run()
```

### Concurrency

Nodes are run _greedily_ and _concurrently_ when possible:

- **Greedily** means functions are run as soon as all of that function's dependencies are satisfied.
- **Concurrently** means that any nodes running at the same _level_ of depth in the graph will run at the same time.

Consider this Diagraph:

```python
def a():
  return 'a'

def b():
  return 'b'

def c(a = Depends(a), b = Depends(b)):
  return 'c'

dg = Diagraph(c)
```

![Example of two nodes that point to a single terminal](https://raw.githubusercontent.com/thekevinscott/Diagraph/main/assets/abc.png)

Nodes `a` and `b` will execute concurrently, while `c` will wait for both nodes to complete before executing.

### Replay a graph

You can replay a Diagraph from a specific function. Consider the Diagraph from above.

To rerun just the `c` function, you could do:

```python
dg[c].run()
```

You could also rerun the left branch by specifying `a`. Diagraph will run function `a` and then `c`, but _not_ function `b`; instead, `c` will receive the cached result for `b` from the first run of the Diagraph.

```python
dg[a].run()
```

Diagraph will build the subgraph emanating from the specified node and run it. You can specify multiple nodes:

```python
dg[a, b].run()
```

Diagraph will run the subgraph emanating from the group of multiple nodes.

Integer indices are also available as a shorthand:

```python
dg[0].run() # run the graph from the first layer (starting layer) of nodes
dg[1].run() # run the graph from the second layer of nodes
dg[-1].run() # run just the terminal layer of nodes
```

### Arguments

Arguments can be passed to `.run()`, and will be forwarded to every function:

```python
def foo(input: str):
  return f'My input: "{input}"'

Diagraph(foo).run('some input') # My input: "some input"
```

Multiple arguments can be specified, along with keyword arguments:

```python

def foo(input1: str, input2: int, keyword_arg='some-default'):
  return f'Inputs: "{input1}" "{input2}" {keyword_arg}'

Diagraph(foo).run('input1', 'input2', keyword_arg='input3') # Inputs: "input1" "input2" "input3"
```

### Editing

You can edit the nodes of a Diagraph, and specifically can edit a node's function, prompt, or result.

Editing a node will automatically clear all downstream nodes' values. 

#### Editing a Result

Set a specific cached function's result:

```
dg[foo].result = 'Some fake result'
```

Any nodes downstream of `foo` will receive `'Some fake result'` as `foo`'s input.

#### Editing a Prompt

If a node is decorated with [`@prompt` (see prompt section)](#prompt), you can modify the node's _prompt_:

```
dg[foo].prompt = 'Some fake prompt'
```

If `prompt` is edited, upon running the function will not be executed, but the associated LLM will be called with the specified prompt.

#### Editing a Function

You can change the function defined for a node:

```
def new_foo():
  return 'I am a new function'

dg[foo] = new_foo
```

**Important**: the original function, in this example `foo`, remains the "key" of the node. Ensure you keep a reference to the original function around.

## `@prompt`

Diagraph accepts regular functions, but functions decorated with the `@prompt` decorator sprout superpowers.

Decorate a function with `@prompt` and return a plain string:

```python
@prompt
def formalize_query(user_query:str):
  return f'The user has provided the following query: {user_query}. Formalize it, fill it out, etc.'
```

The returned string is automatically passed as a prompt to the LLM (default is OpenAI GPT-3.5-turbo).

You can also return a more complicated structure that matches the API of whichever LLM you are calling. For instance, to specify a system prompt for OpenAI:

```
@prompt
def formalize_query(user_query:str):
  return {
    "messages": [{
      "role": "system",
      "content": "My message"
    }]
  }
```

Or to make a function call:

```
@prompt
def formalize_query(user_query:str):
  return {
    "messages": [{
      "role": "user",
      "content": "My message"
    }],
    "functions": ...
  }
```

### `@prompt` arguments

`@prompt` accepts `log`, `llm`, and `error`, all optional, as arguments:

```python
from diagraph import OpenAI

def handle_log(event, data):
    if event == 'start':
        print('*' * 20)
    elif event == 'end':
        print(f'\n')
    else:
        print(data, end='')

def error(e: Exception):
  print(e)
  raise e


@prompt(
  llm=OpenAI('gpt-4'),
  log=handle_log,
  error=error_handler
)
```

These same arguments can be passed to the Diagraph constructor as well, in which case they apply to all the nodes in a Diagraph:

```python
Diagraph(terminal_node, llm=OpenAI('gpt-4'), error=error_handler, log=handle_log)
```

They can also be set at a global level:

```python
Diagraph.llm = OpenAI('gpt-4')
Diagraph.error=error_handler
Diagraph.log=handle_log
```

`llm` and `log` defined at the node level take precedence over Diagraph level, which takes precedence over global levels.

`error` will first be called at the node level (if defined), then the Diagraph level (if defined), and finally at the global level (if defined).

### Handling Errors

Errors can come in a number of different formats.

There can be LLM-related errors, like an authentication issue, billing issue, network issue, etc. These are exposed as whatever exception is raised by the core LLM library.

There can also be validation exceptions, raised in conjunction with result coercion (see next section).

The error handler receives the error:

```python
def error_handler(e: Exception):
  pass
```

The error handler has three choices:

1. Return a value. This returned value will be treated as the result of the original function.
2. Raise an exception
3. Re-run the function the error handler is attached to.

You can specify to rerun the function with:

```python
def error_handler(e: Exception, rerun):
  return rerun()
```

You can also supply additional arguments:

```python
def error_handler(e: Exception, rerun_fn):
  return rerun_fn('1', '2', kw='arg')
```

A common pattern I use is to pass a numeric retry index, to allow for exiting after n failed attempts.

When a function runs into an error that raises an exception, that node and all its descendants halt. Any unrelated nodes will continue processing.

Exceptions can be read by examining the function's `error`:

```
dg[fn].error
```

If an error handler returns a valid value (does not raise an Exception) no error will be recorded, and instead the error handler's result is assigned to the node's `.result`.

---
sidebar_position: 1
---

# Building a Diagraph

Diagraphs operate on functions:

```python
from diagraph import Diagraph

def my_fn():
  return 'I have been run'

dg = Diagraph(my_fn)

```

You can run a diagraph with `run()`:

```python
print(dg.run().result) # 'I have been run'
```

This will execute the function `my_fn`.

## Specifying function dependencies

You can declare a dependency from one function to another with `Depends`:

```python
from diagraph import Diagraph, Depends

def first():
  return '1st fn'

def second(first: str = Depends(first)):
  return f'2nd fn, but my input is: {first}'

dg = Diagraph(second)

print(dg.run().result) # '2n fn, but my input is: 1st fn'
```

This graph looks like:

>>>> blah <<<<

Each function can declare its own independent dependencies, and Diagraph will automatically build the execution graph for you:

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

A Diagraph always takes the final function (referred to as the terminal node) as the argument. You can pass multiple terminal nodes, and the `result` will be a tuple containing the terminal node's results.


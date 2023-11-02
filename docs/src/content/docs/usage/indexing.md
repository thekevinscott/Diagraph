---
sidebar_position: 2
---

# Indexing

You can index into a Diagraph via functions or integers.

## Function indexing

If you define a multistep diagraph:

```python
from diagraph import Diagraph, Depends

def first():
  return '1st fn'

def second(first: str = Depends(first)):
  return f'2nd fn, but my input is: {first}'

dg = Diagraph(second)

print(dg.run().result) # '2n fn, but my input is: 1st fn'
```

You can access specific nodes by indexing by function:

```python
print(dg[first].result) # '1st fn'
print(dg[second].result) # '2n fn, but my input is: 1st fn'
```

If you'd prefer not to use functions as indices, you can force string keys with:

```
dg = Diagraph(second, use_string_keys=True)
```

This will use the function's name (the value returned via `fn.__name__`) as the node key:

```
dg['second'] == second
```

If you are using string keys, ensure your functions have unique names.

## Indexing by integer

You can also index into a diagraph by integer.

```python
from diagraph import Diagraph, Depends

def first():
  return '1st fn'

def second(first: str = Depends(first)):
  return f'2nd fn, but my input is: {first}'

dg = Diagraph(second)

dg[0] # first
dg[1] # second
```

In the case that two nodes run in parallel, an integer index will return a tuple. Consider the following graph:

```python
from diagraph import Diagraph, Depends

def left_node():
  pass

def right_node():
  pass

def terminal(left_node = Depends(left_node), right_node = Depends(right_node)):
  pass

dg = Diagraph(terminal)

dg[0] # (left_node, right_node)
```

Here, `left_node` and `right_node` are dependencies of the `terminal` function, and will run concurrently. They are considered a single layer.

```
dg[1] # terminal
```

The final layer is the terminal layer, a single node.

### Negative indexing

Like other Python data structures, you can also negatively index, which can be useful for fetching from the end of the graph:

```python
dg[-1] # terminal
dg[-2] # left_node, right_node
```


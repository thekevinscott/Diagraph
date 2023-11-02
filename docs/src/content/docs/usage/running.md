---
sidebar_position: 4
---

# Running a Graph

You run a graph with `.run()`

```python
from diagraph import Diagraph, prompt

@prompt
def tell_me_a_joke(input: str) -> str:
    return 'Computer! Tell me a joke about {input}.'

dg = Diagraph(tell_me_a_joke).run('tomatoes')
print(dg.result)  # Why did the tomato turn red? Because it saw the salad dressing!
```

## Passing inputs

## Rerunning

## Editing

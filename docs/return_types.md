# Return Types

_This document is aspirational. I'm still working out the kinks, and none of this has been implemented yet._

### Result coercion

LLMs don't always respond the way you want them to. You can specify return types to automatically coerce your results into your desired format (or raise an Exception if coercion is impossible).

You specify a result coercion by specifying a return type on a function decorated with `@prompt`:

```
@prompt
def language_checker(sentence: str) -> bool:
  return f'Is this sentence in French: {sentence}'
```

The LLM does the heavy lifting of answering whether a sentence is in French, but Diagraph coerces the resulting output as a `True`/`False` boolean.

#### Supported Types

You can specify the following types:

- `str`
- `int`
- `float`
- `bool`
- `list`
- `tuple`

Diagraph will first attempt to coerce the results locally, and if it cannot, will reach out to an LLM for help.

#### Pydantic types

You can also specify a Pydantic type as a response:

```python
from pydantic import BaseModel

class Response(BaseModel):
  functions: []

def foo() -> Response
  return 'functions!'
```

This can be useful for type checking the function return from an OpenAI call.

#### MarvinAI

MarvinAI automatically coerces into a pydantic model. You can specify a MarvinAI model as a return type:

```python
def foo() -> SomeMarvinModel:
  return 'hooza'
```

#### Functions

You can return a function as a return type:

```python
def is_valid_chess_move(move: str):
  Engine.check(move)

@prompt
def make_a_chess_move() -> is_valid_chess_move:
  return 'Make an opening chess move'
```

Functions can raise exceptions, which will propagate to the error handler:

```python
def is_valid_chess_move(move: str):
  if Engine.check(move) is False:
    raise Exception('Invalid move')

def error_handler(e: Exception):
  if e == 'Invalid move':
    # do something
  else:
    raise e

@prompt(error=error_handler)
def make_a_chess_move() -> is_valid_chess_move:
  return 'Make an opening chess move'
```

Functions can _themselves_ be decorated with `@prompt`:

```python
def raise_if_false(funny: str):
  if funny != 'y':
    raise NotFunny()

@prompt
def is_funny(the_joke: str) -> raise_if_false:
  return f'Here is a joke: "{the_joke}". Is it funny? Reply with y/n'.

class NotFunny(Exception):
  pass

def error_handler(e: Exception):
  if isinstance(e, NotFunny)
    # rerun
  else:
    raise e

@prompt(error=error_handler)
def tell_me_a_joke(topic: str) -> is_funny:
  return f'Tell me a joke about {topic}'

Diagraph(tell_me_a_joke).run('chickens')
```


# Examples

## Generating SQL

Consider a scenario where you need an LLM to generate SQL code based on a user query, incorporating information about table schemas. Traditionally, you might structure it like this:

```python
def fetch_table_schemas():
  # fetch table schemas from the local database
  ...

def prompt_to_generate_sql(user_query: str):
  table_schemas = fetch_table_schemas()
  return openai.ChatCompletion.create(
    messages=[{
      "role": "user", 
      "content": f"Generate a SQL query for the user query: {user_query}. The table schemas are: {table_schemas}"
    }]
  )

return prompt_to_generate_sql('Fetch all active users for the past 30 days')
```

Now, imagine you want to run another function concurrently: you would have to rewrite your `prompt_to_generate_sql` function to call both dependent functions concurrently, ensuring you handle error cases, etc.

Diagraph lets you express your functions as a graph:

```python
def fetch_table_schemas():
  # fetch table schemas from the local database
  ...

def generate_sql(user_query: str, table_schemas = Depends(fetch_table_schemas)):
  return openai.ChatCompletion.create(
    messages=[{
      "role": "user", 
      "content": f"Generate a SQL query for the user query: {user_query}. The table schemas are: {table_schemas}"
    }]
  )

print(Diagraph(generate_sql).run('Fetch me all active users for the past 30 days').result)
```
!['Visualization of Diagraph](assets/a.png)

Here are some key points:

1. Dependencies are expressed by passing them as parameters using `Depends(fn)`, a familiar pattern if you've used FastAPI.
2. `Diagraph(fn)` defines the graph. You provide the terminal nodes (final functions). You can pass multiple terminal nodes and get a tuple in return.
3. `run(*args)` accepts user input passed to each function. Multiple arguments can be provided.

Expressing dependencies as a graph allows for easy rearrangement of execution order. Suppose you want to add a step to formalize a user's query. Make it a dependency for `fetch_table_schemas`:
to `fetch_table_schemas`

```python
def formalize_query(user_query:str):
  return f'The user has provided the following query: {user_query}. Formalize it, fill it out, etc.'

def fetch_table_schemas(formalized_query = Depends(formalize_query)):
  # fetch table schemas from the local database
  ...
```

!['Visualization of Diagraph with extra function](assets/b.png)

Diagraph automatically inserts the new function at the top of the graph. If `fetch_table_schemas` doesn't need the formalized query, simply move the dependency to `generate_sql`:


```python
def formalize_query(user_query:str):
  return f'The user has provided the following query: {user_query}. Formalize it, fill it out, etc.'

def fetch_table_schemas():
  # fetch table schemas from the local database
  ...

def generate_sql(user_query: str, formalized_query = Depends(formalize_query), table_schemas = Depends(fetch_table_schemas)):
  ...
```

!['Visualization of Diagraph with extra function](assets/c.png)

Now the first two functions execute concurrently, and the final `generate_sql` query receives both functions' results as arguments.

## Re-execution

Encountering a syntax error at the end of a long chain of LLM interactions can be exasperating.

Diagraph comes to the rescue by enabling selective re-execution of parts of your graph, leveraging cached results from prior runs. Consider the following example:

```python
def formalize_query(user_query:str):
  return f'The user has provided the following query: {user_query}. Formalize it, fill it out, etc.'

def fetch_table_schemas():
  # fetch table schemas from the local database
  ...

def generate_sql(user_query: str, formalized_query = Depends(formalize_query), table_schemas = Depends(fetch_table_schemas)):
  ...

dg = Diagraph(generate_sql)
```

!['Visualization of Diagraph with extra function](assets/c.png)

Assume both `formalize_query` and `fetch_table_schemas` executed successfully, but `generate_sql` encountered a failure. Rerun that specific function with:

```python
dg[generate_sql].run()
```

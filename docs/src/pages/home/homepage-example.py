from typing import Annotated
from diagraph import Diagraph, Depends

def tell_me_a_joke():
    return 'Computer! Tell me a joke'

# def explain_that_joke(the_joke: str = Depends(tell_me_a_joke)):
def explain_that_joke(the_joke: Annotated[str, Depends(tell_me_a_joke)]):
    return f'Explain this joke: {the_joke}'

Diagraph(explain_that_joke).run().result

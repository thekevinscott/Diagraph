from ..utils.annotations import get_dependency, is_annotated
from ..classes.types import Node, Result


def run_node(node: Node, results: dict[Node, Result], *input_args, **kwargs):
    args = []
    arg_index = 0
    for key, val in node.__annotations__.items():
        if key != "return":
            if is_annotated(val):
                dep = get_dependency(val)
                args.append(results.get(dep))
            else:
                args.append(input_args[arg_index])
                arg_index += 1
    return node(*args, **kwargs)

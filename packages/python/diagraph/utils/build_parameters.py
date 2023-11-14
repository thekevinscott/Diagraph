from __future__ import annotations
import inspect
from typing import Any
from ..classes.types import Fn
from .depends import Depends

from .annotations import get_dependency, is_annotated


def build_parameters(diagraph, fn: Fn, input_args: tuple) -> list[Any]:
    args = []
    arg_index = 0
    encountered_star = False
    for parameter in inspect.signature(fn).parameters.values():
        # Depends can be passed as Annotated[str, Depends]
        if is_annotated(parameter.annotation):
            print("Deprecated")
            dep: Fn = get_dependency(parameter.annotation)
            key_for_fn = diagraph.fns.inverse(dep)
            try:
                args.append(diagraph.results[key_for_fn])
            except Exception as e:
                raise Exception(
                    f"Failed to get saved result for fn {key_for_fn}, at parameter {parameter}: {e}"
                )
        # Depends can be passed as arg: str = Depends(dep)
        # Regular args can be passed as :str = 'foo'
        elif parameter.default is not None and parameter.default is not inspect._empty:
            if isinstance(parameter.default, Depends):
                dep: Fn = parameter.default.dependency
                try:
                    key_for_fn = diagraph.fns.inverse(dep)
                except Exception:
                    raise Exception(
                        f"No function has been set for dep {dep}. Available functions: {diagraph.fns}"
                    )
                try:
                    args.append(diagraph.results[key_for_fn])
                except Exception as e:
                    raise Exception(f"Failed to get result for {key_for_fn}: {e}")
            else:
                if arg_index > len(input_args) - 1:
                    args.append(parameter.default)
                else:
                    args.append(input_args[arg_index])
                    arg_index += 1
        elif not str(parameter).startswith("*"):
            if encountered_star:
                raise Exception(
                    "Found arguments defined after * args. Ensure *args and **kwargs come at the end of the function parameter definitions."
                )
            if arg_index > len(input_args) - 1:
                raise Exception(
                    f'No argument provided for "{parameter.name}" in function {fn.__name__}. This indicates you forgot to call ".run()" with sufficient arguments.'
                )
            args.append(input_args[arg_index])
            arg_index += 1
        else:
            encountered_star = True

            if arg_index < len(input_args):
                for arg in input_args[arg_index:]:
                    args.append(arg)
    return args

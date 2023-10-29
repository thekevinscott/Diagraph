from ..classes.types import Fn


def validate_node_ancestors(nodes: tuple[Fn]):
    for node in nodes:
        for ancestor in node.ancestors:
            if ancestor.result is None:
                raise Exception(
                    "An ancestor is missing a result, run the traversal first"
                )

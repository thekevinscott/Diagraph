from ..classes.diagraph_node import DiagraphNode
from ..classes.diagraph_layer import DiagraphLayer


def validate_node_ancestors(layer: tuple[DiagraphNode] | DiagraphLayer):
    for node in layer:
        for ancestor in node.ancestors:
            if ancestor.result is None:
                raise Exception(
                    "An ancestor is missing a result, run the traversal first"
                )

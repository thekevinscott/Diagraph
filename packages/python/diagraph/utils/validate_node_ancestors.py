from ..classes.diagraph_layer import DiagraphLayer
from ..classes.diagraph_node import DiagraphNode


def validate_node_ancestors(layer: DiagraphLayer):
    for node in layer:
        for ancestor in node.ancestors:
            if ancestor.result is None:
                raise Exception(
                    "An ancestor is missing a result, run the traversal first"
                )

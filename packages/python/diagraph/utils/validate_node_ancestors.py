from ..classes.diagraph_node import DiagraphNode
from ..classes.diagraph_node_group import DiagraphNodeGroup


def validate_node_ancestors(layer: tuple[DiagraphNode] | DiagraphNodeGroup):
    for node in layer:
        for ancestor in node.ancestors:
            if ancestor.result is None:
                raise Exception(
                    "An ancestor is missing a result, run the traversal first"
                )

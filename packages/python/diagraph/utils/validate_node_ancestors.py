from ..classes.diagraph_node import DiagraphNode
from ..classes.diagraph_node_group import DiagraphNodeGroup

def validate_node_ancestor(node: DiagraphNode):
    if node.result is None:
        raise Exception(
            "An ancestor is missing a result, run the traversal first"
        )
    

def validate_node_ancestors(node_group: DiagraphNodeGroup):
    [validate_node_ancestor(ancestor) for node in node_group for ancestor in node.ancestors]

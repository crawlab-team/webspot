from webspot.graph.graph_loader import GraphLoader
from webspot.graph.models.node import Node


def get_node_inner_text(g: GraphLoader, n: Node) -> str:
    texts = []
    for c in g.get_node_children_recursive_by_id(n.id):
        if c.text:
            texts.append(c.text)
    return ' '.join(texts)

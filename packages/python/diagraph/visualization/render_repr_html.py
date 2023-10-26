import json
import networkx as nx
from json import load
from pkg_resources import resource_stream


def load_js() -> str:
    return load(resource_stream("diagraph", "visualization/frontend/dist/diagraph.js"))


def render_repr_html(G):
    graph = {}

    links = nx.node_link_data(G)["links"]
    if len(links) == 0:
        for node in nx.topological_sort(G):
            graph[node.__name__] = []
    else:
        for link in links:
            source = link.get("source").__name__
            target = link.get("target").__name__
            if graph.get(target) is None:
                graph[target] = []
            graph[target].append(source)
        if len(graph.keys()) == 0:
            raise Exception("Empty graph")
    graph = json.dumps(graph)

    fe = load_js()

    return f"""
        <script type="module">{fe}</script>
        <div style="min-height: 600px; width: 100%; display: flex; flex: 1;">
         <diagraph-template graph='{graph}' style="position: absolute;">
         </diagraph-template>
         </div>
         """

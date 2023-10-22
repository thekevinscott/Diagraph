import dagre from 'dagre';
// Create a new directed graph 

export const buildGraph = (graph: Record<string, string[]>, width: number, height: number) => {
  const g = new dagre.graphlib.Graph();

  // Set an object for the graph label
  g.setGraph({});

  // Default to assigning a new object as a label for each new edge.
  g.setDefaultEdgeLabel(function () { return {}; });

  // Add nodes to the graph. The first argument is the node id. The second is
  // metadata about the node. In this case we're going to add labels to each of
  // our nodes.
  const nodes = new Set();
  Object.entries(graph).forEach(([key, edges]) => {
    nodes.add(key);
    edges.forEach(edge => {
      nodes.add(edge);
      g.setEdge(key, edge);
    })
  });

  nodes.forEach(key => {
    g.setNode(key, {
      label: key,
      // width: width, height: height,
    });
  });
  return g;
};

export const getLayout = (g) => {
  dagre.layout(g);
  return {
    nodes: g.nodes(),
    edges: g.edges(),
  }
  // g.nodes().forEach(function (v) {
  //   console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
  // });
  // g.edges().forEach(function (e) {
  //   console.log("Edge " + e.v + " -> " + e.w + ": " + JSON.stringify(g.edge(e)));
  // });

};

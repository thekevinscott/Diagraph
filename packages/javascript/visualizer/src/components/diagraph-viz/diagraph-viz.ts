import { LitElement, PropertyValueMap, css, html } from 'lit';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { customElement, property, state } from 'lit/decorators.js';
import { buildGraph, getLayout } from '../../utils/graph.js';
import styles from './diagraph-viz.css?inline';
import { MouseController } from '../../controllers/mouse-controllers.js';
import { parseStyles } from '../../utils/parse-styles.js';
import { styleMap } from 'lit/directives/style-map.js';
import '@internals/code-editor';
import { DiagraphNode, DiagraphInternalNode } from '../diagraph-node/diagraph-node.js';

export const name = 'diagraph-viz';

export const width = 200;
export const height = 44.5;
export const GAP = 80;

export class DiagraphViz extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = [
    parseStyles(styles),
  ];

  private mouseController = new MouseController(this);

  private nodes: Record<string, DiagraphNode> = {};
  private layers: Record<number, string[]> = {};

  private g = {}

  @state()
  private layout?: ReturnType<typeof getLayout>;

  handleSlotchange(e) {
    const graph = {};
    const layers: Record<string, Set<string>> = {};
    e.target.assignedNodes({ flatten: true }).filter(node => node.tagName === 'DIAGRAPH-NODE').forEach((nodeEl: HTMLElement) => {
      try {
        const outEdges: string[] = JSON.parse(nodeEl.getAttribute('edges'));
        graph[nodeEl.id] = outEdges;
        const node: DiagraphNode = {
          depth: parseInt(nodeEl.getAttribute('depth'), 10),
          name: nodeEl.getAttribute('id'),
          fn: nodeEl.getAttribute('fn').split('\\n').join('\n'),
          prompt: nodeEl.getAttribute('prompt').split('\\n').join('\n'),
          result: nodeEl.getAttribute('result').split('\\n').join('\n'),
          outEdges: new Set(outEdges),
          inEdges: new Set(),
        };
        if (!layers[node.depth]) {
          layers[node.depth] = new Set();
        }
        layers[node.depth].add(nodeEl.id);
        this.nodes[nodeEl.id] = node;
      } catch (err) {
        console.log('Problem parsing node', nodeEl.getAttribute('edges'))
      }
    });
    for (const [id, node] of Object.entries(this.nodes)) {
      for (const edge of node.outEdges) {
        this.nodes[edge].inEdges.add(id);
      }
    }
    Object.entries(layers).forEach(([key, value]) => {
      this.layers[key] = [...value];
    });

    this.g = buildGraph(graph, width, height);
    this.layout = getLayout(this.g);
  }

  get columns() {
    return Math.max(...Object.values(this.layers).map(layer => layer.length));
  }

  nodeRefs: Record<string, Ref<DiagraphInternalNode>> = {};
  renderNode = (key: string, index: number) => {
    const node = this.nodes?.[key];
    if (!node) {
      return null;
    }

    if (this.nodeRefs[key] === undefined) {
      this.nodeRefs[key] = createRef<DiagraphInternalNode>();
    }

    const style = styleMap({
      maxWidth: `calc(${100 / this.columns}% - (var(--gap)))`,
    });

    return html`
      <diagraph-internal-node index=${index} .layers=${this.layers} ref=${ref(this.nodeRefs[key])} id=${key} .node=${node} style=${style}></diagraph-internal-node>
    `;
  }

  getNode(id: string): DiagraphInternalNode {
    const node = this.nodeRefs[id]?.value;
    if (!node) {
      throw new Error(`No node found for id ${id}`)
    }
    return node;
  }


  renderEdge = (edge) => {
    const { v: to, w: from } = edge;

    return html`
      <diagraph-edge .host=${this} from=${from} to=${to}></diagraph-edge>
    `;
  }

  render() {
    const { layout, mouseController: { delta } } = this;
    if (!layout) {
      return html`...
        <slot @slotchange=${this.handleSlotchange}></slot>
       `;
    }
    const style = styleMap({
      transform: `translate(${delta.x}px, ${delta.y}px)`,
      '--columns': this.columns,
      '--gap': `${GAP}px`,
      // '--node-width': `${this.nodeWidth}fr`,
    });
    const layers = Object.entries(this.layers).sort(([a], [b]) => parseInt(a, 10) - parseInt(b, 10)).map(([key, value]) => value);
    const minWidth = this.columns * 400 + (GAP * (this.columns - 0));
    return html`
      <div id="container" style="${style}">
        <div id="nodes" style=${styleMap({ 'min-width': `${minWidth}px` })}>
          ${layers.map(layer => html`
          <div class="node-layer" style=${styleMap({ minWidth, '--justify-content': layer.length === 1 ? 'center' : 'space-between' })}>
            ${layer.map(this.renderNode)}
          </div>
          `)}
        </div>
        <div id="edges">
          ${this.layout?.edges?.map(this.renderEdge)}
        </div>
        <slot @slotchange=${this.handleSlotchange}></slot>
      </div>
    `;
  }
}

// ${this.layout?.nodes.map(key => html`
//   <diagraph-node key=${key} .node=${this.g.node(key)} @click=${() => this.recalculate(key, g.node(key))}></diagraph-node>
// `)}
// ${this.layout?.edges.map(key => html`
//   <diagraph-edge offsetX=${width} offsetY=${height} .edge=${this.g.edge(key)}></diagraph-edge>
// `)}

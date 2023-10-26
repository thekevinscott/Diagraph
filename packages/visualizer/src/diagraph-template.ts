import { LitElement, PropertyValueMap, css, html } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { buildGraph, getLayout } from './graph';

export const width = 200;
export const height = 44.5;

@customElement('diagraph-template')
export class DiagraphTemplate extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = css`
    :host {
      width: 100%;
      min-height: 600px;
      flex: 1;
      display: flex;
      position: relative;
    }
  `;

  @state()
  layout?: any;

  start = { x: 0, y: 0 };

  @state()
  delta = { x: 0, y: 0 };

  _handleMouseDown = (e) => {
    this.start = { x: e.clientX - this.delta.x, y: e.clientY - this.delta.y };
    this.addEventListener('mousemove', this._handleMouseMove);
    this.addEventListener('mouseup', this._handleMouseUp);
  }

  _handleMouseMove = (e) => {
    this.delta = { x: e.clientX - this.start.x, y: e.clientY - this.start.y };
    // console.log(this.delta);
  }

  _handleMouseUp = () => {
    this.removeEventListener('mousemove', this._handleMouseMove);
    this.removeEventListener('mouseup', this._handleMouseUp);
  }

  @state()
  g = {}

  @property()
  graph!: string;

  protected updated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    if (_changedProperties.has('graph') && this.graph) {
      console.log(this.graph)
      this.g = buildGraph(JSON.parse(this.graph), width, height);
      this.layout = getLayout(this.g);
      // this.g.nodes().forEach(function (v) {
      //   console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
      // });
    }
  }

  connectedCallback(): void {
    super.connectedCallback();
    this.addEventListener('mousedown', this._handleMouseDown);
  }

  disconnectedCallback() {
    this.removeEventListener('mousedown', this._handleMouseDown);
    this.removeEventListener('mousemove', this._handleMouseMove);
    this.removeEventListener('mouseup', this._handleMouseUp);
    super.disconnectedCallback();
  }

  recalculate(key: string, node: any) {
    //   node.height = 500;
    //   // node.height = 500;
    //   // console.log(e.target.node);
    //   this.layout = getLayout(g);
    //   g.nodes().forEach(function (v) {
    //     console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
    //   });
  }

  // Render the UI as a function of component state
  render() {
    if (!this.g) {
      return html`No g`;
    }
    return html`
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; transform: translate(${this.delta.x}px, ${this.delta.y}px);">
      <patterned-background pattern="checkered"></patterned-background>
      ${this.layout?.nodes.map(key => html`
        <diagraph-node key=${key} .node=${this.g.node(key)} @click=${() => this.recalculate(key, g.node(key))}></diagraph-node>
      `)}
      ${this.layout?.edges.map(key => html`
        <diagraph-edge offsetX=${width} offsetY=${height} .edge=${this.g.edge(key)}></diagraph-edge>
      `)}
      </div>
    `;
  }
}

import { LitElement, css, html } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';

export class DiagraphEdge extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = css`
  :host {
    position: absolute;
    top: 0;
    left: 0;
    z-index: 1; 
    width: 100%;
    height: 100%;
  }
  polyline {
    fill: none;
    stroke-width: 3;
    stroke-linecap: round;
    stroke: rgba(0,0,0,0.5);
}
svg {
    width: 100%;
    height: 100%;
}
  `;

  @property({ type: Object })
  edge?: any;

  @property({ type: Number })
  offsetX?: number;

  @property({ type: Number })
  offsetY?: number;

  // Render the UI as a function of component state
  render() {
    console.log(this.edge);
    const { points } = this.edge;
    return html`
    <svg>
      <polyline points="${points.map(({ x, y }) => [x + this.offsetX / 2, y + this.offsetY / 2].join(',')).join(' ')}"></polyline>    
    </svg>
    `;
  }
}

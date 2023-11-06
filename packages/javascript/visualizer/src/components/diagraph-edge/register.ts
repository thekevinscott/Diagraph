import { DiagraphEdge, name } from './diagraph-edge.js';

customElements.get(name) || customElements.define(name, DiagraphEdge);

declare global {
  interface HTMLElementTagNameMap {
    [name]: DiagraphEdge;
  }
}


import { DiagraphEdge } from "./diagraph-edge.js";

declare global {
  interface HTMLElementTagNameMap {
    'diagraph-edge': DiagraphEdge;
  }
}

customElements.get('diagraph-edge') || customElements.define('diagraph-edge', DiagraphEdge);

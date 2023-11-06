import { DiagraphInternalNode, name } from './diagraph-node.js';

customElements.get(name) || customElements.define(name, DiagraphInternalNode);

declare global {
  interface HTMLElementTagNameMap {
    [name]: DiagraphInternalNode;
  }
}


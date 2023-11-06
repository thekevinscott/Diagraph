import { DiagraphPublicNode, name } from './diagraph-public-node.js';

customElements.get(name) || customElements.define(name, DiagraphPublicNode);

declare global {
  interface HTMLElementTagNameMap {
    [name]: DiagraphPublicNode;
  }
}

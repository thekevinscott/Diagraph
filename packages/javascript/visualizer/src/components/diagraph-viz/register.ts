import { DiagraphViz, name } from './diagraph-viz.js';

customElements.get(name) || customElements.define(name, DiagraphViz);

declare global {
  interface HTMLElementTagNameMap {
    [name]: DiagraphViz;
  }
}

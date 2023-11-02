import { App, } from './app.js';

customElements.get('docs-app') || customElements.define('docs-app', App);

declare global {
  interface HTMLElementTagNameMap {
    "docs-app": App;
  }
}


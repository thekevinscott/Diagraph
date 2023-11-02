import { HomePage, } from './home.js';

customElements.get('page-home') || customElements.define('page-home', HomePage);

declare global {
  interface HTMLElementTagNameMap {
    "page-home": HomePage;
  }
}


import { AppNav, } from './app-nav.js';

customElements.get('app-nav') || customElements.define('app-nav', AppNav);

declare global {
  interface HTMLElementTagNameMap {
    "app-nav": AppNav;
  }
}



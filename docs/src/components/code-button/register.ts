import { CodeButton, } from './code-button.js';

customElements.get('code-button') || customElements.define('code-button', CodeButton);

declare global {
  interface HTMLElementTagNameMap {
    "code-button": CodeButton;
  }
}


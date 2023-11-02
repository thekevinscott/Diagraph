import { CodeBlockRunButton, } from './code-block-run-button.js';

customElements.get('code-block-run-button') || customElements.define('code-block-run-button', CodeBlockRunButton);

declare global {
  interface HTMLElementTagNameMap {
    "code-block-run-button": CodeBlockRunButton;
  }
}

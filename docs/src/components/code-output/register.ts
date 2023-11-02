import { CodeOutput, } from './code-output.js';

customElements.get('code-output') || customElements.define('code-output', CodeOutput);

declare global {
  interface HTMLElementTagNameMap {
    "code-output": CodeOutput;
  }
}


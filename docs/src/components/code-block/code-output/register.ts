import { CodeOutput, } from './code-output';

customElements.get('code-output') || customElements.define('code-output', CodeOutput);

declare global {
  interface HTMLElementTagNameMap {
    "code-output": CodeOutput;
  }
}


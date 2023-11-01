import { CodeBlock, } from './code-block';

customElements.get('code-block') || customElements.define('code-block', CodeBlock);

declare global {
  interface HTMLElementTagNameMap {
    "code-block": CodeBlock;
  }
}

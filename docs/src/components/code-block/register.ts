import { CodeBlock, } from './code-block.js';
import './code-block-run-button/register.js';

customElements.get('code-block') || customElements.define('code-block', CodeBlock);

declare global {
  interface HTMLElementTagNameMap {
    "code-block": CodeBlock;
  }
}

import { CodeBlock, } from './code-block';
import './code-logs/register';
import './code-output/register';

customElements.get('code-block') || customElements.define('code-block', CodeBlock);

declare global {
  interface HTMLElementTagNameMap {
    "code-block": CodeBlock;
  }
}

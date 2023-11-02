import { CodeLogs, } from './code-logs.js';

customElements.get('code-logs') || customElements.define('code-logs', CodeLogs);

declare global {
  interface HTMLElementTagNameMap {
    "code-logs": CodeLogs;
  }
}


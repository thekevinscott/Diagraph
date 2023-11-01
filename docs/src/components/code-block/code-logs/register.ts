import { CodeLogs, } from './code-logs';

customElements.get('code-logs') || customElements.define('code-logs', CodeLogs);

declare global {
  interface HTMLElementTagNameMap {
    "code-logs": CodeLogs;
  }
}


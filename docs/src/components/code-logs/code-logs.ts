// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, PropertyValueMap, css, html } from 'lit';
import styles from './code-logs.css?inline';
import { property } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { parseStyles } from '../../utils/parse-styles.js';

export interface LogMessage {
  message: string;
  timestamp: Date;
  kind: 'stderr' | 'stdout';
}

const PADDING = 20;
const OFFSET = 20;

export class CodeLogs extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @property({ type: Array })
  logs!: LogMessage[];

  @property()
  dark = false;

  scroll() {
    const logs = this.shadowRoot!.getElementById('logs')!;
    const scroll = logs.scrollHeight - logs.offsetHeight - logs.scrollTop - PADDING - OFFSET;
  }

  protected updated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    const logs = this.shadowRoot!.getElementById('logs')!;
    const scroll = logs.scrollHeight - logs.offsetHeight - logs.scrollTop - PADDING - OFFSET;
    if (scroll < 0) {
      logs.scrollTo(0, logs.scrollHeight);
    }
  }

  render() {
    const { dark, } = this;
    const logs = this.logs.map(({ message }) => message).join('\n');
      console.log(logs);
    return html`
      <div id="logs" @scroll=${this.scroll} class=${classMap({ dark })}>${logs}</div>
    `;
  }
}

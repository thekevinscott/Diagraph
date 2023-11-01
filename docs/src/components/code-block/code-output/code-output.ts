// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import styles from '!!raw-loader!./code-output.css';
import { property } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { parseStyles } from '../../parse-styles';

export class CodeOutput extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @property({ type: Boolean })
  accessor dark = false;

  @property({ type: Boolean })
  accessor running = false;

  @property({ type: Object })
  accessor output: any;

  @property({ type: Object })
  accessor error: any;

  renderBody() {
    const { error, output } = this;

    if (error) {
      return html`
        <label class="error">Error</label>
        <pre class="error">${error}</pre>
      `;
    }

    return html`
        <label>Output</label>
        <pre>${output}</pre>
    `;
  }

  render() {
    const { dark, running, error, output } = this;
    const visible = !!output || !!error || running;

    return html`
      <div id="output" class=${classMap({ visible, dark })}>
        ${this.renderBody()}
      </div>
    `;
  }
}


// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import styles from './code-output.css?inline';
import { property } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { parseStyles } from '../../utils/parse-styles.js';

export class CodeOutput extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @property({ type: Boolean })
  dark = false;

  @property({ type: Boolean })
  isError = false;

  @property({ type: Object })
  output: any;

  @property({ type: Object })
  error: any;

  renderBody() {
    const { isError, output } = this;

    if (output) {
      return html`
          <pre class=${classMap({ error: isError })}>${output}</pre>
      `;
    }

    return html``;
  }

  render() {
    const { dark, running } = this;

    return this.renderBody();
    // return html`
    //   <div id="output" class=${classMap({ dark })}>
    //     ${this.renderBody()}
    //   </div>
    // `;
  }
}


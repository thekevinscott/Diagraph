// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
// import globalStyles from '../../../styles/index.css?inline';
import styles from './code-block-run-button.css?inline';
import { parseStyles } from '../../../utils/parse-styles.js';
import { styleMap } from 'lit/directives/style-map.js';
import { emit, } from '../../../utils/event.js';

export class CodeBlockRunButton extends LitElement {
  static styles = [
    // parseStyles(globalStyles),
    parseStyles(styles),
  ];

  @property({ type: Boolean })
  running = false;

  @state()
  hover = false;

  render() {
    const { running } = this;
    if (running) {
      if (this.hover) {
        return html`
          <code-button
            .hotkeys=${['shift', 'escape']}
            @mouseout=${() => this.hover = false}
          >
            <sl-icon slot="prefix" name="stop"></sl-icon>
            Stop
          </code-button>
        `;
      }

      return html`
        <code-button
          .hotkeys=${['shift', 'escape']}
          class="running"
          @mouseover=${() => this.hover = true}
          @mouseout=${() => this.hover = false}
          loading
        >
            <sl-icon slot="prefix" name="stop"></sl-icon>
            Stop
        </code-button>
      `;
    }

    return html`
      <code-button
        .hotkeys=${['shift', 'enter']}
          @mouseover=${() => this.hover = true}
          @mouseout=${() => this.hover = false}
      >
        <sl-icon slot="prefix" name="play"></sl-icon>
        Run
      </code-button>
    `;
  }
};


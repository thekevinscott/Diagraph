// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { CodeEditor } from '../code-editor/code-editor.js';
import globalStyles from '../../styles/index.css?inline';
import styles from './code-button.css?inline';
import { parseStyles } from '../../utils/parse-styles.js';
import { CodeLogs, LogMessage } from './code-logs/code-logs.js';
import { styleMap } from 'lit/directives/style-map.js';
import { LightElement } from '../../utils/light-element.js';
import { emit, } from '../../utils/event.js';
import { KeyController, } from '../../controllers/key-controller/key-controller.js';

export class CodeButton extends LitElement {
  static styles = [
    // parseStyles(globalStyles),
    parseStyles(styles),
  ];

  @property({ type: Boolean })
  disabled = false

  @property({ type: Boolean })
  loading = false

  @property({ type: Array })
  hotkeys: string[];

  private keyListener = new KeyController(this, (e) => {
    if (this.hotkeys.length === 0) {
      return false;
    }
    let isMatch = true;
    for (const hotkey of this.hotkeys) {
      if (isMatch === false) {
        break;
      }

      if (hotkey === 'shift') {
        if (e.shiftKey === false) {
          isMatch = false;
        }
      } else if (hotkey === 'ctrl') {
        if (e.ctrlKey === false) {
          isMatch = false;
        }
      } else if (e.key.toLowerCase() !== hotkey) {
        isMatch = false;
      }
    }

    if (isMatch) {
      e.preventDefault();
      this.trigger();
    }
  });

  trigger() {
    emit(this, 'trigger');
  }

  renderHotkey() {
    return this.hotkeys.map(renderHotkey).join(' + ');
  }

  render() {
    const { loading, disabled, title, hotkeys, size = 'small' } = this;
    return html`
          <sl-button 
          aria-label=${`Trigger with ${hotkeys.join('+')}`}
          title=${`Trigger with ${hotkeys.join('+')}`}
          ?loading=${loading} ?disabled=${disabled} size="${size}" @click=${this.trigger}>
            <slot name="prefix" slot="prefix"></slot>
            <slot></slot>
            <span>${this.renderHotkey()}</span>
          </sl-button>
        `;
  }
}
const renderHotkey = (hotkey: string) => {
  if (hotkey === 'enter') {
    return '⏎';
  }
  if (hotkey === 'shift') {
    return '⇧';
  }
  if (hotkey === 'escape') {
    return '⎋';
  }
  if (hotkey === 'ctrl') {
    return '⌃';
  }
  if (hotkey === 'option') {
    return '⌥';
  }
  if (hotkey === 'command') {
    return '⌘';
  }
  return hotkey;
};

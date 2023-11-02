import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import resetStyles from '../../styles/reset.css?inline';
import globalStyles from '../../styles/global.css?inline';
import styles from './home.css?inline';
import { parseStyles } from '../../utils/parse-styles';
import { styleMap } from 'lit/directives/style-map.js';
import homepageExample from './homepage-example.py?raw';


export class HomePage extends LitElement {
  static styles = [
    parseStyles(resetStyles),
    parseStyles(globalStyles),
    parseStyles(styles),
  ];

    render() {
        return html`
    <main>
      <h1>Diagraph</h1>
      <h2>A graph for LLM interactions.</h2>
      <div id="code-block-container">
        <code-block code=${homepageExample}></code-block>
      </div>
    </main>
        `;
    }
}


import { LitElement, css, html } from 'lit';
import { customElement, property, state } from 'lit/decorators.js';
import { styleMap } from 'lit/directives/style-map.js';

// import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs";

@customElement('diagraph-node')
export class DiagraphNode extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = css`
    :host {
      z-index: 2;
      position: relative;
    }
    #node {
      background: white;
      position: absolute;
      border-radius: calc(8px * 2);
      // box-shadow: 0 2px 3px rgba(0,0,0,0.1);
      font-family: -apple-system, BlinkMacSystemFont, Helvetica, sans-serif;
      border: 3px solid rgba(0,0,0,0.6);
      display: flex;
      justify-content: center;
      align-items: center;
    }

    h1, h2, h3, h4, h5, h6 {
      font-weight: normal;
      margin: 0;
      padding: 0;
    }

    * {
      box-sizing: border-box;
    }

    header#top {
      // border-bottom: 1px solid rgba(0,0,0,0.1);
      // padding: 10px 20px;
      display: flex;
      justify-content: center;
      align-items: center;
    }

    h1 {
      font-size: 20px;
      text-align: center;
    }

    section {
      padding: 10px 20px;
    }

    section header {
      display: flex;
    }

    section header label {
      flex: 1;
    }
  `;

  @property({ type: Object })
  node?: any;

  @state()
  open = false

  // Render the UI as a function of component state
  render() {
    const {
      height,
      label,
      width,
      x,
      y,
    } = this.node;
    return html`
      <div id="node" style=${styleMap({
      width: `${width}px`,
      height: `${height}px`,
      left: `${x}px`,
      top: `${y}px`,
    })}>
        <h1>${label}</h1>
      </div>
    `;
  }
}


// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { CodeEditor } from '../code-editor/code-editor';
import type { loadPyodide as _loadPyodide } from 'pyodide';

// const loadPyodideModule = (version: string) => import(`https://cdn.jsdelivr.net/npm/pyodide@${version}/+esm`);
// const getPyodide = async (version: string) => (await loadPyodideModule(version));
// const loadPyodide = async (version: string) => (await getPyodide(version)).loadPyodide({
//   indexURL: `https://cdn.jsdelivr.net/npm/pyodide@${version}/`,
// });

declare global {
  interface Window { loadPyodide: typeof _loadPyodide; }
}

export class CodeBlock extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = css`
    :host {
      border: 2px solid rgba(0,0,0,0.2);
      border-radius: 8px;
      overflow: hidden;
      width: 100%;
      max-height: 400px;
      display: flex;
      min-height: 40px;
      flex-direction: column;
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, Ubuntu, Cantarell, "Noto Sans", sans-serif, "system-ui", "Segoe UI", Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol"
    }

    #top {
      display: flex;
      flex-direction: row;
      flex: 1;
      border-bottom: 2px solid rgba(0,0,0,0.1);

      &.dark {

        & code-output {
          background: rgba(255,255,255,0.05);
        }

        & button {
          border: 2px solid rgba(255,255,255,0.1);
          background: #333;
        }
      }

      & code-output {
        background: rgba(0,0,0,0.05);
        padding: 3px 10px;
        font-family: Roboto, monospace;
        font-size: 12px;
        box-shadow: inset 0 0 6px rgba(0,0,0,0.1);
      }

      & #editor {
        position: relative;
        flex: 1;
        height: 250px;

        & button {
          position: absolute;
          bottom: 0;
          right: 0;
          border: none;
          padding: 10px;
          font-size: 16px;
          // text-transform: uppercase;
          border: 2px solid rgba(0,0,0,0.1);
          border-bottom: none;
          background: #CCC;
          cursor: pointer;
        }

        & code-editor {
        }
      }
    }

    #visualization {
      flex: 1;
      background: white;
      padding: 10px;

      &.dark {
        background: var(--ifm-background-surface-color);
        color: white;
      }
    }
  `;

  @property()
  accessor code: string = '';

  @property()
  accessor colorMode: 'dark' | 'light' = 'light';

  // @state()
  // accessor output: string = '';

  codeEditor: Ref<CodeEditor> = createRef();

  pyodide = window.loadPyodide();

  keydown(e: KeyboardEvent) {

    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      this.run();
    }
  }

  async run() {
    const code = this.codeEditor!.value.value;
    const pyodide = await this.pyodide;
    // await pyodide.loadPackage('micropip');
    // this.output = await pyodide.runPythonAsync(code);
  };

  // Render the UI as a function of component state
  render() {
    const { code, colorMode } = this;
    const theme = colorMode === 'dark' ? 'vs-dark' : 'vs-light';
    return html`
      <div id="top" class=${classMap({ dark: colorMode === 'dark' })}>
        <div id="editor">
          <code-editor ${ref(this.codeEditor)} @keydown=${this.keydown} code=${code} theme=${theme}></code-editor>
          <button @click=${this.run}>Run (shift + enter)</button>
        </div>
        <code-output>output!</code-output>
      </div>
      <div id="visualization" class=${classMap({ dark: colorMode === 'dark' })}>Visualization</div>
    `;
  }
}

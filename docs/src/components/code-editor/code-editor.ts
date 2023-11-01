import * as monaco from 'monaco-editor';
// import styles from 'monaco-editor/min/vs/editor/editor.main.css';

import { Ref, createRef, ref } from 'lit/directives/ref.js';

import { LitElement, PropertyValueMap, css, html, unsafeCSS } from 'lit';
import { property, query } from 'lit/decorators.js';


import * as editorWorker from 'monaco-editor/esm/vs/editor/editor.worker';
// import * as pythonWorker from 'monaco-editor/esm/vs/editor/python.worker';

// import editorWorker from "monaco-editor/esm/vs/editor/editor.worker?worker";
// import pythonWorker from 'monaco-editor/esm/vs/language/python/python.worker?worker';

// @ts-ignore
self.MonacoEnvironment = {
  getWorker(_: any, label: string) {
    // if (label === "python") {
    //   return new pythonWorker();
    // }
    return new editorWorker();
  },
};

const DEFAULT_EDITOR_OPTIONS: monaco.editor.IEditorConstructionOptions = {
  // autoIndent: "full",
  // automaticLayout: true,
  // contextmenu: true,
  // fontFamily: "monospace",
  // fontSize: 13,
  // lineHeight: 24,
  // hideCursorInOverviewRuler: true,
  // matchBrackets: "always",
  minimap: {
    enabled: false,
  },
  // readOnly: false,
  // scrollbar: {
  //   horizontalSliderSize: 4,
  //   verticalSliderSize: 18,
  // },

  lineNumbers: "on",
  roundedSelection: false,
  scrollBeyondLastLine: false,
  ariaLabel: "online code editor",
  readOnly: false,
  // theme: "hc-black",
  // language: "javascript",
  //Resizes Based on Screen & Container Size.
  automaticLayout: true
};

export class CodeEditor extends LitElement {
  static styles = [
    // unsafeCSS(styles),
    css`
      :host {
        --editor-width: 100%;
        --editor-height: 100%;
      }
      main {
        width: var(--editor-width);
        height: var(--editor-height);
      }
  `];

  @property()
  accessor code: string = '';

  @property()
  accessor theme: string = 'vs-light';

  containerRef: Ref<HTMLDivElement> = createRef();

  // private get theme(dark = false) {
  //   return dark ? "vs-dark" : "vs-light";
  // }

  constructor() {
    super();
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", () => {
        monaco.editor.setTheme('vs-dark');
      });
  }

  editor?: any;

  firstUpdated() {
    this.editor = monaco.editor.create(
      this.containerRef.value!,
      {
        ...DEFAULT_EDITOR_OPTIONS,
        value: this.code,
        language: 'python',
        theme: this.theme,
      },
    );
  }

  get value() {
    return this.editor!.getValue();
  }

  protected updated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    if (_changedProperties.has('theme')) {
      this.editor!.updateOptions({
        theme: this.theme,
      });
    }
  }

  render() {
    return html`
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/monaco-editor@0.44.0/min/vs/editor/editor.main.min.css">
    <main ${ref(this.containerRef)} />`;
  }
}

// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { CodeEditor } from '../code-editor/code-editor';
import styles from '!!raw-loader!./code-block.css';
import { parseStyles } from '../parse-styles';
import { CodeLogs, LogMessage } from './code-logs/code-logs';
import { styleMap } from 'lit/directives/style-map.js';

// declare global {
//   interface Window { loadPyodide: typeof _loadPyodide; }
// }

export class CodeBlock extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @property()
  accessor code: string = '';

  @property()
  accessor colorMode: 'dark' | 'light' = 'light';

  @state()
  accessor output: string = '';

  @state()
  accessor logs: LogMessage[] = [];

  @state()
  accessor running = false;

  @state()
  accessor ready = false;

  @state()
  accessor error: string | undefined;

  codeEditor: Ref<CodeEditor> = createRef();
  codeLogs: Ref<CodeLogs> = createRef();

  worker: SharedWorker;

  accessor id: string | undefined;

  constructor() {
    super();
    this.worker = new SharedWorker(new URL('./runner.js', import.meta.url));
    this.worker.port.postMessage({ event: 'initialize' });
    this.worker.port.onmessage = this.handleMessage;
  }

  handleMessage = (e) => {
    // handleMessage = ({ data: { event, message, id } }) => {
    // console.log(e)
    const { data: { event, message, id } } = e;
    if (event === 'ready') {
      this.ready = true;
    }
    if (id === this.id) {
      // console.log('event', event);
      if (event === 'output') {
        this.output = message;
        this.running = false;
      }
      if (['stdout', 'stderr'].includes(event)) {
        this.logs.push({ message, timestamp: new Date(), kind: event });
        this.requestUpdate();
        this.codeLogs.value.requestUpdate();
      }
      if (event === 'error') {
        this.error = message;
        // console.log('this', this.error);
        this.running = false;
      }
    }
  };

  keydown(e: KeyboardEvent) {

    if (e.key === 'Enter' && e.shiftKey) {
      e.preventDefault();
      this.run();
    }
  }

  async run() {
    if (this.running === false) {
      this.running = true;
      this.logs = [];
      this.output = '';
      const code = this.codeEditor!.value.value;
      this.id = `${Math.random()}`;
      this.worker.port.postMessage({
        event: 'run',
        code,
        id: this.id,
      });
    }
  };

  // Render the UI as a function of component state
  render() {
    const { code, colorMode, ready, running, logs, error, output } = this;

    const dark = colorMode === 'dark';
    const theme = dark ? 'vs-dark' : 'vs-light';
    const height = getHeight(code);
    // console.log('logs', logs);
    return html`
      <div id="top" class=${classMap({ dark })} style=${styleMap({ minHeight: height, maxHeight: height })}>
        <div id="editor">
          <div id="actions">
            <sl-icon-button name="arrow-clockwise" label="Reload Code Snippet"></sl-icon-button>
          </div>
          <code-editor ${ref(this.codeEditor)} @keydown=${this.keydown} code=${code} theme=${theme}></code-editor>
          <sl-button 
            ?disabled=${!ready || running} 
            title="Run (shift + enter)" 
            @click=${this.run}>
            ${getButtonMessage(ready, running)}
          </sl-button>
        </div>
        <code-logs ?dark=${dark} ${ref(this.codeLogs)} .logs=${logs}></code-logs>
      </div>
      <code-output ?dark=${dark} .error=${error} .output=${output} ?running=${running}></code-output>
    `;
  }
}

const getButtonMessage = (ready: boolean, running: boolean) => {
  if (!ready) {
    return 'Starting...';
  }
  if (running) {
    return 'Running...';
  }
  return 'Run ⇧+⏎';
};

const LINE_HEIGHT = 18;

const getHeight = (code: string) => {
  const lines = Math.min(Math.max(code.split('\n').length, 6), 40);
  const height = lines * LINE_HEIGHT;
  return `${height}px`;
}

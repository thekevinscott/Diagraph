// import "node_modules/@vanillawc/wc-monaco-editor/index.js";
// import '@vanillawc/wc-monaco-editor'
import { LitElement, css, html } from 'lit';
import { property, state } from 'lit/decorators.js';
import { classMap } from 'lit/directives/class-map.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { CodeEditor } from '../code-editor/code-editor.js';
import globalStyles from '../../styles/global.css?inline';
import styles from './code-block.css?inline';
import { parseStyles } from '../../utils/parse-styles.js';
import { styleMap } from 'lit/directives/style-map.js';
import { CodeController } from '../../controllers/code-controller/code-controller.js';

import { CodeLogs } from '../code-logs/code-logs.js';

// import * as webllm from "@mlc-ai/web-llm";
// function setLabel(id: string, text: string) {
//   console.log(id, text);
// }

// // Use a chat worker client instead of ChatModule here
// const chat = new webllm.ChatWorkerClient(new Worker(
//   new URL('./worker.ts', import.meta.url),
//   { type: 'module' }
// ));

// chat.setInitProgressCallback((report: webllm.InitProgressReport) => {
//   setLabel("init-label", report.text);
// });
// window['chat'] = chat;
// console.log(chat);
// // chat.reload("RedPajama-INCITE-Chat-3B-v1-q4f32_0");

// const generateProgressCallback = (_step: number, message: string) => {
//   // setLabel("generate-label", message);
// };

// const prompt0 = "What is the capital of Canada?";
// const reply0 = await chat.generate(prompt0, generateProgressCallback);
// console.log(reply0);

export class CodeBlock extends LitElement {
  static styles = [
    parseStyles(globalStyles),
    parseStyles(styles),
  ];

  // @property()
  // code: string = '';

  @property()
  height: string = '';

  @property()
  colorMode: 'dark' | 'light' = 'light';

  @state()
  focused = false;

  codeEditor: Ref<CodeEditor> = createRef();
  codeLogs: Ref<CodeLogs> = createRef();
  private runner = new CodeController(this);

  id: string | undefined;

  reset() {
    this.codeEditor!.value.reset();
  }

  async run() {
    const code = this.codeEditor!.value.value;
    this.id = this.runner.run(code);
  };

  stop() {
    this.runner.stop(this.id);
  }

  focus() {
    this.focused = true;
  }
  blur() {
    this.focused = false;
  }

  handleRunClick() {
    if (this.runner.running) {
      this.stop();
    } else {
      this.run();
    }
  }

  updated() {
    this.codeLogs.value.requestUpdate();
  }

  // Render the UI as a function of component state
  render() {
    const {
      focused,
      colorMode,
      runner,
      height } = this;
    const { running, logs, error, output } = runner;

    const dark = colorMode === 'dark';
    const theme = dark ? 'vs-dark' : 'vs-light';
    const _height = getHeight('');
    return html`
<sl-split-panel 
style="--code-block-height: ${_height}"
vertical 
      class=${classMap({ focused })}
id="container" position="75" snap="95% 75% 50% 0%" snap-threshold="25">
  <sl-icon slot="divider" name="grip-horizontal"></sl-icon>

  <div
    slot="start"
  >
          <code-editor 
          ${ref(this.codeEditor)} 
          @blur=${this.blur}
          @focus=${this.focus}
          theme=${theme}><slot></slot></code-editor>

          <sl-button-group label="Actions">

      <code-button
        .hotkeys=${['ctrl', 'r']}
        @trigger=${this.reset}
      >
  <sl-icon slot="prefix" name="arrow-clockwise"></sl-icon>
  Reset
      </code-button>
  <code-block-run-button 
  @trigger=${this.handleRunClick}
  ?running=${running}></code-block-run-button>
</sl-button-group>
  </div>
<sl-split-panel slot="end" snap="100% 50% 0%" snap-threshold="25">
  <sl-icon slot="divider" name="grip-vertical"></sl-icon>
  <div
    slot="start"
  >
    <label>Output</label>
      <code-output 
      ?dark=${dark} 
      ?isError=${!!error}
      .output=${error || output} 
      ></code-output>
  </div>
  <div
    slot="end"
  >
    <label>Logs</label>
        <code-logs 
        ?dark=${dark} 
        ${ref(this.codeLogs)} 
        .logs=${logs}></code-logs>
  </div>
</sl-split-panel>    


</sl-split-panel>   
`;
  }
}

const LINE_HEIGHT = 18;

const getHeight = (code: string) => {
  return '600px';
  //   const lines = Math.min(Math.max(code.split('\n').length, 6), 40);
  //   const height = lines * LINE_HEIGHT;
  //   return `${height}px`;
}

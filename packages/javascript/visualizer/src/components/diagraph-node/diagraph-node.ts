import { LitElement, PropertyValueMap, css, html } from 'lit';
import { parseStyles } from '../../utils/parse-styles.js';
import styles from './diagraph-node.css?inline';
import { property, queryAll, state } from 'lit/decorators.js';
import { Ref, createRef, ref } from 'lit/directives/ref.js';
import { styleMap } from 'lit/directives/style-map.js';
import { emit } from '../../utils/emit.js';


export const name = 'diagraph-internal-node'
export const CONNECTION_SIZE = 16;
export const STATE_CHANGE_EVENT_NAME = 'state-change';

export interface DiagraphNode {
  name?: string;
  outEdges: Set<string>,
  inEdges: Set<string>,
  fn?: string;
  prompt?: string;
  result?: string;
  depth?: number;
}

const config = {
  lineNumbers: 'off',
  glyphMargin: false,
  folding: false,
  // Undocumented see https://github.com/Microsoft/vscode/issues/30795#issuecomment-410998882
  lineDecorationsWidth: 0,
  lineNumbersMinChars: 0,
  theme: 'vs-dark',
  readOnly: true,
  automaticLayout: true,
  renderLineHighlight: "none"

}

export class DiagraphInternalNode extends LitElement {
  // Define scoped styles right with your component, in plain CSS
  static styles = [
    parseStyles(styles),
  ];

  @property({ type: Object })
  node!: DiagraphNode;

  @property({ type: Number })
  index!: number;

  @property({ type: Object })
  layers!: Record<number, string[]>;

  @queryAll('details')
  details!: HTMLDetailsElement[];

  @state()
  openStates: boolean[] = [];

  updateToggledState = () => {
    this.openStates = [...this.details].map(detail => detail.getAttribute('open') !== null);
  }

  protected updated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    if (_changedProperties.has('openStates')) {
      emit(this, STATE_CHANGE_EVENT_NAME, {});
    }
  }

  openAll() {
    this.details.forEach(detail => {
      detail.setAttribute('open', '');
    });
    this.updateToggledState();
    // this.open = true;
  }

  hideAll() {
    this.details.forEach(detail => {
      detail.removeAttribute('open');
    });
    this.updateToggledState();
  }

  renderConnections(refs: Record<number, Ref<HTMLElement>>) {
    const num = Object.keys(refs).length;
    return html`
        ${Array(num).fill('').map((_, i) => {
      return html`
          <div ref=${ref(refs[i])} class="connection"></div>
          `;
    })}
    `;
  }

  public toRefs: Record<number, Ref<HTMLElement>> = {};
  public fromRefs: Record<number, Ref<HTMLElement>> = {};
  // Render the UI as a function of component state
  render() {
    const {
      node: {
        fn,
        result,
        name,
        depth,
        inEdges,
        outEdges,
      },
      openStates,
    } = this;
    const open = openStates.reduce((open, openState) => {
      return open === false ? false : openState
    }, true);

    for (let i = 0; i < inEdges.size; i++) {
      this.fromRefs[i] = createRef();
    }
    for (let i = 0; i < outEdges.size; i++) {
      this.toRefs[i] = createRef();
    }
    return html`
      <div id="node" style=${styleMap({ '--connection-size': `${CONNECTION_SIZE}px` })}>
        ${depth !== 0 ? html`
        <div id="inputs">
          ${this.renderConnections(this.toRefs)}
        </div>
        ` : html``}
        <header>
          <h1>${name}</h1>
          <div id="actions">
            ${open ? html`
              <sl-icon-button @click=${this.openAll} name="fullscreen-exit" label="Hide all"></sl-icon-button>
            ` : html`
              <sl-icon-button @click=${this.hideAll} name="fullscreen" label="Expand all"></sl-icon-button>
            `}
          </div>
        </header>
        <div id="sections">
        ${[
        { language: 'python', label: 'Function', content: fn },
        { language: 'text', label: 'Prompt', content: prompt },
        { language: 'text', label: 'Result', content: result },
      ].map(({ label, content, language, }) => html`
          <section>
            <details @click=${this.updateToggledState}>
              <summary>
              <label>${label}</label>
              </summary>
              <detail>
              <code-editor .options=${{ ...config, language }}>${content}</code-editor>
              </detail>
              </details>
            </section>
        `)}
        </div>
        ${depth !== Object.keys(this.layers).length - 1 ? html`
        <div id="outputs">
          ${this.renderConnections(this.fromRefs)}
        </div>
        ` : html``}
        </div>
    `;
  }
}



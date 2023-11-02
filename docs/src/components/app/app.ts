import { LitElement, css, html } from 'lit';
// import { property, state } from 'lit/decorators.js';
import { query } from 'lit/decorators.js';
// import { classMap } from 'lit/directives/class-map.js';
// import { Ref, createRef, ref } from 'lit/directives/ref.js';
// import { parseStyles } from '../../utils/parse-styles';
// import { styleMap } from 'lit/directives/style-map.js';
import { Router } from '@lit-labs/router';

import { ROUTES, } from '../../routes.js';

export class App extends LitElement {
  static styles = css`
    #outlet {
    height: 100%;
    overflow: hidden;
        display: flex;
        flex-direction: column;
        align-items: stretch;

        & > * {
            flex: 1;
        }
    }
    `;

  private router = new Router(this, ROUTES);

  @query('#outlet')
  outlet!: HTMLDivElement;

  protected createRenderRoot(): HTMLElement | DocumentFragment {
    return this;
  }

  render() {
    return html`
      <app-nav .pages=${ROUTES}></app-nav>
      ${this.router.outlet()}
    `;
  }
}



import { LitElement, css, html } from 'lit';
import { classMap } from 'lit/directives/class-map.js';

const NAV_ITEMS = [{
  label: 'Diagraph',
  href: '/',
}, {
  label: 'Docs',
  href: '/docs',
}]

export class AppNav extends LitElement {
  protected createRenderRoot(): HTMLElement | DocumentFragment {
    return this;
  }

  render() {
    return html`
      <nav id="app-nav">
        ${NAV_ITEMS.map(({ href, label }) => {
      const active = href === window.location.pathname && href !== '/';
      return html`
            <a 
          href="${href}" 
          class=${classMap({ active })}>${label}</a>
            `;
    })}
      </nav>
    `;
  }
}

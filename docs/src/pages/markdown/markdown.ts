import { LitElement, PropertyValueMap, css, html } from 'lit';
import { classMap } from 'lit/directives/class-map.js';
import { property, query, queryAll, state } from 'lit/decorators.js';
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { parseMarkdown } from './parse-markdown.js';
import { TreeNode } from '../../routes.js';

export class MarkdownPage extends LitElement {
  @property()
  content!: string;

  @property()
  path!: string;

  @property({ type: Object })
  tree!: TreeNode;

  protected createRenderRoot(): HTMLElement | DocumentFragment {
    return this;
  }

  render() {
    const { tree, path } = this;
    const {
      content,
      frontmatter,
    } = parseMarkdown(this.content);
    // console.log(content);
    return html`
    <div id="markdown-page">
      <page-markdown-toc .tree=${tree} active=${path}></page-markdown-toc>
      <main>
        ${unsafeHTML(content)}
        <nav>
        <a href="#">Next</a>
        </nav>
      </main>
      </div>
    `;
  }
}


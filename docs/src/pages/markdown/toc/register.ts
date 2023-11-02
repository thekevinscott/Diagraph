import { MarkdownPageTOC, } from './toc.js';

customElements.get('page-markdown-toc') || customElements.define('page-markdown-toc', MarkdownPageTOC);

declare global {
  interface HTMLElementTagNameMap {
    "page-markdown-toc": MarkdownPageTOC;
  }
}



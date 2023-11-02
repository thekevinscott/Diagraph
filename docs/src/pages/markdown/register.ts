import { MarkdownPage, } from './markdown.js';
import './toc/register.js';

customElements.get('page-markdown') || customElements.define('page-markdown', MarkdownPage);

declare global {
  interface HTMLElementTagNameMap {
    "page-markdown": MarkdownPage;
  }
}


import { LitElement, PropertyValueMap, css, html } from 'lit';
import { classMap } from 'lit/directives/class-map.js';
import { property, query, queryAll, state } from 'lit/decorators.js';
import resetStyles from '../../../styles/reset.css?inline';
import globalStyles from '../../../styles/global.css?inline';
import styles from './toc.css?inline';
import { parseStyles } from '../../../utils/parse-styles.js';
import { TreeNode } from '../../../routes.js';

export class MarkdownPageTOC extends LitElement {
  static styles = [
    parseStyles(resetStyles),
    parseStyles(globalStyles),
    parseStyles(styles),
  ];

  @property()
  active!: string;

  @property({ type: Object })
  tree!: TreeNode;

  renderNode = (node: TreeNode) => {
    const { page, entry } = node;
    if (page) {
      const { path, title } = page;
      const active = isActive(path, this.active);
      console.log(path);
      return html`
        <li>
          <a 
            class=${classMap({ active })} 
            href="${path}"
          >
            ${capitalize(entry)}
          </a>
      </li>`;
    }

    return html`
        <li>
          <a 
            class=${classMap({ active: false })} 
          >
            <span>${capitalize(entry)}</span>

            <sl-icon-button name="caret-down"></sl-icon-button>
          </a>
          ${this.renderTree(node)}
      </li>`;
  }

  renderTree = (node: TreeNode) => {
    if (!node.children) {
      throw new Error('Node is not a tree');
    }

    return html`
      <ul>
        ${Object.values(node.children).sort((a, b) => {
      if (a.page && b.page) {
        return a.page.frontmatter.sidebar_position - b.page.frontmatter.sidebar_position;
      }
      return 0;
    }).map(this.renderNode)
      }
    </ul>
      `;
  }

  render() {
    const { tree } = this;
    if (!tree) {
      return html``;

    }
    return html`
      <nav id="toc">
        ${this.renderTree(tree)}
    </nav>
      `;
  }
}


const isActive = (path: string, active: string) => {
  if (path === active) {
    return true;
  }

  if (path.endsWith('/index') && path.startsWith(active)) {
    return true;
  }
  return false;
};

const capitalizeWord = (str: string) => str.charAt(0).toUpperCase() + str.slice(1);
const capitalize = (entry: string) => entry.split(/[\s-_]+/).map(capitalizeWord).join(' ');

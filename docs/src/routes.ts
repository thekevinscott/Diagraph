import { PathRouteConfig, RouteConfig } from "@lit-labs/router";
import { html } from "lit";
import { Frontmatter, parseMarkdown } from "./pages/markdown/parse-markdown.js";

const modules = import.meta.glob('./content/**/*', { as: 'raw' });
const paths = [];

for (const path in modules) {
  paths.push(path);
}

function addToTree(node: TreeNode, pathParts: string[], data: PageContent) {
  const part = pathParts[0];
  if (!node.children) {
    node.children = {};
  }

  if (pathParts.length === 1) {
    node.children[part] = { entry: part, page: data };
  } else {
    if (!node.children[part]) {
      node.children[part] = { entry: part, };
    }
    addToTree(node.children[part], pathParts.slice(1), data);
  }
}

interface PageContent {
  frontmatter: Frontmatter;
  path: string;
  content: string;
}

export interface TreeNode {
  page?: PageContent;
  children?: Record<string, TreeNode>;
  entry: string;
}

const tree: TreeNode = {
  entry: '',
  children: {},
};

await Promise.all(
  paths.map(async (path) => {
    const fileContent = await modules[path]();
    let parsedPath = path.replace('./content', '').replace('.md', '');
    const { content, frontmatter } = parseMarkdown(fileContent);

    addToTree(tree, parsedPath.split('/').slice(2), {
      frontmatter,
      path: parsedPath,
      content,
    });
  })
);

const routes: RouteConfig[] = [];

const addRoute = (path: string, content: string) => {
  routes.push({
    path,
    render: () => {
      return html`<page-markdown .tree=${tree} path=${path} content=${content}></page-markdown>`;
    },
  });
}

function flattenTree(node) {
  if (node.page) {
    const path: string = node.page.path;
    addRoute(path, node.page.content);
    if (path.endsWith('/index')) {
      const rootPath = path.split('/index')[0];
      addRoute(rootPath, node.page.content);
      addRoute(`${rootPath}/`, node.page.content);
    }
  } else if (node.children) {
    for (const key of Object.keys(node.children)) {
      flattenTree(node.children[key]);
    }
  }
}

flattenTree(tree);

export const ROUTES: RouteConfig[] = [
  { path: '/', render: () => html`<page-home></page-home>` },
  ...routes,
  { path: '*', render: () => html`Not Found` },
];

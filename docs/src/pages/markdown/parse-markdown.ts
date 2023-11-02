import markedCodePreview from 'marked-code-preview'
// import Prism from 'prismjs';
// import 'prismjs/themes/prism.css?inline';
import hljs from 'highlight.js';
// import 'prismjs/components/prism-typescript'; // Language
// import 'prismjs/components/prism-python'; // Language
import { markedHighlight } from "marked-highlight";
import { Marked } from 'marked';

import python from 'highlight.js/lib/languages/python';
import bash from 'highlight.js/lib/languages/bash';

hljs.registerLanguage('python', python);
hljs.registerLanguage('bash', bash);




const marked = new Marked(
  markedHighlight({
    langPrefix: 'hljs language-',
    highlight(code, lang) {
      const language = hljs.getLanguage(lang) ? lang : 'plaintext';
      return hljs.highlight(code, { language }).value;
    }
  })
);


export interface Frontmatter {
  [index: string]: any;
}

export interface ParsedMarkdown {
  content: string;
  frontmatter: Frontmatter;
}

const getValue = (value: string): any => {
  try {
    const intValue = parseInt(value, 10);
    if (!isNaN(intValue)) {
      return intValue;
    }
  } catch (e) { }
  return value;
};

const parseFrontmatter = (frontmatter: string): Frontmatter => {
  return frontmatter.split('\n').filter(line => line).reduce((acc, line) => {
    const parts = line.split(':');
    if (parts.length !== 2) {
      console.warn(`Invalid frontmatter line: ${line}`);
      return acc;
    }
    const value = getValue(parts[1].trim());
    return {
      ...acc,
      [parts[0].trim()]: value,
    }
  }, {});
};

const getFrontmatterAndContents = (fileContents: string): [Frontmatter | null, string] => {
  if (fileContents.trim().startsWith('---')) {
    const [frontmatter, ...contents] = fileContents.trimStart().split('---').slice(1);
    return [parseFrontmatter(frontmatter), contents.join('---')];
  }
  return [{}, fileContents];
}

export const parseMarkdown = (fileContents: string): ParsedMarkdown => {

  // return marked
  const [frontmatter, contents] = getFrontmatterAndContents(fileContents);
  const html = marked
    .use({ gfm: true })
    .use(markedCodePreview({
      template: `<code-block>{code}</code-block>`
    }))
    .parse(contents);

  return {
    content: html,
    frontmatter,
  };
}

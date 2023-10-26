import { html, css, LitElement } from 'lit'
import { property } from 'lit/decorators.js'
import { classMap } from 'lit/directives/class-map.js';

export type Pattern = 'striped' | 'checkered';
const PATTERNS = ['checkered', 'striped'];

export class PatternedBackground extends LitElement {
  static styles = css`
    #background {
      position: absolute;
      top: -999%;
      left: -999%;
      z-index: 0;
      width: calc(999% * 2);
      height: calc(999% * 2);
    }

    .striped {
      background: repeating-linear-gradient(
        -45deg,
        transparent,
        transparent 10px,
        rgba(4, 60, 94, 0.1) 10px,
        rgba(4, 60, 94, 0.1) 20px
      );
    }

    .checkered {
      background: repeating-conic-gradient(
        transparent 0 90deg,
        rgba(4, 60, 94, 0.1) 0 180deg)
      0 0/30px 30px round;
    }

    html[data-theme='dark'] {
      .striped {
        background: repeating-linear-gradient(
          -45deg,
          #00080f,
          #00080f 10px,
          #15232e 10px,
          #15232e 20px,
        );
      }

      .checkered {
        background: repeating-conic-gradient(
          #00080f 0 90deg,
          #15232e 0 180deg) 
        0 0/30px 30px round;
      }
    }
  `

  @property()
  pattern: Pattern = 'striped';

  render() {
    return html`
      <div id="background" class=${classMap({ [getPattern(this.pattern)]: true })}></div>
    `
  }
}

const isValidPattern = (pattern: unknown): pattern is Pattern => typeof pattern === 'string' && PATTERNS.includes(pattern);
const getPattern = (pattern: unknown): Pattern => isValidPattern(pattern) ? pattern : 'striped';

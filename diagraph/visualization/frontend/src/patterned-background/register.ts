import { PatternedBackground } from "./patterned-background.js";

declare global {
  interface HTMLElementTagNameMap {
    'patterned-background': PatternedBackground;
  }
}

customElements.get('patterned-background') || customElements.define('patterned-background', PatternedBackground);

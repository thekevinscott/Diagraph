import { LitElement, PropertyValueMap, css, html } from 'lit';
import { parseStyles } from '../../utils/parse-styles.js';
import styles from './diagraph-edge.css?inline';
import { property } from 'lit/decorators.js';
import { DiagraphViz, GAP } from '../diagraph-viz/diagraph-viz.js';
import { styleMap } from 'lit/directives/style-map.js';
import { CONNECTION_SIZE, STATE_CHANGE_EVENT_NAME } from '../diagraph-node/diagraph-node.js';
import { Ref } from 'lit/directives/ref.js';

export const name = 'diagraph-edge';

export const STROKE_WIDTH = 4;

const bump = (CONNECTION_SIZE / 2) - (STROKE_WIDTH / 2);

export class DiagraphEdge extends LitElement {
  static styles = [
    parseStyles(styles),
  ];

  @property()
  from!: string;

  @property()
  to!: string;

  @property({ type: Object })
  host!: DiagraphViz;

  constructor() {
    super();
    window.addEventListener('resize', this.redraw)
  }

  disconnectedCallback(): void {
    window.removeEventListener('resize', this.redraw)
    // this.observer.disconnect();
    this.host.removeEventListener(STATE_CHANGE_EVENT_NAME, this.redraw);
    super.disconnectedCallback();
  }

  // observer: MutationObserver;

  protected firstUpdated(_changedProperties: PropertyValueMap<any> | Map<PropertyKey, unknown>): void {
    // // Options for the observer (which mutations to observe)
    // const config = { attributes: true, childList: true, subtree: true };

    // // Callback function to execute when mutations are observed
    // const callback = (mutationList, observer) => {
    //   console.log('change', mutationList)
    //   for (const mutation of mutationList) {
    //     if (mutation.type === "childList") {
    //       console.log("A child node has been added or removed.");
    //     } else if (mutation.type === "attributes") {
    //       console.log(`The ${mutation.attributeName} attribute was modified.`);
    //     }
    //   }
    // };

    // this.observer = new MutationObserver(callback);

    // const from = this.host.getNode(this.from);
    // const to = this.host.getNode(this.to);
    // this.observer.observe(from, config);
    // this.observer.observe(to, config);
    this.host.addEventListener(STATE_CHANGE_EVENT_NAME, this.redraw);
  }

  redraw = () => {
    this.requestUpdate();
    setTimeout(() => this.requestUpdate(), 0);
    setTimeout(() => this.requestUpdate(), 1);
  }

  getDirection(dir: Ref<HTMLElement>) {
    return dir?.value?.getBoundingClientRect() || { x: 0, y: 0, width: 0, height: 0 };
  }

  get fromNode() {
    return this.host.getNode(this.from);
  }
  get toNode() {
    return this.host.getNode(this.to);
  }

  getFrom() {
    return this.getDirection(this.fromNode?.fromRefs[this.toNode.getAttribute('index')]);
  }

  getTo() {
    return this.getDirection(this.toNode?.toRefs[this.fromNode.getAttribute('index')]);
  }

  getEndX = () => {
    const { x: startX } = this.getFrom();
    const { x: endX } = this.getTo();
    return (endX - startX) + bump;
  }

  getEndY = () => {
    const { y: startY } = this.getFrom();
    const { y: endY } = this.getTo();
    return (endY - startY) + bump;
  }

  renderPath = () => {
    const edgeX = this.getEndX();
    const edgeY = this.getEndY();
    const midYPoint = edgeY - (GAP / 2)
    const startingX = edgeX < 0 ? (STROKE_WIDTH * 2) - edgeX : STROKE_WIDTH;
    const endingX = edgeX < 0 ? STROKE_WIDTH : edgeX;
    const points = [
      ['M', startingX, STROKE_WIDTH],
      ['V', midYPoint],
      ['H', endingX],
      ['V', edgeY],
    ];
    // console.log(this.from, '-->', this.to, points);
    return points.reduce<string[]>((arr, points) => points.reduce((arr2, point) => arr2.concat(`${point}`), arr), []).join(' ');
  }

  getLeft = () => {
    const { x: startX } = this.getFrom();
    const edgeX = this.getEndX();
    const leftX = startX + (CONNECTION_SIZE / 2);
    if (edgeX < 0) {
      return leftX + edgeX - 1 - (STROKE_WIDTH * 2);
    }

    return leftX - 1 - STROKE_WIDTH;
  }

  get width() {
    const { x: fromX, width: fromWidth } = this.getFrom();
    const { x: toX, width: toWidth } = this.getTo();
    // console.log(fromX, toX, fromWidth)
    return Math.abs(fromX - toX) + fromWidth;
  }

  render() {
    const { x: startX, y: startY } = this.getFrom();
    const { x: endX, y: endY } = this.getTo();
    // const width = Math.abs((endX - startX)) + CONNECTION_SIZE;
    const height = Math.abs((endY - startY) + (CONNECTION_SIZE * 1));

    const style = styleMap({
      left: this.getLeft(),
      top: startY,
      // top: startY + (CONNECTION_SIZE / 2) + (STROKE_WIDTH / 2) - STROKE_WIDTH,
      width: this.width,
      height,
    });

    return html`
      <svg class="edge" xmlns="http://www.w3.org/2000/svg" style=${style}>
        <path 
        stroke-linejoin="round"
        stroke-linecap="round"

        d="${this.renderPath()}" stroke-width="${STROKE_WIDTH}" stroke="rgb(81, 209, 255) " fill="transparent"/>
      </svg>
    `;
  }
}

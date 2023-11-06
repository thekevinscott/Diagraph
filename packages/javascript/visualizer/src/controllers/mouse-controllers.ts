import { LitElement, ReactiveController } from 'lit';

export class MouseController implements ReactiveController {
  host: LitElement;

  constructor(host: LitElement) {
    this.host = host;
    this.host.addController(this);
  }

  hostConnected() {
    // called when the host is connected
    this.host.addEventListener('mousedown', this._handleMouseDown);
  }

  disconnectedCallback() {
    this.host.removeEventListener('mousedown', this._handleMouseDown);
    this.host.removeEventListener('mousemove', this._handleMouseMove);
    this.host.removeEventListener('mouseup', this._handleMouseUp);
  }

  hostDisconnected() {
    // called when the host is disconnected
  }

  hostUpdate() {
    // called before the host updates
  }

  hostUpdated() {
    // called after the host updates
  }


  start = { x: 0, y: 0 };

  delta = { x: 0, y: 0 };

  _handleMouseDown = (e) => {
    this.start = { x: e.clientX - this.delta.x, y: e.clientY - this.delta.y };
    this.host.addEventListener('mousemove', this._handleMouseMove);
    this.host.addEventListener('mouseup', this._handleMouseUp);
  }

  _handleMouseMove = (e) => {
    this.delta = { x: e.clientX - this.start.x, y: e.clientY - this.start.y };
    this.host.requestUpdate();
  }

  _handleMouseUp = () => {
    this.host.removeEventListener('mousemove', this._handleMouseMove);
    this.host.removeEventListener('mouseup', this._handleMouseUp);
  }

}

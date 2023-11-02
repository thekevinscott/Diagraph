import { ReactiveController, ReactiveControllerHost } from 'lit';
import { WorkerHandler, } from '../utils/worker-handler.js';

export class KeyController implements ReactiveController {
  host: ReactiveControllerHost;
  keydown: (e: KeyboardEvent) => void;

  constructor(host: ReactiveControllerHost, keydown: (e: KeyboardEvent) => void) {
    (this.host = host).addController(this);
    this.keydown = keydown;
  }

  hostConnected() {
    window.addEventListener('keydown', this.keydown);
  }

  hostDisconnected() {
    window.removeEventListener('keydown', this.keydown);
  }
}

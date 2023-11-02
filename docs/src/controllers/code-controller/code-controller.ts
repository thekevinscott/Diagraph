import { ReactiveController, ReactiveControllerHost } from 'lit';
// import { property, state } from 'lit/decorators.js';
//
class WorkerHandler {
  worker: SharedWorker;

  constructor(url: URL, handleMessage?: (e) => void) {
    this.worker = new SharedWorker(url, { type: 'module' });
    this.worker.port.postMessage({ event: 'initialize' });
    if (handleMessage) {
      this.worker.port.onmessage = handleMessage;
    }
  }

  get port() {
    return this.worker.port;
  }
}

// create dummy worker to start it up
new WorkerHandler(new URL('./worker.ts', import.meta.url));

export class CodeController implements ReactiveController {
  host: ReactiveControllerHost;


  constructor(host: ReactiveControllerHost) {
    (this.host = host).addController(this);
    this.worker = new WorkerHandler(new URL('./worker.ts', import.meta.url), this.handleMessage);
  }


  output: string = '';
  logs: LogMessage[] = [];
  running = false;
  error: string | undefined;

  resetState() {
    this.running = false;
    this.logs = [];
    this.output = '';
    this.error = undefined;
    this.id = `${Math.random()}`;
  }

  public run(code: string) {
    this.resetState();
    this.running = true;
    this.worker.port.postMessage({
      event: 'run',
      code,
      id: this.id,
      // interruptBuffer: new Uint8Array(new SharedArrayBuffer(1)),
    });
    this.host.requestUpdate();
    return this.id;
  }

  public stop(code: string, runId: string) {
    this.worker.port.postMessage({
      event: 'stop',
      id: runId,
    });
    this.id = undefined;
    this.running = false;
    this.host.requestUpdate();
  }

  handleMessage = (e) => {
    const { data: { event, message, id } } = e;
    if (event === 'ready') {
      this.ready = true;
    }
    if (id === this.id) {
      console.log('event', event, message, id);
      if (event === 'output') {
        this.output = message;
        this.running = false;
      }
      if (['stdout', 'stderr'].includes(event)) {
        this.logs.push({ message, timestamp: new Date(), kind: event });
      }
      if (event === 'error') {
        this.error = message;
        this.running = false;
      }
      this.host.requestUpdate();
    }
  };

  hostConnected() {
  }

  hostDisconnected() {
  }
}




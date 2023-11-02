// // importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");
import { loadPyodide } from 'pyodide';
import diagraph from '../../../static/diagraph-0.1.2-py3-none-any.whl?url'

import { ChatWorkerHandler, ChatModule } from "@mlc-ai/web-llm";

// Hookup a chat module to a worker handler
const chat = new ChatModule();
const handler = new ChatWorkerHandler(chat);
self.onmessage = (msg: MessageEvent) => {
  handler.onmessage(msg);
};


class Logger {
  callbacks = new Map();
  stdout = (...messages) => {
    for (const [id, { stdout }] of this.callbacks.entries()) {
      stdout(...messages);
    }
  }
  stderr = (...messages) => {
    for (const [id, { stderr }] of this.callbacks.entries()) {
      stderr(...messages);
    }
  }

  register = (id, stdout, stderr) => {
    this.callbacks.set(id, { stdout, stderr });
  }

  deregister = (id) => {
    this.callbacks.delete(id);
  }
}
const logger = new Logger();

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
    stdout: logger.stdout,
    stderr: logger.stderr,
  });

  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  await micropip.install(diagraph, {
    keepGoing: true,
  })
  // console.log('1')
  // await micropip.install('diagraph', {
  //   keepGoing: true,
  // })
  // console.log('2')
};

const pyodideReadyPromise = loadPyodideAndPackages();

const interruptBuffers = new Map<string, Uint8Array>();
onconnect = async (e) => {
  const port = e.ports[0];

  port.onmessage = async ({ data: { event, id, code } }) => {
    if (event === 'stop') {
      console.log('stop!');
      interruptBuffers[id] = 2;
      console.log('stopped!');
    }
    if (event === 'run') {
      const interruptBuffer = new Uint8Array(new ArrayBuffer(1));
      interruptBuffers[id] = interruptBuffer;
      try {
        const stdout = (...message) => {
          port.postMessage({ event: 'stdout', message, id });
        };
        const stderr = (...message) => {
          port.postMessage({ event: 'stdout', message, id });
        };
        logger.register(id, stdout, stderr);
        port.postMessage({ event: 'start', id });
        await pyodideReadyPromise;
        await self.pyodide.loadPackagesFromImports(code);

        const message = await self.pyodide.runPythonAsync(`
import js
class VicunaLLM:
  pass
from diagraph import Diagraph
# Diagraph.set_llm(VicunaLLM())
${code}
`.trim());
        // const message = self.pyodide.runPython(`'foo'`);
        port.postMessage({ event: 'output', message, id });
      } catch (error) {
        port.postMessage({ event: 'error', message: error.message, id });
      } finally {
        logger.deregister(id);
      }

    } else if (event === 'initialize') {
      await pyodideReadyPromise;
      port.postMessage({ event: 'ready' });
    }
  };
};

// // importScripts("https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js");
import { loadPyodide } from 'pyodide';
import { LLM } from "@mlc-ai/web-llm";
const llm = new LLM({ model: 'vicuna-7b' });
const pipeline = await llm.pipeline();
const out = await pipeline('hi, who are u')
console.log('out', out)

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
  await micropip.install('/diagraph-0.1.2-py3-none-any.whl', {
    keepGoing: true,
  })
};

const pyodideReadyPromise = loadPyodideAndPackages();

onconnect = async (e) => {
  const port = e.ports[0];

  port.onmessage = async ({ data: { event, id, code } }) => {
    if (event === 'run') {
      try {
        const stdout = (...message) => {
          port.postMessage({ event: 'stdout', message, id });
        };
        const stderr = (...message) => {
          port.postMessage({ event: 'stdout', message, id });
        };
        logger.register(id, stdout, stderr);
        // self.pyodide = await loadPyodide({
        //   indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/",
        //   stdout,
        //   stderr,
        // });
        port.postMessage({ event: 'start', id });
        // await self.pyodide.loadPackagesFromImports(code);
        const message = await self.pyodide.runPythonAsync(`
import js
class VicunaLLM:
  pass
from diagraph import Diagraph
Diagraph.set_llm(VicunaLLM())
${code}`);
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

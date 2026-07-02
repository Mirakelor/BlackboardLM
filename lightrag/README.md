# LightRAG

Lightweight Retrieval-Augmented Generation library with Knowledge Graph.  
Runs natively in browser and Node.js via Transformers.js.

## Install

```bash
npm install lightrag
```

## Usage

```js
const { pipeline } = require('@huggingface/transformers');
const { LightRAG, Embedder } = require('lightrag');

const _pipe = await pipeline('feature-extraction', 'Xenova/multilingual-e5-small', { dtype: 'fp32' });
const _embedder = new Embedder(_pipe);
const _rag = new LightRAG({ embedder: _embedder, llmFunc: yourLLMFunction });

await _rag.insert('Your document text here...');

const _answer = await _rag.query('What is this about?', { mode: 'hybrid' });
console.log(_answer);
```

## API

### `new LightRAG(opts)`
- `opts.llmFunc` — async function `(prompt, options) => string`
- `opts.embedder` — `Embedder` instance
- `opts.chunkSize` — chunk size in characters (default: `3000`)
- `opts.chunkOverlap` — overlap in characters (default: `150`)

### `rag.insert(text)`
Insert document text. Chunks, embeds, and extracts entities+relations into knowledge graph.

### `rag.query(question, options)`
Query with RAG. `options.mode`: `'naive'` | `'local'` | `'global'` | `'hybrid'` | `'mix'`

### `rag.getGraphData()`
Returns `{ nodes, edges }` — nodes with `id, entity_type, description, degree`, edges with `source, target, keywords, weight`.

### `rag.toJSON()` / `LightRAG.fromJSON(data, opts)`
Serialize/deserialize the entire RAG state.

## License

MIT

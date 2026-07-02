# LightRAG

Lightweight Retrieval-Augmented Generation library with Knowledge Graph.  
Runs in Node.js (CommonJS) and browsers (Web Worker, no bundler required).

## Install

```bash
npm install lightrag
```

## Usage

### Node.js

```js
const { pipeline } = require('@huggingface/transformers');
const { LightRAG, Embedder } = require('lightrag');

(async () => {
    const _pipe = await pipeline('feature-extraction', 'Xenova/multilingual-e5-small', { dtype: 'fp32' });
    const _embedder = new Embedder(_pipe);
    const _rag = new LightRAG({
        embedder: _embedder,
        tokenizer: _pipe.tokenizer,
        llmFunc: async (prompt, opts = {}) => {
            const _resp = await fetch('https://api.deepseek.com/v1/chat/completions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer YOUR_KEY' },
                body: JSON.stringify({ model: 'deepseek-v4-flash', messages: [{ role: 'user', content: prompt }] }),
            });
            const _json = await _resp.json();
            return _json.choices?.[0]?.message?.content || '';
        },
    });

    await _rag.insert('Your document text here...');
    const _answer = await _rag.query('What is this about?', { mode: 'hybrid' });
    console.log(_answer);
})();
```

### Browser (Web Worker)

Load Transformers.js from CDN in your Worker, then create a LightRAG instance. The `storage.js` module provides IndexedDB persistence for saving/restoring RAG state across page reloads.

```js
import { pipeline, env } from 'https://unpkg.com/@huggingface/transformers@4.2.0/dist/transformers.js';

env.allowLocalModels = false;
env.useBrowserCache = true;

const _pipe = await pipeline('feature-extraction', 'Xenova/multilingual-e5-small', { dtype: 'fp32' });
const _embedder = new Embedder(_pipe);
const _rag = new LightRAG({
    embedder: _embedder,
    tokenizer: _pipe.tokenizer,
    llmFunc: async (prompt) => {
        const _resp = await fetch('https://api.deepseek.com/v1/chat/completions', { ... });
        const _json = await _resp.json();
        return _json.choices?.[0]?.message?.content || '';
    },
});

await _rag.insert(documentText);
const _context = await _rag.buildContext(question, 'hybrid');
```

See the [BlackboardLM](https://github.com/Mirakelor/BlackboardLM) project for a complete browser integration example using Web Workers, IndexedDB persistence, and streaming LLM responses.

## API

### `new LightRAG(opts)`

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `opts.llmFunc` | `async (prompt, options) => string` | **required** | LLM call function |
| `opts.embedder` | `Embedder` | **required** | Transformers.js embedder instance |
| `opts.tokenizer` | tokenizer | — | Tokenizer for token-counting chunker (falls back to character-based) |
| `opts.embeddingDim` | `number` | `384` | Embedding vector dimension |
| `opts.chunkSize` | `number` | `480` | Max tokens per chunk (with tokenizer) or chars (without) |
| `opts.chunkOverlap` | `number` | `50` | Overlap tokens (or chars) between chunks |
| `opts.maxEntityTokens` | `number` | `96000` | Max characters sent to LLM for entity extraction per chunk |

### `rag.insert(text)`

Inserts document text: tokenizes → chunks → embeds each chunk into vector DB → extracts entities & relations into knowledge graph.

### `rag.query(question, options)`

Query with RAG. Calls `llmFunc` with the question, system prompt (including retrieved context), and conversation history.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `options.mode` | `string` | `'hybrid'` | `'naive'` \| `'local'` \| `'global'` \| `'hybrid'` \| `'mix'` |
| `options.systemPrompt` | `string` | `''` | System prompt prepended to LLM context |
| `options.history` | `array` | `[]` | Conversation history `[{role, content}]` |
| `options.stream` | `boolean` | `false` | Passed through to `llmFunc` |

### `rag.buildContext(question, mode)`

Returns the retrieved context string for a given question and mode, **without** calling the LLM. Useful when you want to handle the LLM call yourself (e.g., for streaming).

| Arg | Type | Description |
|-----|------|-------------|
| `question` | `string` | The query to build context for |
| `mode` | `string` | Retrieval mode (`'local'` / `'global'` / `'hybrid'` / `'mix'`) |

Returns `''` for `'naive'` mode or when no documents are indexed.

### `rag.getGraphData()`

Returns `{ nodes, edges }` — nodes with `id, entity_type, description, degree`; edges with `source, target, keywords, weight`.

### `rag.getProgress()`

Returns `{ total, ready, isInserting, isReady }` — insertion progress.

### `rag.vdbSize`

Getter returning the number of vectors currently stored (read-only).

### `rag.toJSON()` / `LightRAG.fromJSON(data, opts)`

Serialize/deserialize the entire RAG state (vector DB + knowledge graph). Use with `storage.js` for IndexedDB persistence in browsers, or with `fs` in Node.js.

## Storage (Browser)

`lightrag/src/storage.js` provides a simple IndexedDB wrapper for persisting RAG state:

```js
import { Storage } from 'lightrag/src/storage.js';

await Storage.save('rag_state', rag.toJSON());
const _data = await Storage.load('rag_state');
const _rag = LightRAG.fromJSON(_data, opts);
await Storage.clear();
```

## License

MIT

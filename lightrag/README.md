# LightRAG

Lightweight Retrieval-Augmented Generation library with Knowledge Graph.  
Runs in Node.js (CommonJS). Browser usage requires a bundler.

## Install

```bash
npm install lightrag
```

## Usage

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
            // call your LLM API here, return string
        },
    });

    await _rag.insert('Your document text here...');

    const _answer = await _rag.query('What is this about?', { mode: 'hybrid' });
    console.log(_answer);
})();
```

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

Query with RAG.

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `options.mode` | `string` | `'hybrid'` | `'naive'` \| `'local'` \| `'global'` \| `'hybrid'` \| `'mix'` |
| `options.systemPrompt` | `string` | `''` | System prompt prepended to LLM context |
| `options.history` | `array` | `[]` | Conversation history `[{role, content}]` |
| `options.stream` | `boolean` | `false` | Whether the LLM should stream (passed to `llmFunc`) |

### `rag.getGraphData()`

Returns `{ nodes, edges }` — nodes with `id, entity_type, description, degree`; edges with `source, target, keywords, weight`.

### `rag.getProgress()`

Returns `{ total, ready, isInserting, isReady }` — insertion progress.

### `rag.toJSON()` / `LightRAG.fromJSON(data, opts)`

Serialize/deserialize the entire RAG state (vector DB + knowledge graph).

## License

MIT

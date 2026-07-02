import { pipeline, env } from 'https://unpkg.com/@huggingface/transformers@4.2.0/dist/transformers.js';

env.allowLocalModels = false;
env.useBrowserCache = true;

const _MODEL = 'Xenova/multilingual-e5-small';
const _CHUNK_SIZE = 480;
const _CHUNK_OVERLAP = 50;
const _EMBEDDING_DIM = 384;
const _MAX_ENTITY_TOKENS = 96000;
const _STORAGE_KEY = 'rag_state';
const _DB_NAME = 'blackboardlm_rag';
const _DB_VERSION = 1;
const _STORE_NAME = 'rag_data';

let _pipe = null;
let _embedder = null;
let _rag = null;
let _llmConfig = {
  apiKey: '',
  baseUrl: 'https://api.deepseek.com',
  model: 'deepseek-v4-flash',
  thinking: 'disabled',
  reasoningEffort: 'max',
  maxTokens: 16384,
  proxyUrl: '/api/hf-proxy',
};

const ENTITY_EXTRACTION_PROMPT = `---Role---
You are an expert knowledge graph builder. Extract entities and relationships from the text.

---Goal---
Given a text chunk, identify ALL named entities (people, places, organizations, concepts, events, dates, technologies) and the relationships between them.

---Output Format---
Return a JSON object with "entities" and "relations":
{
  "entities": [
    {"name": "Entity", "type": "PERSON|ORGANIZATION|LOCATION|CONCEPT|EVENT|DATE|TECH", "description": "Brief description"}
  ],
  "relations": [
    {"source": "Entity A", "target": "Entity B", "keywords": "relationship", "weight": 1.0}
  ]
}

---Rules---
- Entity name under 60 chars, description under 120 chars
- Extract at least 3 entities per chunk
- Weight between 0.5 (weak) and 1.5 (strong)
- Return ONLY valid JSON, no other text.

---Text---
{text}`;

class KnowledgeGraph {
  constructor() {
    this._nodes = new Map();
    this._edges = [];
    this._adj = new Map();
  }
  upsertNode(id, data = {}) {
    if (!this._nodes.has(id)) {
      this._nodes.set(id, { id, entity_type: data.entity_type || '', description: data.description || '' });
      this._adj.set(id, new Map());
    } else {
      const _n = this._nodes.get(id);
      if (data.description && data.description.length > _n.description.length) _n.description = data.description;
      if (data.entity_type) _n.entity_type = data.entity_type;
    }
  }
  upsertEdge(source, target, data = {}) {
    if (!this._nodes.has(source)) this.upsertNode(source);
    if (!this._nodes.has(target)) this.upsertNode(target);
    const _e = { source, target, keywords: data.keywords || '', weight: data.weight || 1 };
    this._edges.push(_e);
    const _adjSource = this._adj.get(source);
    if (_adjSource) _adjSource.set(target, _e);
    const _adjTarget = this._adj.get(target);
    if (_adjTarget) _adjTarget.set(source, _e);
  }
  getAllNodes() {
    return Array.from(this._nodes.values()).map(_n => ({
      id: _n.id, entity_type: _n.entity_type, description: _n.description,
      degree: (this._adj.get(_n.id)?.size || 0),
    }));
  }
  getAllEdges() {
    return this._edges
      .filter(_e => this._nodes.has(_e.source) && this._nodes.has(_e.target))
      .map(_e => ({ source: _e.source, target: _e.target, keywords: _e.keywords, weight: _e.weight }));
  }
  get size() { return this._nodes.size; }
  toJSON() {
    return {
      nodes: Array.from(this._nodes.entries()),
      edges: this._edges,
      adj: Array.from(this._adj.entries()).map(([k, v]) => [k, Array.from(v.entries())]),
    };
  }
  static fromJSON(data) {
    const _g = new KnowledgeGraph();
    if (data.nodes) for (const [k, v] of data.nodes) _g._nodes.set(k, v);
    if (data.edges) _g._edges = data.edges;
    if (data.adj) for (const [k, entries] of data.adj) {
      const _m = new Map();
      for (const [k2, v] of entries) _m.set(k2, v);
      _g._adj.set(k, _m);
    }
    return _g;
  }
}

class VectorDB {
  constructor(dim) {
    this._dim = dim;
    this._vectors = [];
    this._meta = [];
  }
  async upsert(entries) {
    for (const _e of entries) {
      const _idx = this._meta.findIndex(_m => _m.id === _e.id);
      if (_idx >= 0) {
        this._vectors[_idx] = _e.vector;
        this._meta[_idx] = { id: _e.id, text: _e.text || '' };
      } else {
        this._vectors.push(_e.vector);
        this._meta.push({ id: _e.id, text: _e.text || '' });
      }
    }
  }
  async query(vector, topK = 10) {
    if (this._vectors.length === 0) return [];
    const _scores = this._vectors.map((_v, _i) => ({
      index: _i,
      score: _cosineSim(vector, _v),
      id: this._meta[_i].id,
      text: this._meta[_i].text,
    }));
    _scores.sort((_a, _b) => _b.score - _a.score);
    return _scores.slice(0, topK);
  }
  get size() { return this._vectors.length; }
  toJSON() {
    return { dim: this._dim, vectors: this._vectors, meta: this._meta };
  }
  static fromJSON(data) {
    const _db = new VectorDB(data.dim);
    _db._vectors = data.vectors || [];
    _db._meta = data.meta || [];
    return _db;
  }
}

function _cosineSim(a, b) {
  let _dot = 0, _na = 0, _nb = 0;
  for (let _i = 0; _i < a.length; _i++) { _dot += a[_i] * b[_i]; _na += a[_i] * a[_i]; _nb += b[_i] * b[_i]; }
  _na = Math.sqrt(_na); _nb = Math.sqrt(_nb);
  return (_na && _nb) ? _dot / (_na * _nb) : 0;
}

class TokenChunker {
  constructor(tokenizer, tokenLimit = 480, overlapTokens = 50) {
    this._tokenizer = tokenizer;
    this._tokenLimit = tokenLimit;
    this._overlapTokens = overlapTokens;
  }
  chunk(text) {
    if (!this._tokenizer) {
      const _chunks = [];
      let _start = 0;
      while (_start < text.length) {
        const _end = Math.min(_start + 3000, text.length);
        _chunks.push(text.slice(_start, _end));
        if (_end >= text.length) break;
        _start = _end - 150;
      }
      return _chunks;
    }
    const _tokens = this._tokenizer.encode(text);
    const _chunks = [];
    let _start = 0;
    while (_start < _tokens.length) {
      const _end = Math.min(_start + this._tokenLimit, _tokens.length);
      const _chunkTokens = _tokens.slice(_start, _end);
      const _chunkText = this._tokenizer.decode(_chunkTokens, { skip_special_tokens: true });
      _chunks.push(_chunkText);
      if (_end >= _tokens.length) break;
      _start = _end - this._overlapTokens;
    }
    return _chunks;
  }
}

class Embedder {
  constructor(pipeline) {
    this._pipe = pipeline;
  }
  async embed(texts, context = 'document') {
    const _prefix = context === 'query' ? 'query: ' : 'passage: ';
    const _prefixed = texts.map(_t => _prefix + _t);
    const _output = await this._pipe(_prefixed, { pooling: 'mean', normalize: true });
    return _output.tolist();
  }
  async embedQuery(query) {
    return (await this.embed([query], 'query'))[0];
  }
  async embedDocuments(docs) {
    return await this.embed(docs, 'document');
  }
}

class LightRAG {
  constructor(opts = {}) {
    this._llmFunc = opts.llmFunc;
    this._embedder = opts.embedder;
    this._embeddingDim = opts.embeddingDim || 384;
    this._chunkSize = opts.chunkSize || 480;
    this._chunkOverlap = opts.chunkOverlap || 50;
    this._maxEntityTokens = opts.maxEntityTokens || 96000;
    this._chunker = new TokenChunker(opts.tokenizer, this._chunkSize, this._chunkOverlap);
    this._vdb = new VectorDB(this._embeddingDim);
    this._graph = new KnowledgeGraph();
    this._progress = { total: 0, ready: 0, isInserting: false, isReady: true };
  }

  async insert(text) {
    const _chunks = this._chunker.chunk(text);
    this._progress = { total: _chunks.length, ready: 0, isInserting: true, isReady: false };
    for (let _i = 0; _i < _chunks.length; _i++) {
      const _chunk = _chunks[_i];
      const _id = `chunk_${Date.now()}_${_i}`;
      const _vectors = await this._embedder.embedDocuments([_chunk]);
      const _vec = new Float32Array(_vectors[0]);
      await this._vdb.upsert([{ id: _id, vector: Array.from(_vec), text: _chunk }]);
      await this._extractEntities(_chunk, _id);
      this._progress.ready = _i + 1;
      self.postMessage({ type: 'progress', total: _chunks.length, ready: _i + 1, isInserting: true, isReady: false });
    }
    this._progress.isInserting = false;
    this._progress.isReady = true;
    self.postMessage({ type: 'progress', total: _chunks.length, ready: _chunks.length, isInserting: false, isReady: true });
  }

  async _extractEntities(text, sourceId) {
    const _prompt = ENTITY_EXTRACTION_PROMPT.replace('{text}', text.slice(0, this._maxEntityTokens));
    try {
      const _raw = await this._llmFunc(_prompt);
      const _json = _parseJson(_raw);
      if (_json && _json.entities) {
        for (const _e of _json.entities) {
          const _name = (_e.name || '').trim().replace(/(?:^|\s+)([a-z])/g, (_m, _c) => _m[0] === ' ' ? ' ' + _c.toUpperCase() : _c.toUpperCase());
          if (!_name) continue;
          this._graph.upsertNode(_name, { entity_type: _e.type || '', description: _e.description || '', source_id: sourceId });
        }
      }
      if (_json && _json.relations) {
        for (const _r of _json.relations) {
          const _s = (_r.source || '').trim().replace(/(?:^|\s+)([a-z])/g, (_m, _c) => _m[0] === ' ' ? ' ' + _c.toUpperCase() : _c.toUpperCase());
          const _t = (_r.target || '').trim().replace(/(?:^|\s+)([a-z])/g, (_m, _c) => _m[0] === ' ' ? ' ' + _c.toUpperCase() : _c.toUpperCase());
          if (!_s || !_t) continue;
          this._graph.upsertEdge(_s, _t, { keywords: _r.keywords || '', weight: _r.weight || 1, source_id: sourceId });
        }
      }
    } catch (_e) {
      self.postMessage({ type: 'error', message: `Entity extraction failed: ${_e.message}` });
    }
  }

  async buildContext(question, mode) {
    if (mode === 'naive' || this._vdb.size === 0) return '';
    const _qVec = await this._embedder.embedQuery(question);
    return await this._buildContext(new Float32Array(_qVec), mode);
  }

  async _buildContext(_qVec, mode) {
    let _parts = [];
    if (mode === 'local' || mode === 'hybrid' || mode === 'mix') {
      const _chunks = await this._vdb.query(Array.from(_qVec), 5);
      if (_chunks.length) _parts.push('=== Relevant Document Chunks ===\n' + _chunks.map(_c => `[${_c.id}] ${_c.text}`).join('\n\n'));
    }
    if (mode === 'global' || mode === 'hybrid' || mode === 'mix') {
      const _nodes = this._graph.getAllNodes();
      const _sorted = _nodes.sort((_a, _b) => _b.degree - _a.degree).slice(0, 20);
      if (_sorted.length) {
        _parts.push('=== Knowledge Graph Entities ===\n' + _sorted.map(_n => `- ${_n.id} [${_n.entity_type}]: ${_n.description}`).join('\n'));
      }
    }
    return _parts.join('\n\n');
  }

  getGraphData() {
    return { nodes: this._graph.getAllNodes(), edges: this._graph.getAllEdges() };
  }

  getProgress() { return { ...this._progress }; }

  get vdbSize() { return this._vdb.size; }

  toJSON() {
    return {
      embeddingDim: this._embeddingDim,
      vdb: this._vdb.toJSON(),
      graph: this._graph.toJSON(),
    };
  }

  static fromJSON(data, opts = {}) {
    const _rag = new LightRAG({ ...opts, embeddingDim: data.embeddingDim || 384 });
    _rag._vdb = VectorDB.fromJSON(data.vdb || {});
    _rag._graph = KnowledgeGraph.fromJSON(data.graph || {});
    return _rag;
  }
}

function _parseJson(raw) {
  let _s = raw.trim();
  if (_s.startsWith('```')) _s = _s.replace(/```\w*\n?/g, '').trim();
  try { return JSON.parse(_s); } catch (_e) {}
  const _m = _s.match(/\{[\s\S]*\}/);
  if (_m) try { return JSON.parse(_m[0]); } catch (_e) {}
  return null;
}

function _openDB() {
  return new Promise((_resolve, _reject) => {
    const _req = indexedDB.open(_DB_NAME, _DB_VERSION);
    _req.onupgradeneeded = (_e) => {
      const _db = _e.target.result;
      if (!_db.objectStoreNames.contains(_STORE_NAME)) {
        _db.createObjectStore(_STORE_NAME);
      }
    };
    _req.onsuccess = (_e) => _resolve(_e.target.result);
    _req.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _dbSave(key, data) {
  const _db = await _openDB();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readwrite');
    const _store = _tx.objectStore(_STORE_NAME);
    _store.put(data, key);
    _tx.oncomplete = () => _resolve();
    _tx.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _dbLoad(key) {
  const _db = await _openDB();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readonly');
    const _store = _tx.objectStore(_STORE_NAME);
    const _req = _store.get(key);
    _req.onsuccess = (_e) => _resolve(_e.target.result);
    _req.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _dbClear() {
  const _db = await _openDB();
  return new Promise((_resolve, _reject) => {
    const _tx = _db.transaction(_STORE_NAME, 'readwrite');
    const _store = _tx.objectStore(_STORE_NAME);
    _store.clear();
    _tx.oncomplete = () => _resolve();
    _tx.onerror = (_e) => _reject(_e.target.error);
  });
}

async function _saveState() {
  if (!_rag) return;
  await _dbSave(_STORAGE_KEY, _rag.toJSON());
}

async function _loadState() {
  try {
    const _data = await _dbLoad(_STORAGE_KEY);
    if (_data && _embedder) {
      _rag = LightRAG.fromJSON(_data, {
        embedder: _embedder,
        llmFunc: _entityExtractionLLM,
        tokenizer: _pipe?.tokenizer,
        embeddingDim: _EMBEDDING_DIM,
        chunkSize: _CHUNK_SIZE,
        chunkOverlap: _CHUNK_OVERLAP,
        maxEntityTokens: _MAX_ENTITY_TOKENS,
      });
      return true;
    }
  } catch (_e) {
    self.postMessage({ type: 'error', message: `Failed to load state: ${_e.message}` });
  }
  return false;
}

async function _entityExtractionLLM(prompt) {
  const _resp = await fetch(`${_llmConfig.baseUrl}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${_llmConfig.apiKey}` },
    body: JSON.stringify({
      model: _llmConfig.model,
      messages: [{ role: 'user', content: prompt }],
      temperature: 0.3,
      max_tokens: 4096,
      stream: false,
      extra_body: {
        thinking: { type: _llmConfig.thinking },
        reasoning_effort: _llmConfig.reasoningEffort,
      },
    }),
  });
  if (!_resp.ok) throw new Error(`LLM API error: ${_resp.status} ${_resp.statusText}`);
  const _json = await _resp.json();
  return _json.choices?.[0]?.message?.content || '';
}

async function _streamLLM(messages) {
  const _resp = await fetch(`${_llmConfig.baseUrl}/v1/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${_llmConfig.apiKey}` },
    body: JSON.stringify({
      model: _llmConfig.model,
      messages: messages,
      temperature: 0.7,
      max_tokens: _llmConfig.maxTokens,
      stream: true,
      extra_body: {
        thinking: { type: _llmConfig.thinking },
        reasoning_effort: _llmConfig.reasoningEffort,
      },
    }),
  });
  if (!_resp.ok) throw new Error(`LLM API error: ${_resp.status} ${_resp.statusText}`);
  const _reader = _resp.body.getReader();
  const _decoder = new TextDecoder();
  let _buf = '';
  while (true) {
    const { done, value } = await _reader.read();
    if (done) break;
    _buf += _decoder.decode(value, { stream: true });
    const _lines = _buf.split('\n');
    _buf = _lines.pop();
    for (const _line of _lines) {
      if (!_line.startsWith('data: ')) continue;
      const _data = _line.slice(6);
      if (_data === '[DONE]') return;
      try {
        const _json = JSON.parse(_data);
        const _content = _json.choices?.[0]?.delta?.content || '';
        if (_content) {
          self.postMessage({ type: 'chunk', text: _content });
        }
      } catch (_e) {}
    }
  }
}

async function _init(opts = {}) {
  console.log('[rag.worker] _init called, opts:', { apiKey: opts.apiKey ? '***' : '(empty)', baseUrl: opts.baseUrl, model: opts.model });
  if (opts.apiKey) _llmConfig.apiKey = opts.apiKey;
  if (opts.baseUrl) _llmConfig.baseUrl = opts.baseUrl;
  if (opts.model) _llmConfig.model = opts.model;
  if (opts.thinking) _llmConfig.thinking = opts.thinking;
  if (opts.reasoningEffort) _llmConfig.reasoningEffort = opts.reasoningEffort;
  if (opts.maxTokens) _llmConfig.maxTokens = opts.maxTokens;
  if (opts.proxyUrl) { _llmConfig.proxyUrl = opts.proxyUrl; env.remoteHost = opts.proxyUrl; }

  if (_pipe) {
    console.log('[rag.worker] _init: already initialized');
    return { alreadyInit: true };
  }

  const _start = Date.now();
  console.log('[rag.worker] Loading model:', _MODEL);
  _pipe = await pipeline('feature-extraction', _MODEL, {
    dtype: 'fp32',
    progress_callback: (_info) => {
      if (_info.status === 'progress' && _info.total) {
        const _pct = Math.round(_info.loaded * 100 / _info.total);
        if (_info.loaded % 5 === 0 || _pct === 100) {
          console.log('[rag.worker] Model download:', _pct + '%', _info.file || '');
        }
        self.postMessage({ type: 'init_progress', loaded: _info.loaded, total: _info.total, file: _info.file });
      }
    },
  });
  console.log('[rag.worker] Model loaded in', Date.now() - _start, 'ms');
  _embedder = new Embedder(_pipe);

  const _loaded = await _loadState();
  if (!_loaded) {
    _rag = new LightRAG({
      embedder: _embedder,
      llmFunc: _entityExtractionLLM,
      tokenizer: _pipe.tokenizer,
      embeddingDim: _EMBEDDING_DIM,
      chunkSize: _CHUNK_SIZE,
      chunkOverlap: _CHUNK_OVERLAP,
      maxEntityTokens: _MAX_ENTITY_TOKENS,
    });
  }

  const _elapsed = Date.now() - _start;
  self.postMessage({ type: 'ready', model: _MODEL, initMs: _elapsed, hasData: _rag.vdbSize > 0 });
}

async function _handleQuery(data) {
  if (!_rag) throw new Error('RAG not initialized');
  const _mode = data.mode || 'hybrid';
  let _context = '';
  if (_mode !== 'naive' && _rag.vdbSize > 0) {
    _context = await _rag.buildContext(data.question, _mode);
  }
  const _sysPrompt = (data.systemPrompt || '') + (_context ? `\n\n---Context from your documents---\n${_context}` : '');
  const _messages = [];
  if (_sysPrompt) _messages.push({ role: 'system', content: _sysPrompt });
  if (data.history) _messages.push(...data.history);
  _messages.push({ role: 'user', content: data.question });
  await _streamLLM(_messages);
}

self.onmessage = async (_e) => {
  const { type, data } = _e.data;
  console.log('[rag.worker] Received:', type, data ? Object.keys(data) : null);
  try {
    switch (type) {
      case 'init':
        console.log('[rag.worker] Init start');
        await _init(data);
        console.log('[rag.worker] Init done, pipe:', !!_pipe, 'rag:', !!_rag, 'vdb_size:', _rag ? _rag.vdbSize : 0);
        break;
      case 'insert':
        if (!_rag) throw new Error('RAG not initialized. Send "init" first.');
        console.log('[rag.worker] Insert start, text length:', (data.text || '').length);
        await _rag.insert(data.text);
        await _saveState();
        self.postMessage({ type: 'insert_done', graph: _rag.getGraphData() });
        console.log('[rag.worker] Insert done, vdb_size:', _rag.vdbSize);
        break;
      case 'query':
        console.log('[rag.worker] Query start:', (data.question || '').slice(0, 50));
        await _handleQuery(data || {});
        self.postMessage({ type: 'done' });
        console.log('[rag.worker] Query done');
        break;
      case 'graph':
        if (_rag) {
          const _g = _rag.getGraphData();
          console.log('[rag.worker] Graph:', _g.nodes.length, 'nodes,', _g.edges.length, 'edges');
          self.postMessage({ type: 'graph', ..._g });
        } else {
          self.postMessage({ type: 'graph', nodes: [], edges: [] });
        }
        break;
      case 'reset':
        console.log('[rag.worker] Reset');
        _rag = null;
        if (_embedder && _pipe) {
          _rag = new LightRAG({
            embedder: _embedder,
            llmFunc: _entityExtractionLLM,
            tokenizer: _pipe.tokenizer,
            embeddingDim: _EMBEDDING_DIM,
            chunkSize: _CHUNK_SIZE,
            chunkOverlap: _CHUNK_OVERLAP,
            maxEntityTokens: _MAX_ENTITY_TOKENS,
          });
        }
        await _dbClear();
        self.postMessage({ type: 'reset_done' });
        break;
      case 'set_config':
        console.log('[rag.worker] set_config, apiKey:', data.apiKey ? '***' : '(empty)');
        if (data.apiKey !== undefined) _llmConfig.apiKey = data.apiKey;
        if (data.baseUrl !== undefined) _llmConfig.baseUrl = data.baseUrl;
        if (data.model !== undefined) _llmConfig.model = data.model;
        if (data.thinking !== undefined) _llmConfig.thinking = data.thinking;
        if (data.reasoningEffort !== undefined) _llmConfig.reasoningEffort = data.reasoningEffort;
        if (data.maxTokens !== undefined) _llmConfig.maxTokens = data.maxTokens;
        if (data.proxyUrl !== undefined) { _llmConfig.proxyUrl = data.proxyUrl; env.remoteHost = data.proxyUrl; }
        self.postMessage({ type: 'config_set' });
        break;
      default:
        console.error('[rag.worker] Unknown action:', type);
        self.postMessage({ type: 'error', message: `Unknown action: ${type}` });
    }
  } catch (_err) {
    console.error('[rag.worker] Error:', _err.message, _err.stack);
    self.postMessage({ type: 'error', message: _err.message });
  }
};

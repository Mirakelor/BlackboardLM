const { TokenChunker } = require('./chunker');
const { VectorDB } = require('./vector_db');
const { KnowledgeGraph } = require('./graph');
const { ENTITY_EXTRACTION_PROMPT } = require('./prompts');

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
        console.error(`[LightRAG] Chunked text (token_limit=${this._chunkSize}, overlap=${this._chunkOverlap}) into ${_chunks.length} chunks`);
        this._progress = { total: _chunks.length, ready: 0, isInserting: true, isReady: false };
        for (let _i = 0; _i < _chunks.length; _i++) {
            const _chunk = _chunks[_i];
            const _id = `chunk_${Date.now()}_${_i}`;
            console.error(`[LightRAG] Embedding chunk ${_i + 1}/${_chunks.length} (${_chunk.length} chars)`);
            const _vectors = await this._embedder.embedDocuments([_chunk]);
            const _vec = new Float32Array(_vectors[0]);
            await this._vdb.upsert([{ id: _id, vector: Array.from(_vec), text: _chunk }]);
            console.error(`[LightRAG] Extracting entities from chunk ${_i + 1}/${_chunks.length}`);
            await this._extractEntities(_chunk, _id);
            this._progress.ready = _i + 1;
        }
        console.error(`[LightRAG] Insert complete: ${this._vdb.size} vectors, ${this._graph.size} entities`);
        this._progress.isInserting = false;
        this._progress.isReady = true;
    }

    async _extractEntities(text, sourceId) {
        console.error(`[LightRAG] Calling LLM for entity extraction (${text.length} chars)`);
        const _prompt = ENTITY_EXTRACTION_PROMPT.replace('{text}', text.slice(0, this._maxEntityTokens));
        try {
            const _raw = await this._llmFunc(_prompt);
            const _json = this._parseJson(_raw);
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
            const _ec = _json?.entities?.length || 0;
            const _rc = _json?.relations?.length || 0;
            console.error(`[LightRAG] Entity extraction done: ${_ec} entities, ${_rc} relations`);
        } catch (_e) {
            console.error(`[LightRAG] Entity extraction failed: ${_e.message}`);
        }
    }

    _parseJson(raw) {
        let _s = raw.trim();
        if (_s.startsWith('```')) _s = _s.replace(/```\w*\n?/g, '').trim();
        try { return JSON.parse(_s); } catch (_e) {}
        const _m = _s.match(/\{[\s\S]*\}/);
        if (_m) try { return JSON.parse(_m[0]); } catch (_e) {}
        return null;
    }

    async query(question, options = {}) {
        const _mode = options.mode || 'hybrid';
        console.error(`[LightRAG] Query in "${_mode}" mode: "${question.slice(0, 80)}..."`);
        if (_mode === 'naive' || this._vdb.size === 0) {
            console.error(`[LightRAG] No retrieval needed (mode=${_mode}, vdb_size=${this._vdb.size})`);
            return await this._llmFunc(question, { system_prompt: options.systemPrompt || '', history: options.history || [], stream: options.stream });
        }
        const _qVec = await this._embedder.embedQuery(question);
        const _context = await this._buildContext(new Float32Array(_qVec), _mode);
        console.error(`[LightRAG] Context built: ${_context.length} chars`);
        const _sysPrompt = (options.systemPrompt || '') + (_context ? `\n\n---Context from your documents---\n${_context}` : '');
        return await this._llmFunc(question, { system_prompt: _sysPrompt, history: options.history || [], stream: options.stream });
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

module.exports = { LightRAG };

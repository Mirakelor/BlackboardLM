const { pipeline, env } = require('@huggingface/transformers');
const { LightRAG, Embedder } = require('./src/index');
const fs = require('fs');

env.remoteHost = process.env.HF_REMOTE_HOST || 'https://huggingface.co/';
const MODEL_NAME = process.env.TRANSFORMERS_JS_MODEL || 'Xenova/multilingual-e5-small';
const STORAGE_FILE = (process.env.LIGHTRAG_STORAGE || '/tmp/blackboardlm_rag.json');

let _rag = null;
let _pipe = null;

async function _llmFunc(prompt, opts = {}) {
    const _apiKey = process.env.DEEPSEEK_API_KEY || '';
    const _baseUrl = process.env.DEEPSEEK_BASE_URL || 'https://api.deepseek.com';
    const _model = process.env.LLM_MODEL || 'deepseek-v4-flash';
    const _messages = [];
    if (opts.system_prompt) _messages.push({ role: 'system', content: opts.system_prompt });
    if (opts.history) _messages.push(...opts.history);
    _messages.push({ role: 'user', content: prompt });
    const _resp = await fetch(`${_baseUrl}/v1/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${_apiKey}` },
        body: JSON.stringify({
            model: _model,
            messages: _messages,
            temperature: 0.7,
            max_tokens: parseInt(process.env.LLM_MAX_TOKENS || '16384'),
            stream: !!opts.stream,
            extra_body: {
                thinking: { type: process.env.LLM_THINKING || 'disabled' },
                reasoning_effort: process.env.LLM_REASONING_EFFORT || 'max',
            },
        }),
    });
    if (!_resp.ok) throw new Error(`LLM API error: ${_resp.status}`);
    if (opts.stream) {
        let _text = '';
        const _body = _resp.body;
        const _reader = _body.getReader();
        const _decoder = new TextDecoder();
        while (true) {
            const { done, value } = await _reader.read();
            if (done) break;
            const _chunk = _decoder.decode(value, { stream: true });
            const _lines = _chunk.split('\n').filter(_l => _l.startsWith('data: '));
            for (const _line of _lines) {
                const _data = _line.slice(6);
                if (_data === '[DONE]') continue;
                try {
                    const _json = JSON.parse(_data);
                    const _content = _json.choices?.[0]?.delta?.content || '';
                    _text += _content;
                } catch (_e) {}
            }
        }
        return _text;
    }
    const _json = await _resp.json();
    return _json.choices?.[0]?.message?.content || '';
}

async function _init() {
    const _start = Date.now();
    _pipe = await pipeline('feature-extraction', MODEL_NAME, {
        dtype: 'fp32',
        progress_callback: (_info) => {
            if (_info.status === 'progress' && _info.total) {
                process.stderr.write(JSON.stringify({ status: 'progress', loaded: _info.loaded, total: _info.total, file: _info.file }) + '\n');
            }
        },
    });
    const _embedder = new Embedder(_pipe);
    if (fs.existsSync(STORAGE_FILE)) {
        try {
            const _json = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'));
            _rag = LightRAG.fromJSON(_json, { embedder: _embedder, llmFunc: _llmFunc, tokenizer: _pipe.tokenizer });
        } catch (_e) {
            _rag = new LightRAG({ embedder: _embedder, llmFunc: _llmFunc, tokenizer: _pipe.tokenizer });
        }
    } else {
        _rag = new LightRAG({ embedder: _embedder, llmFunc: _llmFunc, tokenizer: _pipe.tokenizer });
    }
    const _elapsed = Date.now() - _start;
    process.stderr.write(JSON.stringify({ status: 'ready', model: MODEL_NAME, init_ms: _elapsed, loaded: _rag._vdb.size > 0 }) + '\n');
}

function _save() {
    fs.writeFileSync(STORAGE_FILE, JSON.stringify(_rag.toJSON()), 'utf-8');
}

function _clearStorage() {
    if (fs.existsSync(STORAGE_FILE)) fs.unlinkSync(STORAGE_FILE);
}

async function _handle(req) {
    console.error(`[Server] Request: action=${req.action}`);
    switch (req.action) {
        case 'insert':
            console.error(`[Server] Inserting text (${(req.text || '').length} chars)`);
            await _rag.insert(req.text);
            _save();
            console.error(`[Server] Insert done, saved to ${STORAGE_FILE}`);
            return { ok: true, progress: _rag.getProgress() };
        case 'query': {
            console.error(`[Server] Query: mode=${req.mode || 'hybrid'}, history_len=${(req.history || []).length}`);
            const _text = await _rag.query(req.question, {
                mode: req.mode || 'hybrid',
                systemPrompt: req.systemPrompt || '',
                history: req.history || [],
            });
            return { ok: true, text: _text };
        }
        case 'graph':
            return { ok: true, ..._rag.getGraphData() };
        case 'progress':
            return { ok: true, ..._rag.getProgress() };
        case 'reset':
            const { LightRAG: _LR, Embedder: _E } = require('./src/index');
            _rag = new _LR({ embedder: new _E(_pipe), llmFunc: _llmFunc, tokenizer: _pipe.tokenizer });
            _clearStorage();
            return { ok: true };
        case 'save':
            _save();
            return { ok: true };
        case 'load':
            if (fs.existsSync(STORAGE_FILE)) {
                const _json = JSON.parse(fs.readFileSync(STORAGE_FILE, 'utf-8'));
                const { LightRAG: _LR2, Embedder: _E2 } = require('./src/index');
                _rag = LightRAG.fromJSON(_json, { embedder: new _E2(_pipe), llmFunc: _llmFunc, tokenizer: _pipe.tokenizer });
                return { ok: true, loaded: _rag._vdb.size > 0 };
            }
            return { ok: true, loaded: false };
        default:
            return { error: `Unknown action: ${req.action}` };
    }
}

async function main() {
    await _init();
    let _buf = '';
    process.stdin.setEncoding('utf-8');
    for await (const _chunk of process.stdin) {
        _buf += _chunk;
        const _parts = _buf.split('\n');
        _buf = _parts.pop();
        for (const _line of _parts) {
            if (!_line.trim()) continue;
            try {
                const _req = JSON.parse(_line);
                const _resp = await _handle(_req);
                if (_resp !== null) process.stdout.write(JSON.stringify(_resp) + '\n');
            } catch (_e) {
                process.stdout.write(JSON.stringify({ error: _e.message }) + '\n');
            }
        }
    }
}

main().catch(_e => {
    process.stderr.write(JSON.stringify({ error: _e.message }) + '\n');
    process.exit(1);
});

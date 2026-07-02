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
module.exports = { TokenChunker };

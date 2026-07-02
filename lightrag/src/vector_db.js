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
            score: this._cosine(vector, _v),
            id: this._meta[_i].id,
            text: this._meta[_i].text,
        }));
        _scores.sort((_a, _b) => _b.score - _a.score);
        return _scores.slice(0, topK);
    }
    _cosine(a, b) {
        let _dot = 0, _na = 0, _nb = 0;
        for (let _i = 0; _i < a.length; _i++) { _dot += a[_i] * b[_i]; _na += a[_i] * a[_i]; _nb += b[_i] * b[_i]; }
        _na = Math.sqrt(_na); _nb = Math.sqrt(_nb);
        return (_na && _nb) ? _dot / (_na * _nb) : 0;
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
module.exports = { VectorDB };

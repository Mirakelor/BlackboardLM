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
module.exports = { Embedder };

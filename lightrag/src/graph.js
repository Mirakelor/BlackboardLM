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
    getNeighbors(id, maxDegree = 10) {
        const _adjNode = this._adj.get(id);
        if (!_adjNode) return [];
        return Array.from(_adjNode.entries())
            .sort((_a, _b) => _b[1].weight - _a[1].weight)
            .slice(0, maxDegree)
            .map(([_nodeId, _edge]) => ({ nodeId: _nodeId, ..._edge }));
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
    getNode(id) { return this._nodes.get(id) || null; }
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
module.exports = { KnowledgeGraph };

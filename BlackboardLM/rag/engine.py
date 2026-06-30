from BlackboardLM.llm.client import get_response
from sentence_transformers import SentenceTransformer
import asyncio
import concurrent.futures
import queue
import tempfile
import threading
import numpy as np
from pathlib import Path
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from typing import AsyncGenerator
import BlackboardLM.settings as _s

_WORKING_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_rag_storage")
_Q_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2)

async def _llm_func(prompt: str, system_prompt: str = None,
                   history_messages: list = None, **kwargs):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    if history_messages:
        messages = history_messages + messages
    if kwargs.get("stream"):
        return get_response(messages)
    result = ""
    async for _chunk in get_response(
        messages, model=kwargs.get("model", _s.LLM_MODEL)
    ):
        result += _chunk
    return result

_embed_model = None
_embed_lock = threading.Lock()

def _load_embed_model():
    global _embed_model
    if _embed_model is None:
        with _embed_lock:
            if _embed_model is None:
                _embed_model = SentenceTransformer("intfloat/multilingual-e5-small")
    return _embed_model

async def _embed_func(texts: list[str], context: str) -> np.ndarray:
    loop = asyncio.get_running_loop()
    model = await loop.run_in_executor(None, _load_embed_model)
    prefix = "query: " if context == "query" else "passage: "
    passages = [f"{prefix}{_text}" for _text in texts]
    return await loop.run_in_executor(None, model.encode, passages)

_embedding_func = EmbeddingFunc(
    embedding_dim=384,
    max_token_size=512,
    func=_embed_func,
    supports_asymmetric=True,
)

class RAGEngine:
    def __init__(self, working_dir: str = None):
        self._working_dir = working_dir or _WORKING_DIR
        self._loop = None
        self._thread = None
        self.rag = None
        self._storages_ready = False
        self._ready = threading.Event()

    async def startup(self):
        if self._thread is not None:
            return
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        await asyncio.to_thread(self._ready.wait)
        await self._ensure_storages()

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._ready.set()
        self._loop.run_forever()

    def _submit(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return asyncio.wrap_future(future)

    async def _ensure_storages(self):
        if not hasattr(self, "_storages_lock"):
            self._storages_lock = asyncio.Lock()
        async with self._storages_lock:
            if not self._storages_ready:
                await self._submit(self._init_and_load())
                self._storages_ready = True

    async def _init_and_load(self):
        self.rag = LightRAG(
            llm_model_func=_llm_func,
            embedding_func=_embedding_func,
            working_dir=str(self._working_dir),
            entity_extraction_use_json=True,
            chunk_token_size=3000,
            chunk_overlap_token_size=150,
            summary_max_tokens=600,
            llm_model_max_async=16,
            llm_model_kwargs={"model": _s.LLM_MODEL},
        )
        await self.rag.initialize_storages()

    async def insert(self, text: str):
        await self._ensure_storages()
        await self._submit(self.rag.ainsert(text))

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        conversation_history: list[dict] = None,
    ) -> AsyncGenerator[str, None]:
        await self._ensure_storages()
        _q: queue.Queue = queue.Queue()
        loop = asyncio.get_running_loop()

        async def _query_in_rag():
            try:
                _param = QueryParam(
                    mode=mode,
                    stream=True,
                    enable_rerank=False,
                    conversation_history=conversation_history or [],
                )
                result = await self.rag.aquery(question, param=_param)
                if isinstance(result, str):
                    _q.put(result)
                else:
                    async for _chunk in result:
                        _q.put(_chunk)
            except Exception as _exc:
                _q.put(_exc)
            finally:
                _q.put(None)

        self._submit(_query_in_rag())
        while True:
            _chunk = await loop.run_in_executor(_Q_EXECUTOR, _q.get)
            if _chunk is None:
                return
            if isinstance(_chunk, Exception):
                raise _chunk
            yield _chunk

    async def get_graph_data(self):
        if not self._storages_ready:
            return {"nodes": [], "edges": []}

        async def _fetch():
            nodes = await self.rag.chunk_entity_relation_graph.get_all_nodes()
            edges = await self.rag.chunk_entity_relation_graph.get_all_edges()
            return nodes, edges

        nodes, edges = await self._submit(_fetch())
        degree: dict[str, int] = {}
        for _e in edges:
            _s = _e.get("source", "")
            _t = _e.get("target", "")
            degree[_s] = degree.get(_s, 0) + 1
            degree[_t] = degree.get(_t, 0) + 1
        kept_ids: set = set()
        sorted_nodes = sorted(nodes, key=lambda _n: degree.get(_n.get("id", ""), 0), reverse=True)
        for _n in sorted_nodes[:200]:
            kept_ids.add(_n.get("id", ""))
        node_list = []
        for _n in nodes:
            _nid = _n.get("id", "")
            if _nid in kept_ids:
                node_list.append({
                    "id": _nid,
                    "entity_type": _n.get("entity_type", ""),
                    "degree": degree.get(_nid, 0),
                    "description": (_n.get("description", "") or "")[:120],
                })
        edge_list = []
        for _e in edges:
            _s = _e.get("source", "")
            _t = _e.get("target", "")
            if _s in kept_ids and _t in kept_ids:
                edge_list.append({
                    "source": _s,
                    "target": _t,
                    "weight": _e.get("weight", 1),
                    "keywords": (_e.get("keywords", "") or "")[:60],
                })
        return {"nodes": node_list, "edges": edge_list}

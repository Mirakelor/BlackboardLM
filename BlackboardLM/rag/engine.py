import asyncio
import concurrent.futures
import queue
import shutil
import tempfile
import threading
from pathlib import Path
from typing import AsyncGenerator
import numpy as np
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from sentence_transformers import SentenceTransformer
from BlackboardLM.llm.client import get_response
from BlackboardLM.config.prompts import (
    BLACKBOARDLM_RAG_SYSTEM_PROMPT,
    BLACKBOARDLM_NAIVE_SYSTEM_PROMPT,
)
import BlackboardLM.config.settings as _s

_WORKING_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_rag_storage")
_Q_EXECUTOR = concurrent.futures.ThreadPoolExecutor(max_workers=2)

async def _llm_func(
    prompt: str,
    system_prompt: str = None,
    history_messages: list = None,
    **kwargs,
):
    _messages = []
    if system_prompt:
        _messages.append({"role": "system", "content": system_prompt})
    _messages.append({"role": "user", "content": prompt})
    if history_messages:
        _messages = history_messages + _messages
    if kwargs.get("stream"):
        return get_response(_messages)
    _result = ""
    async for _chunk in get_response(
        _messages, model=kwargs.get("model"),
    ):
        _result += _chunk
    return _result

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
    _loop = asyncio.get_running_loop()
    _model = await _loop.run_in_executor(None, _load_embed_model)
    _prefix = "query: " if context == "query" else "passage: "
    _passages = [f"{_prefix}{_text}" for _text in texts]
    return await _loop.run_in_executor(None, _model.encode, _passages)

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
            llm_model_kwargs={},
        )
        await self.rag.initialize_storages()

    async def insert(self, text: str):
        await self._ensure_storages()
        await self._submit(self.rag.ainsert(text))

    async def query(
        self,
        question: str,
        mode: str = None,
        conversation_history: list[dict] = None,
        user_prompt: str = "",
    ) -> AsyncGenerator[str, None]:
        await self._ensure_storages()
        _mode = mode or _s.QUERY_MODE
        _sys_prompt = (
            BLACKBOARDLM_NAIVE_SYSTEM_PROMPT if _mode == "naive"
            else BLACKBOARDLM_RAG_SYSTEM_PROMPT
        )
        _q: queue.Queue = queue.Queue()
        _main_loop = asyncio.get_running_loop()

        async def _query_in_rag():
            try:
                _param = QueryParam(
                    mode=_mode,
                    stream=True,
                    enable_rerank=False,
                    max_total_tokens=96000,
                    user_prompt=user_prompt,
                    conversation_history=conversation_history or [],
                )
                _result = await self.rag.aquery(
                    question, param=_param, system_prompt=_sys_prompt,
                )
                if isinstance(_result, str):
                    _q.put(_result)
                else:
                    async for _chunk in _result:
                        _q.put(_chunk)
            except Exception as _exc:
                _q.put(_exc)
            finally:
                _q.put(None)

        self._submit(_query_in_rag())
        while True:
            _chunk = await _main_loop.run_in_executor(_Q_EXECUTOR, _q.get)
            if _chunk is None:
                return
            if isinstance(_chunk, Exception):
                raise _chunk
            yield _chunk

    async def get_graph_data(self):
        if not self._storages_ready:
            return {"nodes": [], "edges": []}

        async def _fetch():
            _nodes = await self.rag.chunk_entity_relation_graph.get_all_nodes()
            _edges = await self.rag.chunk_entity_relation_graph.get_all_edges()
            return _nodes, _edges

        _nodes, _edges = await self._submit(_fetch())
        _degree: dict[str, int] = {}
        for _e in _edges:
            _s = _e.get("source", "")
            _t = _e.get("target", "")
            _degree[_s] = _degree.get(_s, 0) + 1
            _degree[_t] = _degree.get(_t, 0) + 1
        _kept_ids: set = set()
        _sorted_nodes = sorted(_nodes, key=lambda _n: _degree.get(_n.get("id", ""), 0), reverse=True)
        for _n in _sorted_nodes[:200]:
            _kept_ids.add(_n.get("id", ""))
        _node_list = []
        for _n in _nodes:
            _nid = _n.get("id", "")
            if _nid in _kept_ids:
                _node_list.append({
                    "id": _nid,
                    "entity_type": _n.get("entity_type", ""),
                    "degree": _degree.get(_nid, 0),
                    "description": (_n.get("description", "") or "")[:120],
                })
        _edge_list = []
        for _e in _edges:
            _s = _e.get("source", "")
            _t = _e.get("target", "")
            if _s in _kept_ids and _t in _kept_ids:
                _edge_list.append({
                    "source": _s,
                    "target": _t,
                    "weight": _e.get("weight", 1),
                    "keywords": (_e.get("keywords", "") or "")[:60],
                })
        return {"nodes": _node_list, "edges": _edge_list}

    async def reset(self):
        await self._ensure_storages()
        _loop = asyncio.get_running_loop()
        if self._working_dir.exists():
            await _loop.run_in_executor(None, shutil.rmtree, str(self._working_dir))
        self._working_dir.mkdir(parents=True, exist_ok=True)
        self._storages_ready = False
        self.rag = None
        await self._ensure_storages()

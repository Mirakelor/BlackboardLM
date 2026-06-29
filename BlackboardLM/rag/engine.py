from BlackboardLM.llm.client import get_response
from sentence_transformers import SentenceTransformer
import asyncio
import tempfile
import numpy as np
from pathlib import Path
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from typing import AsyncGenerator

_WORKING_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_rag_storage")

async def llm_func(prompt: str, system_prompt: str = None,
                   history_messages: list = None, **kwargs):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    if history_messages:
        messages = history_messages + messages
    if kwargs.get("stream"):
        return get_response(messages, model=kwargs.get("model", "deepseek-v4-pro"))
    result = ""
    async for chunk in get_response(messages, model=kwargs.get("model", "deepseek-v4-pro")):
        result += chunk
    return result

_embed_model = None
_embed_lock = asyncio.Lock()

async def embed_func(texts: list[str], context: str) -> np.ndarray:
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer("intfloat/multilingual-e5-small")
    prefix = "query: " if context == "query" else "passage: "
    passages = [f"{prefix}{text}" for text in texts]
    loop = asyncio.get_running_loop()
    async with _embed_lock:
        embeddings = await loop.run_in_executor(None, _embed_model.encode, passages)
    return embeddings

_embedding_func = EmbeddingFunc(
    embedding_dim=384,
    max_token_size=512,
    func=embed_func,
    supports_asymmetric=True,
)

class RAGEngine:
    def __init__(self, working_dir: str = None):
        self.rag = LightRAG(
            llm_model_func=llm_func,
            embedding_func=_embedding_func,
            working_dir=str(working_dir or _WORKING_DIR),
            entity_extraction_use_json=True,
            chunk_token_size=3000,
            chunk_overlap_token_size=150,
            summary_max_tokens=600,
            llm_model_max_async=256,
            llm_model_kwargs={"model": "deepseek-v4-flash"},
        )
        self._storages_ready = False

    async def startup(self):
        await self._ensure_storages()
        self._warmup_task = asyncio.create_task(embed_func(["warmup"], "document"))

    async def _ensure_storages(self):
        if not self._storages_ready:
            await self.rag.initialize_storages()
            self._storages_ready = True

    async def insert(self, text: str):
        await self._ensure_storages()
        await self.rag.ainsert(text)

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        conversation_history: list[dict] = None,
    ) -> AsyncGenerator[str, None]:
        await self._ensure_storages()
        param = QueryParam(
            mode=mode,
            stream=True,
            enable_rerank=False,
            conversation_history=conversation_history or [],
        )
        result = await self.rag.aquery(question, param=param)
        async for chunk in result:
            yield chunk

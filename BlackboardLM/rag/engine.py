import asyncio
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import AsyncGenerator
from BlackboardLM.config.settings import PROJECT_ROOT
from BlackboardLM.config.prompts import (
    BLACKBOARDLM_RAG_SYSTEM_PROMPT,
    BLACKBOARDLM_NAIVE_SYSTEM_PROMPT,
)
import BlackboardLM.config.settings as _s

_log = logging.getLogger("BlackboardLM.RAG")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")

_WORKING_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_rag_storage")
_SERVER_PATH = PROJECT_ROOT.joinpath("lightrag", "server.js")
_WORKING_DIR.mkdir(parents=True, exist_ok=True)

_proc = None
_lock = asyncio.Lock()
_ready = asyncio.Event()

async def _ensure_server():
    global _proc
    if _proc is not None and _proc.returncode is None:
        await _ready.wait()
        return _proc
    async with _lock:
        if _proc is not None and _proc.returncode is None:
            await _ready.wait()
            return _proc
        _ready.clear()
        _env = os.environ.copy()
        _hf = os.environ.get("HF_ENDPOINT", "https://huggingface.co/")
        if not _hf.endswith("/"):
            _hf += "/"
        _env["HF_REMOTE_HOST"] = _hf
        _env["LIGHTRAG_STORAGE"] = str(_WORKING_DIR.joinpath("rag_data.json"))
        _log.info("Starting lightrag Node.js server at %s", _SERVER_PATH)
        _proc = await asyncio.create_subprocess_exec(
            "node", str(_SERVER_PATH),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=_env,
        )
        asyncio.create_task(_monitor_stderr(_proc))
    await _ready.wait()
    return _proc

async def _monitor_stderr(proc):
    global _ready
    while proc.returncode is None:
        _line = await proc.stderr.readline()
        if not _line:
            break
        try:
            _msg = json.loads(_line.decode())
        except json.JSONDecodeError:
            _log.info("[Node] %s", _line.decode().strip())
            continue
        if _msg.get("status") == "ready":
            _log.info("RAG server ready, model=%s, init_ms=%s",
                       _msg.get("model"), _msg.get("init_ms"))
            _ready.set()
        elif _msg.get("status") == "progress":
            _loaded = _msg.get("loaded", 0)
            _total = _msg.get("total", 1)
            _pct = _loaded / _total if _total > 0 else 0.0
            _log.info("Downloading model: %.0f%%", _pct * 100)
        else:
            _log.info("[Node] %s", _line.decode().strip())
    if not _ready.is_set():
        _ready.set()

async def _send(req: dict) -> dict:
    _proc = await _ensure_server()
    _line = json.dumps(req, ensure_ascii=False) + "\n"
    _log.info("Sending request: action=%s", req.get("action"))
    async with _lock:
        _proc.stdin.write(_line.encode())
        await _proc.stdin.drain()
        _resp_line = await _proc.stdout.readline()
    _resp = json.loads(_resp_line.decode())
    if "error" in _resp:
        raise RuntimeError(_resp["error"])
    return _resp

class RAGEngine:
    def __init__(self, working_dir: str = None):
        self._working_dir = working_dir or _WORKING_DIR

    async def startup(self):
        asyncio.create_task(_ensure_server())

    async def wait_ready(self):
        await _ensure_server()

    async def insert(self, text: str):
        await _ensure_server()
        await _send({"action": "insert", "text": text})

    async def query(
        self,
        question: str,
        mode: str = None,
        conversation_history: list[dict] = None,
        user_prompt: str = "",
        response_type: str = "Multiple Paragraphs",
    ) -> AsyncGenerator[str, None]:
        await _ensure_server()
        _mode = mode or _s.QUERY_MODE
        _sys_prompt = (
            BLACKBOARDLM_NAIVE_SYSTEM_PROMPT if _mode == "naive"
            else BLACKBOARDLM_RAG_SYSTEM_PROMPT
        )
        if user_prompt:
            _sys_prompt += "\n\n" + user_prompt
        _sys_prompt = _sys_prompt.format(response_type=response_type)
        _text = await _send({
            "action": "query",
            "question": question,
            "mode": _mode,
            "systemPrompt": _sys_prompt,
            "history": conversation_history or [],
        })
        _result = _text.get("text", "")
        if _result:
            yield _result

    async def get_graph_data(self):
        try:
            _resp = await _send({"action": "graph"})
            return _resp
        except Exception:
            return {"nodes": [], "edges": []}

    async def reset(self):
        try:
            await _send({"action": "reset"})
        except Exception:
            _loop = asyncio.get_running_loop()
            if self._working_dir.exists():
                await _loop.run_in_executor(None, shutil.rmtree, str(self._working_dir))
            self._working_dir.mkdir(parents=True, exist_ok=True)

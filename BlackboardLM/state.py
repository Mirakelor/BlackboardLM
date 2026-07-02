import asyncio
import hashlib
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

import reflex as rx

from BlackboardLM.pipeline.parsers.markitdown_parser import MarkitdownParser
from BlackboardLM.rag.engine import get_llm_config_json
import BlackboardLM.config.settings as _s
from BlackboardLM.config.settings import _write_env
from BlackboardLM.config.prompts import PRESET_MODES, BLACKBOARDLM_RAG_SYSTEM_PROMPT, BLACKBOARDLM_NAIVE_SYSTEM_PROMPT
import BlackboardLM.config.theme as _theme

_parser = MarkitdownParser()
_PREVIEW_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_previews")
_PREVIEW_DIR.mkdir(parents=True, exist_ok=True)

class AppState(rx.State):
    uploaded_files: list[str] = []
    chat_messages: list[dict] = []
    current_input: str = ""
    is_processing: bool = False
    theme_name: str = _s.THEME
    expanded_doc: str = ""
    star_chart_visible: bool = True
    parsing_files: list[str] = []
    graph_data: dict = {}
    preview_content: str = ""
    preview_ready: bool = False
    settings_visible: bool = False
    settings_api_key: str = _s.DEEPSEEK_API_KEY or ""
    settings_model: str = _s.LLM_MODEL
    settings_base_url: str = _s.DEEPSEEK_BASE_URL
    settings_thinking: str = _s.LLM_THINKING
    settings_reasoning: str = _s.LLM_REASONING_EFFORT
    settings_max_tokens: int = _s.LLM_MAX_TOKENS
    settings_query_mode: str = _s.QUERY_MODE
    settings_response_type: str = _s.RESPONSE_TYPE
    selected_preset: str = ""
    presets_expanded: bool = False
    settings_saved: bool = False
    clear_done: bool = False
    auth_token: str = rx.Cookie(name="bl_auth")
    is_authenticated: bool = not _s.ACCESS_PASSWORD
    login_password: str = ""
    login_error: str = ""
    _on_load_done: bool = False
    _pending_files: list = []
    _uploaded_hashes: set = set()
    rag_doc_counter: int = 0
    rag_doc_text: str = ""
    rag_query_counter: int = 0
    rag_query_params: str = "{}"
    rag_reset_counter: int = 0
    rag_config_updated: bool = False
    rag_status: str = ""
    rag_model_progress: int = 0
    rag_insert_ready: int = 0
    rag_insert_total: int = 0
    rag_worker_ready: bool = False

    @rx.var
    def rag_model_progress_pct(self) -> str:
        return f"{self.rag_model_progress}%"

    @rx.var
    def rag_insert_progress_pct(self) -> str:
        if self.rag_insert_total == 0:
            return "0%"
        return f"{int(self.rag_insert_ready * 100 / self.rag_insert_total)}%"

    @rx.var
    def graph_data_json(self) -> str:
        return json.dumps(self.graph_data, ensure_ascii=False)

    @rx.var
    def graph_node_count(self) -> int:
        return len(self.graph_data.get("nodes", []))

    @rx.var
    def theme(self) -> dict:
        _t = _theme.THEMES.get(self.theme_name, _theme.THEMES[_theme.THEME_SAKURA])
        return asdict(_t)

    @rx.var
    def rag_llm_config_json(self) -> str:
        _cfg = json.loads(get_llm_config_json())
        _cfg["_configChanged"] = self.rag_config_updated
        return json.dumps(_cfg, ensure_ascii=False)

    @rx.event
    async def on_load(self):
        if self._on_load_done:
            return
        if _s.ACCESS_PASSWORD:
            if not self._verify_token(self.auth_token):
                async with self:
                    self.is_authenticated = False
                return
            async with self:
                self.is_authenticated = True
        async with self:
            self._on_load_done = True

    @rx.event
    def set_theme(self, name: str):
        if name in _theme.THEMES:
            self.theme_name = name

    @rx.event
    def toggle_star_chart(self):
        self.star_chart_visible = not self.star_chart_visible

    @rx.event
    async def toggle_doc_preview(self, filename: str):
        if self.expanded_doc == filename:
            self.expanded_doc = ""
            self.preview_content = ""
            self.preview_ready = False
            return
        self.expanded_doc = filename
        _hash = hashlib.md5(filename.encode()).hexdigest()[:16]
        _path = _PREVIEW_DIR.joinpath(f"{_hash}.txt")
        _loop = asyncio.get_running_loop()
        if await _loop.run_in_executor(None, _path.exists):
            self.preview_content = await _loop.run_in_executor(None, _path.read_text, "utf-8")
            self.preview_ready = True

    @rx.event
    def toggle_presets(self):
        self.presets_expanded = not self.presets_expanded

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        _loop = asyncio.get_running_loop()
        _pending = []
        for _file in files:
            _suffix = Path(_file.filename).suffix if _file.filename else ""
            _content = await _file.read()
            _content_hash = hashlib.md5(_content).hexdigest()
            if _content_hash in self._uploaded_hashes:
                continue
            self._uploaded_hashes.add(_content_hash)
            with tempfile.NamedTemporaryFile(suffix=_suffix, delete=False) as _tmp:
                await _loop.run_in_executor(None, _tmp.write, _content)
                _tmp_path = _tmp.name
            self.uploaded_files.append(_file.filename)
            self.parsing_files.append(_file.filename)
            _pending.append((_tmp_path, _file.filename))
        if not _pending:
            return
        self._pending_files = _pending
        asyncio.create_task(self._process_files())

    async def _process_files(self):
        _loop = asyncio.get_running_loop()
        _full_texts = []
        for _tmp_path, _filename in self._pending_files:
            _name_hash = hashlib.md5(_filename.encode()).hexdigest()[:16]
            _path = _PREVIEW_DIR.joinpath(f"{_name_hash}.txt")
            try:
                _result = await _loop.run_in_executor(None, _parser.parse, _tmp_path)
                _full_text = _result["text"]
                await _loop.run_in_executor(None, _path.write_text, _full_text, "utf-8")
                _full_texts.append(_full_text)
            finally:
                await _loop.run_in_executor(None, Path(_tmp_path).unlink, True)
        if _full_texts:
            _combined = "\n\n".join(_full_texts)
            async with self:
                self.rag_doc_text = _combined
                self.rag_doc_counter += 1

    @rx.event
    async def send_message(self):
        if self.is_processing or not self.current_input.strip():
            return
        _question = self.current_input.strip()
        self.current_input = ""
        self.chat_messages.append({"role": "user", "content": _question})
        _history = [
            {"role": _m["role"], "content": _m["content"]}
            for _m in self.chat_messages[:-1]
        ]
        _mode = self.settings_query_mode
        _sys_prompt = (
            BLACKBOARDLM_NAIVE_SYSTEM_PROMPT if _mode == "naive"
            else BLACKBOARDLM_RAG_SYSTEM_PROMPT
        )
        _user_prompt = PRESET_MODES.get(self.selected_preset, "")
        if _user_prompt:
            _sys_prompt += "\n\n" + _user_prompt
        _sys_prompt = _sys_prompt.format(response_type=self.settings_response_type)
        _params = {
            "question": _question,
            "mode": _mode,
            "systemPrompt": _sys_prompt,
            "history": _history,
        }
        self.is_processing = True
        self.rag_query_params = json.dumps(_params, ensure_ascii=False)
        self.rag_query_counter += 1
        yield

    @rx.event
    def on_chat_chunk(self, chunk: str):
        if not self.chat_messages or self.chat_messages[-1]["role"] != "assistant":
            self.chat_messages.append({"role": "assistant", "content": chunk})
        else:
            self.chat_messages[-1]["content"] += chunk

    @rx.event
    def on_chat_done(self):
        self.is_processing = False

    @rx.event
    def on_rag_insert_done(self, graph_json: str):
        self.parsing_files = []
        try:
            self.graph_data = json.loads(graph_json)
        except Exception:
            pass

    @rx.event
    def on_rag_graph_update(self, graph_json: str):
        try:
            self.graph_data = json.loads(graph_json)
        except Exception:
            pass

    @rx.event
    def on_rag_error(self, error: str):
        self.rag_status = error

    @rx.event
    def on_rag_model_progress(self, loaded: int, total: int, file: str):
        if total > 0:
            self.rag_model_progress = int(loaded * 100 / total)
            self.rag_status = f"Downloading model: {self.rag_model_progress}%"

    @rx.event
    def on_rag_insert_progress(self, total: int, ready: int):
        self.rag_insert_ready = ready
        self.rag_insert_total = total
        self.rag_status = f"Processing document: {ready}/{total} chunks"

    @rx.event
    def on_rag_worker_ready(self):
        self.rag_worker_ready = True
        self.rag_status = ""

    @rx.event
    def set_input(self, value: str):
        self.current_input = value

    @rx.event
    def set_preset(self, _value: str):
        self.selected_preset = _value if self.selected_preset != _value else ""

    @rx.event
    def toggle_settings(self):
        self.settings_visible = not self.settings_visible
        self.settings_saved = False
        self.clear_done = False

    @rx.event
    def set_settings_api_key(self, _value: str):
        self.settings_api_key = _value

    @rx.event
    def set_settings_model(self, _value: str):
        self.settings_model = _value

    @rx.event
    def set_settings_base_url(self, _value: str):
        self.settings_base_url = _value

    @rx.event
    def set_settings_thinking(self, _value: str):
        self.settings_thinking = _value

    @rx.event
    def set_settings_reasoning(self, _value: str):
        self.settings_reasoning = _value

    @rx.event
    def set_settings_max_tokens(self, _value):
        self.settings_max_tokens = int(_value[0]) if isinstance(_value, list) else int(_value)

    @rx.event
    def set_settings_query_mode(self, _value: str):
        self.settings_query_mode = _value

    @rx.event
    def set_settings_response_type(self, _value: str):
        self.settings_response_type = _value

    @rx.event
    def save_settings(self):
        _restart_keys = [
            ("DEEPSEEK_API_KEY", self.settings_api_key),
            ("LLM_MODEL", self.settings_model),
            ("DEEPSEEK_BASE_URL", self.settings_base_url),
            ("LLM_THINKING", self.settings_thinking),
            ("LLM_REASONING_EFFORT", self.settings_reasoning),
            ("LLM_MAX_TOKENS", str(self.settings_max_tokens)),
            ("QUERY_MODE", self.settings_query_mode),
            ("RESPONSE_TYPE", self.settings_response_type),
        ]
        for _key, _val in _restart_keys:
            _write_env(_key, _val)
        self.settings_saved = True
        self.rag_config_updated = not self.rag_config_updated

    @rx.event
    def set_login_password(self, _value: str):
        self.login_password = _value
        self.login_error = ""

    @rx.event
    def handle_login_key(self, _key: str):
        if _key == "Enter":
            return AppState.login

    @rx.event
    def login(self):
        if self.login_password != _s.ACCESS_PASSWORD:
            self.login_error = "Incorrect password"
            self.login_password = ""
            return
        _token = hashlib.sha256(f"{self.login_password}:bl_salt".encode()).hexdigest()
        self.auth_token = _token
        self.is_authenticated = True
        self.login_error = ""
        self.login_password = ""
        return AppState.on_load

    @rx.event
    def logout(self):
        self.auth_token = ""
        self.is_authenticated = False

    def _verify_token(self, _token: str) -> bool:
        if not _token or not _s.ACCESS_PASSWORD:
            return False
        _expected = hashlib.sha256(f"{_s.ACCESS_PASSWORD}:bl_salt".encode()).hexdigest()
        return _token == _expected

    @rx.event(background=True)
    async def clear_all_data(self):
        _loop = asyncio.get_running_loop()
        if await _loop.run_in_executor(None, _PREVIEW_DIR.exists):
            _f_list = await _loop.run_in_executor(None, lambda d=_PREVIEW_DIR: list(d.iterdir()))
            for _f in _f_list:
                await _loop.run_in_executor(None, _f.unlink, True)
        async with self:
            self.uploaded_files = []
            self.chat_messages = []
            self.expanded_doc = ""
            self.preview_content = ""
            self.preview_ready = False
            self.graph_data = {"nodes": [], "edges": []}
            self.clear_done = True
            self._uploaded_hashes = set()
            self.rag_status = ""
            self.rag_model_progress = 0
            self.rag_insert_ready = 0
            self.rag_insert_total = 0
            self.rag_reset_counter += 1

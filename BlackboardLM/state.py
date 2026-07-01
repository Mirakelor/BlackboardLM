import asyncio
import hashlib
import json
import tempfile
from dataclasses import asdict
from pathlib import Path
import reflex as rx
from BlackboardLM.pipeline.parsers.docling_parser import DoclingParser
from BlackboardLM.rag.engine import RAGEngine
import BlackboardLM.config.settings as _s
from BlackboardLM.config.settings import _write_env
from BlackboardLM.config.prompts import PRESET_MODES
import BlackboardLM.config.theme as _theme

_rag = RAGEngine()
_parser = DoclingParser()
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
    _pending_parse: list = []
    graph_data: dict = {}
    preview_content: str = ""
    preview_ready: bool = False
    settings_visible: bool = False
    settings_api_key: str = _s.OPENAI_API_KEY or ""
    settings_model: str = _s.LLM_MODEL
    settings_base_url: str = _s.OPENAI_BASE_URL
    settings_thinking: str = _s.LLM_THINKING
    settings_reasoning: str = _s.LLM_REASONING_EFFORT
    settings_max_tokens: int = _s.LLM_MAX_TOKENS
    settings_query_mode: str = _s.QUERY_MODE
    settings_response_type: str = "Multiple Paragraphs"
    selected_preset: str = ""
    presets_expanded: bool = False
    settings_saved: bool = False

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

    async def on_load(self):
        await _rag.startup()
        await asyncio.sleep(1)
        data = await _rag.get_graph_data()
        async with self:
            self.graph_data = data

    def set_theme(self, name: str):
        if name in _theme.THEMES:
            self.theme_name = name

    def toggle_star_chart(self):
        self.star_chart_visible = not self.star_chart_visible

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

    def toggle_presets(self):
        self.presets_expanded = not self.presets_expanded

    async def upload_file(self, files: list[rx.UploadFile]):
        self.is_processing = True
        yield
        _loop = asyncio.get_running_loop()
        _pending = []
        for _file in files:
            _suffix = Path(_file.filename).suffix if _file.filename else ""
            with tempfile.NamedTemporaryFile(suffix=_suffix, delete=False) as _tmp:
                _content = await _file.read()
                await _loop.run_in_executor(None, _tmp.write, _content)
                _tmp_path = _tmp.name
            self.uploaded_files.append(_file.filename)
            self.parsing_files.append(_file.filename)
            _pending.append((_tmp_path, _file.filename))
        self.is_processing = False
        self._pending_parse = _pending
        yield
        yield AppState.start_parsing

    @rx.event
    def start_parsing(self):
        return AppState.parse_and_index

    @rx.event(background=True)
    async def parse_and_index(self):
        async with self:
            _pending = list(self._pending_parse)
            self._pending_parse = []
            _expanded_doc = self.expanded_doc
        _loop = asyncio.get_running_loop()
        for _tmp_path, _filename in _pending:
            _hash = hashlib.md5(_filename.encode()).hexdigest()[:16]
            _path = _PREVIEW_DIR.joinpath(f"{_hash}.txt")
            try:
                _result = await _loop.run_in_executor(None, _parser.parse, _tmp_path)
                _full_text = _result["text"]
                for _table in _result["tables"]:
                    _full_text += "\n" + _table
                await _loop.run_in_executor(None, _path.write_text, _full_text, "utf-8")
                await _rag.insert(_full_text)
            finally:
                await _loop.run_in_executor(None, Path(_tmp_path).unlink, True)
        _preview_text = ""
        if _expanded_doc:
            _exp_hash = hashlib.md5(_expanded_doc.encode()).hexdigest()[:16]
            _exp_path = _PREVIEW_DIR.joinpath(f"{_exp_hash}.txt")
            if await _loop.run_in_executor(None, _exp_path.exists):
                _preview_text = await _loop.run_in_executor(None, _exp_path.read_text, "utf-8")
        data = await _rag.get_graph_data()
        async with self:
            self.parsing_files = []
            if _preview_text:
                self.preview_content = _preview_text
                self.preview_ready = True
            self.graph_data = data

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
        self.is_processing = True
        yield
        async for _chunk in _rag.query(
            _question,
            mode=self.settings_query_mode,
            conversation_history=_history,
            user_prompt=PRESET_MODES.get(self.selected_preset, ""),
        ):
            if not self.chat_messages or self.chat_messages[-1]["role"] != "assistant":
                self.chat_messages.append({"role": "assistant", "content": _chunk})
            else:
                self.chat_messages[-1]["content"] += _chunk
            yield
        self.is_processing = False
        yield

    def set_input(self, value: str):
        self.current_input = value

    def set_preset(self, _value: str):
        self.selected_preset = _value if self.selected_preset != _value else ""

    def toggle_settings(self):
        self.settings_visible = not self.settings_visible
        self.settings_saved = False

    def set_settings_api_key(self, _value: str):
        self.settings_api_key = _value

    def set_settings_model(self, _value: str):
        self.settings_model = _value

    def set_settings_base_url(self, _value: str):
        self.settings_base_url = _value

    def set_settings_thinking(self, _value: str):
        self.settings_thinking = _value

    def set_settings_reasoning(self, _value: str):
        self.settings_reasoning = _value

    def set_settings_max_tokens(self, _value):
        self.settings_max_tokens = int(_value[0]) if isinstance(_value, list) else int(_value)

    def set_settings_query_mode(self, _value: str):
        self.settings_query_mode = _value

    def set_settings_response_type(self, _value: str):
        self.settings_response_type = _value

    def save_settings(self):
        _restart_keys = [
            ("OPENAI_API_KEY", self.settings_api_key),
            ("LLM_MODEL", self.settings_model),
            ("OPENAI_BASE_URL", self.settings_base_url),
            ("LLM_THINKING", self.settings_thinking),
            ("LLM_REASONING_EFFORT", self.settings_reasoning),
            ("LLM_MAX_TOKENS", str(self.settings_max_tokens)),
            ("QUERY_MODE", self.settings_query_mode),
        ]
        for _key, _val in _restart_keys:
            _write_env(_key, _val)
        self.settings_saved = True

from dataclasses import asdict
import asyncio
import hashlib
import json
import tempfile
from pathlib import Path
import reflex as rx
from BlackboardLM.rag.engine import RAGEngine
from BlackboardLM.pipeline.parsers.docling_parser import DoclingParser
import BlackboardLM.theme as _theme
import BlackboardLM.settings as _s

_rag = RAGEngine()
_parser = DoclingParser()
_bg_tasks: set = set()
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
    graph_data: dict = {}
    preview_content: str = ""
    preview_ready: bool = False

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

    def set_input(self, value: str):
        self.current_input = value

    def set_theme(self, name: str):
        if name in _theme.THEMES:
            self.theme_name = name

    def toggle_star_chart(self):
        self.star_chart_visible = not self.star_chart_visible

    def toggle_doc_preview(self, filename: str):
        if self.expanded_doc == filename:
            self.expanded_doc = ""
            self.preview_content = ""
            self.preview_ready = False
        else:
            self.expanded_doc = filename
            _hash = hashlib.md5(filename.encode()).hexdigest()[:16]
            _path = _PREVIEW_DIR.joinpath(f"{_hash}.txt")
            if _path.exists():
                _text = _path.read_text(encoding="utf-8")
                self.preview_content = _text
                self.preview_ready = True
            else:
                self.preview_content = ""
                self.preview_ready = False

    async def on_load(self):
        await _rag.startup()
        await asyncio.sleep(1)
        data = await _rag.get_graph_data()
        async with self:
            self.graph_data = data

    async def upload_file(self, files: list[rx.UploadFile]):
        self.is_processing = True
        yield
        pending = []
        for _file in files:
            suffix = Path(_file.filename).suffix if _file.filename else ""
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as _tmp:
                content = await _file.read()
                _tmp.write(content)
                _tmp_path = _tmp.name
            self.uploaded_files.append(_file.filename)
            pending.append((_tmp_path, _file.filename))
        self.is_processing = False
        yield
        _bg_tasks.add(asyncio.create_task(self._parse_and_index(pending)))

    async def _parse_and_index(self, pending: list[tuple[str, str]]):
        _loop = asyncio.get_running_loop()
        for _tmp_path, _filename in pending:
            try:
                result = await _loop.run_in_executor(None, _parser.parse, _tmp_path)
                full_text = result["text"]
                for _table in result["tables"]:
                    full_text += "\n" + _table
                _hash = hashlib.md5(_filename.encode()).hexdigest()[:16]
                _path = _PREVIEW_DIR.joinpath(f"{_hash}.txt")
                _path.write_text(full_text, encoding="utf-8")
                await _rag.insert(full_text)
            finally:
                Path(_tmp_path).unlink(missing_ok=True)
        data = await _rag.get_graph_data()
        async with self:
            self.graph_data = data

    async def send_message(self):
        if self.is_processing or not self.current_input.strip():
            return
        question = self.current_input.strip()
        self.current_input = ""
        self.chat_messages.append({"role": "user", "content": question})
        self.is_processing = True
        yield
        async for _chunk in _rag.query(question):
            if not self.chat_messages or self.chat_messages[-1]["role"] != "assistant":
                self.chat_messages.append({"role": "assistant", "content": _chunk})
            else:
                self.chat_messages[-1]["content"] += _chunk
            yield
        self.is_processing = False
        yield

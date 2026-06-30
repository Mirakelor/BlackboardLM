from dataclasses import asdict
import asyncio
import tempfile
from pathlib import Path
import reflex as rx
from BlackboardLM.rag.engine import RAGEngine
from BlackboardLM.pipeline.parsers.docling_parser import DoclingParser
import BlackboardLM.theme as _theme
import BlackboardLM.settings as _s

_rag = RAGEngine()
_parser = DoclingParser()

class AppState(rx.State):
    uploaded_files: list[str] = []
    chat_messages: list[dict] = []
    current_input: str = ""
    is_processing: bool = False
    theme_name: str = _s.THEME
    expanded_doc: str = ""
    star_chart_visible: bool = True

    @rx.var
    def theme(self) -> dict:
        t = _theme.THEMES.get(self.theme_name, _theme.THEMES["sakura"])
        return asdict(t)

    def set_input(self, value: str):
        self.current_input = value

    def set_theme(self, name: str):
        if name in _theme.THEMES:
            self.theme_name = name

    def toggle_star_chart(self):
        self.star_chart_visible = not self.star_chart_visible

    def toggle_doc_preview(self, filename: str):
        self.expanded_doc = "" if self.expanded_doc == filename else filename

    async def on_load(self):
        await _rag.startup()

    async def upload_file(self, files: list[rx.UploadFile]):
        self.is_processing = True
        yield
        loop = asyncio.get_running_loop()
        for file in files:
            suffix = Path(file.filename).suffix if file.filename else ""
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            try:
                result = await loop.run_in_executor(None, _parser.parse, tmp_path)
                full_text = result["text"]
                for table in result["tables"]:
                    full_text += "\n" + table
                await _rag.insert(full_text)
                self.uploaded_files.append(file.filename)
            finally:
                Path(tmp_path).unlink(missing_ok=True)
        self.is_processing = False
        yield

    async def send_message(self):
        if self.is_processing or not self.current_input.strip():
            return
        question = self.current_input.strip()
        self.current_input = ""
        self.chat_messages.append({"role": "user", "content": question})
        self.is_processing = True
        yield
        async for chunk in _rag.query(question):
            if not self.chat_messages or self.chat_messages[-1]["role"] != "assistant":
                self.chat_messages.append({"role": "assistant", "content": chunk})
            else:
                self.chat_messages[-1]["content"] += chunk
            yield
        self.is_processing = False
        yield

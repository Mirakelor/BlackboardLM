import tempfile
from pathlib import Path
import reflex as rx
from BlackboardLM.rag.engine import RAGEngine
from BlackboardLM.pipeline.parsers.docling_parser import DoclingParser

_rag = RAGEngine()
_parser = DoclingParser()

class AppState(rx.State):
    uploaded_files: list[str] = []
    chat_messages: list[dict] = []
    current_input: str = ""
    is_processing: bool = False

    def set_input(self, value: str):
        self.current_input = value

    async def on_load(self):
        await _rag.startup()

    async def upload_file(self, files: list[rx.UploadFile]):
        self.is_processing = True
        yield
        for file in files:
            suffix = Path(file.filename).suffix if file.filename else ""
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            try:
                result = _parser.parse(tmp_path)
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
        if not self.current_input.strip():
            return
        question = self.current_input.strip()
        self.current_input = ""
        self.chat_messages.append({"role": "user", "content": question})
        self.chat_messages.append({"role": "assistant", "content": ""})
        self.is_processing = True
        yield
        async for chunk in _rag.query(question):
            self.chat_messages[-1]["content"] += chunk
            yield
        self.is_processing = False
        yield

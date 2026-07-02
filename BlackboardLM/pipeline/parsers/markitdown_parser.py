from pathlib import Path
from .base import BaseParser

class MarkitdownParser(BaseParser):
    def __init__(self):
        self._md = None

    def _get_md(self):
        if self._md is None:
            from markitdown import MarkItDown
            self._md = MarkItDown()
        return self._md

    def parse(self, file_path: str) -> dict:
        _ext = Path(file_path).suffix[1:].lower()
        if _ext not in self.supported_formats():
            raise ValueError(f"Unsupported file format: .{_ext}")
        _md = self._get_md()
        _result = _md.convert_local(file_path)
        return {"text": _result.text_content}

    def supported_formats(self) -> list[str]:
        return ['pdf', 'docx', 'pptx', 'html', 'md', 'txt', 'xlsx', 'epub',
                'jpg', 'jpeg', 'png', 'tiff', 'csv', 'json', 'xml']

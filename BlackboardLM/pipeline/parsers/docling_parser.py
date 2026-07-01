import hashlib
import tempfile
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions

from .base import BaseParser

_IMAGES_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_parsed_images")

class DoclingParser(BaseParser):
    def __init__(self):
        _pipeline_options = PdfPipelineOptions()
        _pipeline_options.generate_picture_images = True
        _pipeline_options.do_ocr = False
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=_pipeline_options),
            }
        )

    def parse(self, file_path: str) -> dict:
        _ext = Path(file_path).suffix[1:].lower()
        if _ext not in self.supported_formats():
            raise ValueError(f"Unsupported file format: .{_ext}, supported: {self.supported_formats()}")
        _IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        _result = self.converter.convert(file_path)
        _doc = _result.document
        _text = _doc.export_to_markdown()
        _tables = [table.export_to_markdown(_doc) for table in _doc.tables]
        _pictures = []
        _doc_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        for _i, _pic_item in enumerate(_doc.pictures):
            _image = _pic_item.get_image(_doc)
            if _image is None:
                continue
            _image_path = _IMAGES_DIR.joinpath(f"{_doc_id}_{_i}.png")
            _caption = _pic_item.caption_text(_doc)
            _image.save(str(_image_path))
            _pictures.append({"path": str(_image_path), "caption": _caption})
        return {
            "text": _text,
            "tables": _tables,
            "pictures": _pictures,
            "metadata": {
                "source": file_path,
                "pages": len(_result.pages) if _result.pages else 0,
                "source_type": _ext or 'unknown',
            }
        }

    def supported_formats(self) -> list[str]:
        return ['pdf', 'docx', 'pptx', 'html', 'md', 'txt', 'xlsx', 'epub', 'jpg', 'jpeg', 'png', 'tiff']

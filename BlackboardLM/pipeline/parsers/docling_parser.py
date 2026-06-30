from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from .base import BaseParser
import hashlib
import tempfile
from pathlib import Path

_IMAGES_DIR = Path(tempfile.gettempdir()).joinpath("blackboardlm_parsed_images")

class DoclingParser(BaseParser):
    def __init__(self):
        pipeline_options = PdfPipelineOptions()
        pipeline_options.generate_picture_images = True
        pipeline_options.do_ocr = False
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )

    def supported_formats(self) -> list[str]:
        return ['pdf', 'docx', 'pptx', 'html', 'md', 'txt', 'xlsx', 'epub', 'jpg', 'jpeg', 'png', 'tiff']

    def parse(self, file_path: str) -> dict:
        _ext = Path(file_path).suffix[1:].lower()
        if _ext not in self.supported_formats():
            raise ValueError(f"Unsupported file format: .{_ext}, supported: {self.supported_formats()}")
        _IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        result = self.converter.convert(file_path)
        _doc = result.document
        text = _doc.export_to_markdown()
        _tables = [table.export_to_markdown(_doc) for table in _doc.tables]
        pictures = []
        doc_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        for _i, _pic_item in enumerate(_doc.pictures):
            image = _pic_item.get_image(_doc)
            if image is None:
                continue
            image_path = _IMAGES_DIR.joinpath(f"{doc_id}_{_i}.png")
            caption = _pic_item.caption_text(_doc)
            image.save(str(image_path))
            pictures.append({"path": str(image_path), "caption": caption})
        return {
            "text": text,
            "tables": _tables,
            "pictures": pictures,
            "metadata": {
                "source": file_path,
                "pages": len(result.pages) if result.pages else 0,
                "source_type": _ext or 'unknown',
            }
        }

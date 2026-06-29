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
        ext = Path(file_path).suffix[1:].lower()
        if ext not in self.supported_formats():
            raise ValueError(f"Unsupported file format: .{ext}, supported: {self.supported_formats()}")
        _IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        result = self.converter.convert(file_path)
        doc = result.document
        text = doc.export_to_markdown()
        tables = [table.export_to_markdown(doc) for table in doc.tables]
        pictures = []
        doc_id = hashlib.md5(file_path.encode()).hexdigest()[:8]
        for i, pic_item in enumerate(doc.pictures):
            image = pic_item.get_image(doc)
            if image is None:
                continue
            image_path = _IMAGES_DIR.joinpath(f"{doc_id}_{i}.png")
            caption = pic_item.caption_text(doc)
            image.save(str(image_path))
            pictures.append({"path": str(image_path), "caption": caption})
        return {
            "text": text,
            "tables": tables,
            "pictures": pictures,
            "metadata": {
                "source": file_path,
                "pages": len(result.pages) if result.pages else 0,
                "source_type": ext or 'unknown',
            }
        }

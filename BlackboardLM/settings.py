import os
import socket
import tempfile
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT.joinpath(".env"))

os.environ.setdefault("REFLEX_UPLOADED_FILES_DIR", str(Path(tempfile.gettempdir()).joinpath("blackboardlm_uploads")))

if not os.getenv("HF_ENDPOINT"):
    try:
        socket.create_connection(("huggingface.co", 443), timeout=3).close()
    except Exception:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import os
import socket
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import BlackboardLM.theme as _theme

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT.joinpath(".env"))

os.environ.setdefault("REFLEX_UPLOADED_FILES_DIR", str(Path(tempfile.gettempdir()).joinpath("blackboardlm_uploads")))

if not os.getenv("HF_ENDPOINT"):
    try:
        socket.create_connection(("huggingface.co", 443), timeout=3).close()
    except Exception:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")
LLM_THINKING = os.environ.get("LLM_THINKING", "disabled")
LLM_REASONING_EFFORT = os.environ.get("LLM_REASONING_EFFORT", "max")
THEME = os.environ.get("THEME", _theme.THEME_SAKURA)

import os
import socket
import tempfile
from pathlib import Path
from dotenv import load_dotenv
import BlackboardLM.config.theme as _theme

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_env_file = PROJECT_ROOT.joinpath(".env")
if _env_file.exists():
    load_dotenv(_env_file)

os.environ.setdefault("REFLEX_UPLOADED_FILES_DIR", str(Path(tempfile.gettempdir()).joinpath("blackboardlm_uploads")))

if not os.getenv("HF_ENDPOINT"):
    try:
        socket.create_connection(("huggingface.co", 443), timeout=3).close()
    except Exception:
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

def _write_env(_key: str, _value: str):
    _lines = []
    if _env_file.exists():
        _lines = _env_file.read_text("utf-8").splitlines()
    for _i, _line in enumerate(_lines):
        if _line.startswith(f"{_key}=") or _line.startswith(f"#{_key}="):
            _lines[_i] = f"{_key}={_value}"
            break
    else:
        _lines.append(f"{_key}={_value}")
    _env_file.write_text("\n".join(_lines) + "\n", "utf-8")
    os.environ[_key] = _value

ACCESS_PASSWORD = os.environ.get("ACCESS_PASSWORD", "")
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-v4-flash")
LLM_THINKING = os.environ.get("LLM_THINKING", "disabled")
LLM_REASONING_EFFORT = os.environ.get("LLM_REASONING_EFFORT", "max")
LLM_MAX_TOKENS = int(os.environ.get("LLM_MAX_TOKENS", "16384"))
THEME = os.environ.get("THEME", _theme.THEME_SAKURA)
QUERY_MODE = os.environ.get("QUERY_MODE", "naive")
RESPONSE_TYPE = os.environ.get("RESPONSE_TYPE", "Multiple Paragraphs")

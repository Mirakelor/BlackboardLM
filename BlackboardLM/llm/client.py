import os
import threading
from openai import AsyncOpenAI

_lock = threading.Lock()
_client = None
_client_cfg = None

def _get_client():
    global _client, _client_cfg
    _cfg = (
        os.environ.get("OPENAI_API_KEY", ""),
        os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com"),
    )
    if _client_cfg != _cfg:
        with _lock:
            if _client_cfg != _cfg:
                _client_cfg = _cfg
                _api_key, _base_url = _cfg
                _client = AsyncOpenAI(api_key=_api_key, base_url=_base_url)
    return _client

async def get_response(
    messages: list[dict],
    model: str = None,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
):
    _kwargs = {
        "model": model or os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": int(os.environ.get("LLM_MAX_TOKENS", "16384")),
        "stream": True,
        "extra_body": {
            "thinking": {"type": thinking or os.environ.get("LLM_THINKING", "disabled")},
            "reasoning_effort": reasoning_effort or os.environ.get("LLM_REASONING_EFFORT", "max"),
        },
    }
    _response = await _get_client().chat.completions.create(**_kwargs)
    async for _chunk in _response:
        if _chunk.choices[0].delta.content:
            yield _chunk.choices[0].delta.content

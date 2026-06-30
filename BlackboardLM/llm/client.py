from openai import AsyncOpenAI
import threading
import BlackboardLM.settings as _s

if not _s.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

_local = threading.local()

def _get_client():
    if not hasattr(_local, "client"):
        _local.client = AsyncOpenAI(api_key=_s.OPENAI_API_KEY, base_url=_s.OPENAI_BASE_URL)
    return _local.client

async def get_response(
    messages: list[dict],
    model: str = _s.LLM_MODEL,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
):
    kwargs = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "stream": True,
    }
    _body = {}
    _t = thinking or _s.LLM_THINKING
    if _t:
        _body["thinking"] = {"type": _t}
    _re = reasoning_effort or _s.LLM_REASONING_EFFORT
    if _re:
        _body["reasoning_effort"] = _re
    if _body:
        kwargs["extra_body"] = _body
    response = await _get_client().chat.completions.create(**kwargs)
    async for _chunk in response:
        if _chunk.choices[0].delta.content:
            yield _chunk.choices[0].delta.content

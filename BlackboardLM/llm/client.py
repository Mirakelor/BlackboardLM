from openai import AsyncOpenAI
import BlackboardLM.settings as _s

if not _s.OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

_client = AsyncOpenAI(api_key=_s.OPENAI_API_KEY, base_url=_s.OPENAI_BASE_URL)

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
    body = {}
    t = thinking or _s.LLM_THINKING
    if t:
        body["thinking"] = {"type": t}
    re = reasoning_effort or _s.LLM_REASONING_EFFORT
    if re:
        body["reasoning_effort"] = re
    if body:
        kwargs["extra_body"] = body
    response = await _client.chat.completions.create(**kwargs)
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

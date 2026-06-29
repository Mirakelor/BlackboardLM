import os
from openai import AsyncOpenAI
import BlackboardLM.settings

api_key = os.environ.get("DEEPSEEK_API_KEY", "")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")

client = AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")

async def get_response(messages: list[dict], model: str = "deepseek-v4-pro"):
    response = await client.chat.completions.create(
        model=model, messages=messages, temperature=0.7, stream=True
    )
    async for chunk in response:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

import json
import os
import BlackboardLM.config.settings as _s

_KEY_MAP = {
    "DEEPSEEK_API_KEY": "apiKey",
    "DEEPSEEK_BASE_URL": "baseUrl",
    "LLM_MODEL": "model",
    "LLM_THINKING": "thinking",
    "LLM_REASONING_EFFORT": "reasoningEffort",
    "LLM_MAX_TOKENS": "maxTokens",
}

def _build_config():
    return {
        "apiKey": _s.DEEPSEEK_API_KEY or "",
        "baseUrl": _s.DEEPSEEK_BASE_URL,
        "model": _s.LLM_MODEL,
        "thinking": _s.LLM_THINKING,
        "reasoningEffort": _s.LLM_REASONING_EFFORT,
        "maxTokens": _s.LLM_MAX_TOKENS,
        "hfEndpoint": os.environ.get("HF_ENDPOINT", "https://huggingface.co"),
    }

def get_llm_config_json():
    return json.dumps(_build_config(), ensure_ascii=False)

def get_llm_config():
    return _build_config()

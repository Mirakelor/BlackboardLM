import json

import BlackboardLM.config.settings as _s

def _build_config():
    return {
        "apiKey": _s.DEEPSEEK_API_KEY or "",
        "baseUrl": _s.DEEPSEEK_BASE_URL,
        "model": _s.LLM_MODEL,
        "thinking": _s.LLM_THINKING,
        "reasoningEffort": _s.LLM_REASONING_EFFORT,
        "maxTokens": _s.LLM_MAX_TOKENS,
        "proxyUrl": "/api/hf-proxy",
    }

def get_llm_config_json():
    return json.dumps(_build_config(), ensure_ascii=False)

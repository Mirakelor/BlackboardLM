import json
import os


def _build_config():
    return {
        "apiKey": os.environ.get("DEEPSEEK_API_KEY", ""),
        "baseUrl": os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        "model": os.environ.get("LLM_MODEL", "deepseek-v4-flash"),
        "thinking": os.environ.get("LLM_THINKING", "disabled"),
        "reasoningEffort": os.environ.get("LLM_REASONING_EFFORT", "max"),
        "maxTokens": int(os.environ.get("LLM_MAX_TOKENS", "16384")),
    }


def get_llm_config_json():
    return json.dumps(_build_config(), ensure_ascii=False)

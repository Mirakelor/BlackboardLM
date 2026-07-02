import os

import httpx
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.requests import Request

_FALLBACKS = [
    os.environ.get("HF_ENDPOINT", "https://huggingface.co"),
    "https://hf-mirror.com",
]

hf_proxy_app = FastAPI()


@hf_proxy_app.get("/api/hf-proxy/{_path:path}")
@hf_proxy_app.head("/api/hf-proxy/{_path:path}")
async def _hf_proxy(_request: Request, _path: str = ""):
    _headers = {}
    if "range" in _request.headers:
        _headers["range"] = _request.headers["range"]
    _method = "GET" if _request.method == "GET" else "HEAD"

    for _endpoint in _FALLBACKS:
        try:
            _url = f"{_endpoint}/{_path}"
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, trust_env=False) as client:
                _resp = await client.send(
                    client.build_request(_method, _url, headers=_headers)
                )
                _resp_headers = {
                    "content-type": _resp.headers.get("content-type", "application/octet-stream"),
                    "accept-ranges": "bytes",
                    "cache-control": "public, max-age=31536000",
                    "access-control-allow-origin": "*",
                }
                _cl = _resp.headers.get("content-length")
                if _cl:
                    _resp_headers["content-length"] = _cl
                return PlainTextResponse(
                    _resp.content.decode("utf-8", errors="replace"),
                    status_code=_resp.status_code,
                    headers=_resp_headers,
                )
        except Exception:
            continue
    return PlainTextResponse("all endpoints failed", status_code=502)

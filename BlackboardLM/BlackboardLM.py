import reflex as rx

from BlackboardLM.components.layout import index
from BlackboardLM.state import AppState

app = rx.App()
app.add_page(index, route="/", on_load=AppState.on_load)

from BlackboardLM.proxy_api import _hf_proxy
app._api.add_route("/api/hf-proxy/{_path:path}", _hf_proxy, methods=["GET", "HEAD"])

import reflex as rx

from BlackboardLM.components.layout import index
from BlackboardLM.state import AppState
from BlackboardLM.proxy_api import hf_proxy_app

app = rx.App(api_transformer=hf_proxy_app)
app.add_page(index, route="/", on_load=AppState.on_load)

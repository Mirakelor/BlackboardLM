import reflex as rx

from BlackboardLM.components.layout import index
from BlackboardLM.state import AppState

app = rx.App()
app.add_page(index, route="/", on_load=AppState.on_load)

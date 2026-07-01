import reflex as rx

from BlackboardLM.components.layout import index

app = rx.App()
app.add_page(index, route="/")

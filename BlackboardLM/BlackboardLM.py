import reflex as rx
from BlackboardLM.state import AppState

def sidebar() -> rx.Component:
    return rx.box(
        rx.heading("Sources", size="5"),
        rx.upload(
            rx.button("Upload Files"),
            multiple=True,
            on_drop=AppState.upload_file,
            accept={
                "application/pdf": [".pdf"],
                "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
                "text/plain": [".txt", ".md"],
                "text/html": [".html"],
            },
            margin_bottom="2rem",
        ),
        rx.foreach(AppState.uploaded_files, lambda f: rx.text(f)),
        width="250px",
        padding="1rem",
        border_right="1px solid #eee",
    )

def chat_area() -> rx.Component:
    return rx.vstack(
        rx.foreach(
            AppState.chat_messages,
            lambda msg: rx.box(
                rx.text(msg["role"], font_weight="bold"),
                rx.text(msg["content"]),
            ),
        ),
        rx.hstack(
            rx.input(
                value=AppState.current_input,
                on_change=AppState.set_input,
                placeholder="Ask a question...",
                width="100%",
            ),
            rx.button("Send", on_click=AppState.send_message),
        ),
        padding="1rem",
        height="100%",
    )

def index() -> rx.Component:
    return rx.hstack(
        sidebar(),
        chat_area(),
        width="100%",
        height="100vh",
    )

app = rx.App()
app.add_page(index)

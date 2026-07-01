import reflex as rx
from BlackboardLM.state import AppState

def login_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.icon("book-open", size=48, color=AppState.theme["primary"]),
            rx.heading(
                "BlackboardLM",
                size="7",
                font_family=AppState.theme["font_heading"],
                color=AppState.theme["primary"],
                letter_spacing="0.05em",
            ),
            rx.text(
                AppState.theme["description"],
                font_size="sm",
                color=AppState.theme["text_muted"],
                font_style="italic",
                margin_bottom="16px",
            ),
            rx.input(
                placeholder="Password",
                type="password",
                value=AppState.login_password,
                on_change=AppState.set_login_password,
                on_key_down=AppState.handle_login_key,
                background=AppState.theme["input_bg"],
                border=AppState.theme["input_border"],
                color=AppState.theme["text_primary"],
                font_size="sm",
                width="240px",
                text_align="center",
            ),
            rx.cond(
                AppState.login_error != "",
                rx.text(
                    AppState.login_error,
                    font_size="xs",
                    color=AppState.theme["accent"],
                ),
            ),
            rx.button(
                rx.text("Enter", font_size="sm"),
                on_click=AppState.login,
                background=AppState.theme["primary"],
                color=AppState.theme["background"],
                border_radius=AppState.theme["radius"],
                width="240px",
                cursor="pointer",
            ),
            spacing="3",
            align="center",
        ),
        display="flex",
        align_items="center",
        justify_content="center",
        height="100dvh",
        width="100%",
        background=AppState.theme["background"],
    )

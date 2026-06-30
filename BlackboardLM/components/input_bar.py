import reflex as rx
from BlackboardLM.state import AppState

def input_bar() -> rx.Component:
    return rx.box(
        rx.form(
            rx.hstack(
                rx.icon("feather", size=18, color=AppState.theme["text_muted"], flex_shrink="0"),
                rx.text_area(
                    value=AppState.current_input,
                    on_change=AppState.set_input,
                    placeholder=AppState.theme["placeholder"],
                    width="100%",
                    variant="soft",
                    font_family=AppState.theme["font_body"],
                    font_style="italic",
                    font_size="16px",
                    color=AppState.theme["text_primary"],
                    rows="1",
                    resize="none",
                    style={
                        "background": "transparent",
                        "border": "none",
                        "box_shadow": "none",
                        "outline": "none",
                        "padding": "8px 4px",
                        "line_height": "24px",
                        "min_height": "24px",
                        "overflow": "hidden",
                    },
                    color_scheme="gold",
                ),
                rx.button(
                    rx.cond(
                        AppState.is_processing,
                        rx.spinner(size="3", color=AppState.theme["background"]),
                        rx.icon("send-horizontal", size=18),
                    ),
                    type="submit",
                    background=AppState.theme["primary"],
                    color=AppState.theme["background"],
                    border_radius="full",
                    padding="8px",
                    cursor="pointer",
                    flex_shrink="0",
                    style={"_hover": {"box_shadow": f"0 0 15px {AppState.theme["primary"]}"}},
                ),
                spacing="2",
                width="100%",
                align="center",
            ),
            on_submit=AppState.send_message,
            width="100%",
            reset_on_submit=False,
        ),
        padding="10px 20px",
        margin="0",
        border_radius="16px",
        background=AppState.theme["input_bg"],
        border=AppState.theme["input_border"],
        box_shadow=AppState.theme["shadow"],
        width="100%",
        class_name="input-container",
    )

import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.theme as _theme

def _message_bubble(msg: dict) -> rx.Component:
    is_user = msg["role"] == "user"
    return rx.box(
        rx.cond(
            is_user,
            rx.box(
                rx.text(msg["content"], color=AppState.theme["message_user_color"], font_size="15px", line_height="1.6"),
                background=AppState.theme["message_user_bg"],
                border_radius="4px 16px 16px 16px",
                padding="12px 18px",
                box_shadow="2px 3px 10px rgba(0,0,0,0.3)",
                margin_left="auto",
                max_width="75%",
                animation="message-enter 0.35s ease-out",
            ),
            rx.box(
                rx.markdown(msg["content"], color=AppState.theme["message_ai_color"]),
                background=AppState.theme["message_ai_bg"],
                border=AppState.theme["message_ai_border"],
                border_radius="4px 16px 16px 16px",
                padding="16px 22px",
                box_shadow=AppState.theme["message_ai_shadow"],
                max_width="85%",
                animation="message-enter 0.35s ease-out",
                class_name=rx.cond(AppState.theme_name == _theme.THEME_HOGWARTS, "parchment-texture", ""),
            ),
        ),
        width="100%",
        padding="4px 0",
        class_name="message-row",
    )

def chat_area() -> rx.Component:
    return rx.box(
        rx.scroll_area(
            rx.vstack(
                rx.foreach(AppState.chat_messages, _message_bubble),
                rx.cond(
                    AppState.is_processing,
                    rx.hstack(
                        rx.spinner(size="3", color=AppState.theme["primary"]),
                        rx.text(AppState.theme["loading_text"], font_size="sm", color=AppState.theme["text_muted"], font_style="italic"),
                        spacing="2",
                        padding_x="24px",
                    ),
                ),
                rx.box(id="chat-bottom", height="1px"),
                spacing="1",
                padding_x="24px",
                padding_y="16px",
                align_items="stretch",
                width="100%",
            ),
            width="100%",
            type="hover",
            class_name="chat-scroll-area",
            style={"flex": "1", "min_height": "0"},
        ),
        display="flex",
        flex_direction="column",
        flex="1",
        min_height="0",
        width="100%",
    )

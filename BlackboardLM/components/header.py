import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.config.theme as _theme

def _theme_switch(theme_id: str) -> rx.Component:
    _display = _theme.THEMES[theme_id].display_name
    return rx.box(
        rx.text(_display, font_size="xs", white_space="nowrap"),
        padding="4px 12px",
        border_radius="full",
        cursor="pointer",
        background=rx.cond(
            AppState.theme_name == theme_id,
            AppState.theme["primary"],
            "transparent",
        ),
        color=rx.cond(
            AppState.theme_name == theme_id,
            AppState.theme["background"],
            AppState.theme["text_muted"],
        ),
        border=f"1px solid {rx.cond(AppState.theme_name == theme_id, AppState.theme["primary"], AppState.theme["text_muted"])}",
        on_click=AppState.set_theme(theme_id),
        style={"_hover": {"border_color": AppState.theme["primary"]}},
        transition="all 0.2s ease",
    )

def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("book-open", size=22, color=AppState.theme["primary"]),
                rx.heading(
                    "BlackboardLM",
                    size="6",
                    font_family=AppState.theme["font_heading"],
                    color=AppState.theme["primary"],
                    letter_spacing="0.05em",
                    class_name="header-heading",
                ),
                rx.text(
                    AppState.theme["description"],
                    font_size="sm",
                    color=AppState.theme["text_muted"],
                    font_style="italic",
                    class_name="header-subtitle",
                ),
                spacing="2",
                flex_shrink="1",
                overflow="hidden",
                min_width="0",
            ),
            rx.spacer(),
            rx.hstack(
                _theme_switch(_theme.THEME_HOGWARTS),
                _theme_switch(_theme.THEME_SAKURA),
                rx.icon(
                    "settings",
                    size=20,
                    color=AppState.theme["text_muted"],
                    cursor="pointer",
                    on_click=AppState.toggle_settings,
                    style={"_hover": {"color": AppState.theme["primary"]}},
                ),
                spacing="2",
                align="center",
                flex_shrink="0",
            ),
            width="100%",
            align="center",
        ),
        padding="14px 24px",
        border_bottom=AppState.theme["border"],
        background=AppState.theme["surface"],
        width="100%",
        flex_shrink="0",
        class_name="header-bar",
    )

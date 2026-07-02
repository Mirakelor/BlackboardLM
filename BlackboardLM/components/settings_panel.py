import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.config.settings as _s

_MODE_OPTIONS = ["naive", "local", "global", "hybrid", "mix"]
_RESPONSE_OPTIONS = ["Multiple Paragraphs", "Bullet Points", "Single Paragraph"]
_REASONING_OPTIONS = ["low", "medium", "high", "max"]

def _label(_text: str) -> rx.Component:
    return rx.text(_text, font_size="xs", color=AppState.theme["text_muted"], font_weight="bold", text_transform="uppercase", letter_spacing="0.05em")

def _restart_badge() -> rx.Component:
    return rx.text(
        "restart",
        font_size="10px",
        color=AppState.theme["accent"],
        background=f"{AppState.theme['accent']}15",
        padding="1px 6px",
        border_radius="3px",
    )

def _text_input(_label_text: str, _value: str, _on_change, *, _restart: bool = True, _password: bool = False) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            _label(_label_text),
            rx.cond(_restart, _restart_badge(), rx.text("")),
            spacing="2",
            align="center",
        ),
        rx.input(
            value=_value,
            on_change=_on_change,
            type="password" if _password else "text",
            background=AppState.theme["input_bg"],
            border=AppState.theme["input_border"],
            color=AppState.theme["text_primary"],
            font_size="sm",
            width="100%",
        ),
        spacing="1",
        align="start",
        width="100%",
    )

def _select_input(_label_text: str, _value: str, _options: list[str], _on_change, *, _restart: bool = True) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            _label(_label_text),
            rx.cond(_restart, _restart_badge(), rx.text("")),
            spacing="2",
            align="center",
        ),
        rx.select(
            _options,
            value=_value,
            on_change=_on_change,
            variant="soft",
            background=AppState.theme["input_bg"],
            border=AppState.theme["input_border"],
            color=AppState.theme["text_primary"],
            font_size="sm",
            width="100%",
            style={"paddingLeft": "12px", "paddingRight": "32px"},
        ),
        spacing="1",
        align="start",
        width="100%",
    )

def _slider_input(_label_text: str, _value: int, _on_change) -> rx.Component:
    return rx.vstack(
        _label(_label_text),
        rx.hstack(
            rx.slider(
                value=[_value],
                min=1024,
                max=32768,
                step=1024,
                on_change=_on_change,
                width="100%",
            ),
            rx.text(
                f"{_value // 1024}K",
                font_size="sm",
                color=AppState.theme["primary"],
                flex_shrink="0",
                min_width="40px",
                text_align="right",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="1",
        align="start",
        width="100%",
    )

def _section(_title: str, _icon: str) -> rx.Component:
    return rx.hstack(
        rx.icon(_icon, size=16, color=AppState.theme["primary"]),
        rx.text(_title, font_size="sm", font_weight="bold", color=AppState.theme["text_primary"]),
        spacing="2",
        align="center",
        padding_bottom="4px",
        border_bottom=f"1px solid {AppState.theme['border']}",
        width="100%",
        margin_bottom="8px",
    )

def settings_panel() -> rx.Component:
    return rx.box(
        rx.box(
            on_click=AppState.toggle_settings,
            position="fixed",
            left="0",
            top="0",
            width="100vw",
            height="100vh",
            background="rgba(0,0,0,0.4)",
            z_index=998,
            opacity=rx.cond(AppState.settings_visible, "1", "0"),
            pointer_events=rx.cond(AppState.settings_visible, "auto", "none"),
            style={"transition": "opacity 0.3s ease"},
        ),
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Settings", font_size="lg", font_weight="bold", color=AppState.theme["text_primary"]),
                    rx.spacer(),
                    rx.icon("x", size=20, color=AppState.theme["text_muted"], cursor="pointer", on_click=AppState.toggle_settings),
                    spacing="3",
                    align="center",
                    width="100%",
                ),
                rx.scroll_area(
                    rx.vstack(
                        _section("Model", "brain"),
                        _text_input("API Key", AppState.settings_api_key, AppState.set_settings_api_key, _restart=False, _password=True),
                        _text_input("Model ID", AppState.settings_model, AppState.set_settings_model, _restart=False),
                        _text_input("Base URL", AppState.settings_base_url, AppState.set_settings_base_url, _restart=False),
                        _select_input("Thinking", AppState.settings_thinking, ["enabled", "disabled"], AppState.set_settings_thinking, _restart=False),
                        _select_input("Reasoning Effort", AppState.settings_reasoning, _REASONING_OPTIONS, AppState.set_settings_reasoning, _restart=False),
                        _slider_input("Max Output Tokens", AppState.settings_max_tokens, AppState.set_settings_max_tokens),
                        _section("Query", "search"),
                        _select_input("Query Mode", AppState.settings_query_mode, _MODE_OPTIONS, AppState.set_settings_query_mode, _restart=False),
                        _select_input("Response Style", AppState.settings_response_type, _RESPONSE_OPTIONS, AppState.set_settings_response_type, _restart=False),
                        spacing="4",
                    ),
                    flex="1",
                    type="auto",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("save", size=16),
                        rx.text("Save & Apply", font_size="sm"),
                        spacing="2",
                    ),
                    on_click=AppState.save_settings,
                    background=AppState.theme["primary"],
                    color=AppState.theme["background"],
                    border_radius=AppState.theme["radius"],
                    width="100%",
                    cursor="pointer",
                ),
                rx.cond(
                    AppState.settings_saved,
                    rx.text("Saved. All settings applied.", font_size="xs", color=AppState.theme["accent"]),
                ),
                rx.separator(size="4", style={"color": AppState.theme["text_muted"], "opacity": 0.2}),
                _section("Data", "database"),
                rx.button(
                    rx.hstack(
                        rx.icon("trash-2", size=16),
                        rx.text("Clear All Data", font_size="sm"),
                        spacing="2",
                    ),
                    on_click=AppState.clear_all_data,
                    background="transparent",
                    color=AppState.theme["accent"],
                    border=f"1px solid {AppState.theme['accent']}",
                    border_radius=AppState.theme["radius"],
                    width="100%",
                    cursor="pointer",
                    style={"_hover": {"background": f"{AppState.theme['accent']}15"}},
                ),
                rx.cond(
                    AppState.clear_done,
                    rx.text("All data cleared.", font_size="xs", color=AppState.theme["accent"]),
                ),
                rx.cond(
                    _s.ACCESS_PASSWORD != "",
                    rx.button(
                        rx.hstack(
                            rx.icon("log-out", size=16),
                            rx.text("Logout", font_size="sm"),
                            spacing="2",
                        ),
                        on_click=AppState.logout,
                        background="transparent",
                        color=AppState.theme["text_muted"],
                        border=f"1px solid {AppState.theme['text_muted']}",
                        border_radius=AppState.theme["radius"],
                        width="100%",
                        cursor="pointer",
                    ),
                ),
                spacing="4",
                padding="20px",
                height="100%",
            ),
            position="fixed",
            right="0",
            top="0",
            width="380px",
            max_width="90vw",
            height="100vh",
            background=AppState.theme["surface"],
            border_left=AppState.theme["border"],
            box_shadow=AppState.theme["shadow"],
            z_index=999,
            transform=rx.cond(AppState.settings_visible, "translateX(0)", "translateX(100%)"),
            style={"transition": "transform 0.3s ease"},
        ),
    )

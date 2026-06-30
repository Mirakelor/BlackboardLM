import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.theme as _theme
from BlackboardLM.components.styles import global_styles
from BlackboardLM.components.header import header
from BlackboardLM.components.decorations import hogwarts_stars, sakura_petals
from BlackboardLM.components.star_chart import star_chart
from BlackboardLM.components.documents import doc_shelf, doc_preview
from BlackboardLM.components.chat import chat_area
from BlackboardLM.components.input_bar import input_bar

def index() -> rx.Component:
    return rx.fragment(
        global_styles(),
        rx.html("""
        <div id="loading">
            <div class="cat">
                <div class="body"></div>
                <div class="head">
                    <div class="face"></div>
                </div>
                <div class="foot">
                    <div class="tummy-end"></div>
                    <div class="bottom"></div>
                    <div class="legs left"></div>
                    <div class="legs right"></div>
                </div>
                <div class="paw">
                    <div class="hands left"></div>
                    <div class="hands right"></div>
                </div>
            </div>
        </div>
        """),
        rx.box(
            rx.cond(
                AppState.theme_name == _theme.THEME_HOGWARTS,
                hogwarts_stars(),
                sakura_petals(),
            ),
            header(),
            rx.flex(
                doc_shelf(),
                rx.box(
                    doc_preview(AppState.expanded_doc),
                    max_height=rx.cond(AppState.expanded_doc != "", "400px", "0px"),
                    overflow="hidden",
                    style={"transition": "max-height 0.3s ease"},
                    flex_shrink="0",
                ),
                star_chart(),
                rx.separator(size="4", flex_shrink="0", margin_x="24px", margin_y="8px", style={"color": AppState.theme["text_muted"], "opacity": 0.3}),
                chat_area(),
                direction="column",
                flex="1",
                width="100%",
                max_width=["100%", "100%", "780px", "920px"],
                margin_x="auto",
                min_height="0",
                overflow="hidden",
            ),
            rx.vstack(
                rx.text(
                    "Enter ↵ 发送 · Shift + Enter ↵ 换行",
                    font_size="12px",
                    color=AppState.theme["text_muted"],
                    text_align="center",
                ),
                input_bar(),
                spacing="1",
                align="center",
                padding_top="8px",
                padding_bottom="4px",
                padding_x="16px",
                flex_shrink="0",
                width="100%",
                max_width=["100%", "100%", "860px", "1000px"],
                margin_x="auto",
            ),
            display="flex",
            flex_direction="column",
            height="100dvh",
            width="100%",
            background=AppState.theme["background"],
            class_name=rx.cond(AppState.theme_name == _theme.THEME_HOGWARTS, "hogwarts-bg", "sakura-bg"),
        ),
        on_mount=AppState.on_load,
    )

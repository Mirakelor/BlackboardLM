import reflex as rx

from BlackboardLM.components.styles import global_styles
from BlackboardLM.components.decorations import hogwarts_stars, sakura_petals
from BlackboardLM.components.header import header
from BlackboardLM.components.settings_panel import settings_panel
from BlackboardLM.components.documents import doc_shelf, doc_preview
from BlackboardLM.components.star_chart import star_chart
from BlackboardLM.components.chat import chat_area
from BlackboardLM.components.input_bar import input_bar
from BlackboardLM.components.auth import login_card
from BlackboardLM.state import AppState
import BlackboardLM.config.theme as _theme

def _main_app() -> rx.Component:
    return rx.box(
        rx.cond(
            AppState.theme_name == _theme.THEME_HOGWARTS,
            hogwarts_stars(),
            sakura_petals(),
        ),
        header(),
        settings_panel(),
        rx.html(f"""
        <div id="rag-theme-colors" style="display:none">{AppState.theme["primary"]}|{AppState.theme["background"]}|{AppState.theme["text_primary"]}|{AppState.theme["surface"]}|{AppState.theme["text_muted"]}</div>
        """),
        rx.html("""
        <div id="rag-status-bar" style="display:none;position:fixed;top:38px;left:50%;transform:translateX(-50%);z-index:10000;padding:5px 18px;font-size:12px;align-items:center;gap:8px;border-radius:16px;box-shadow:0 2px 16px rgba(0,0,0,0.12);font-family:system-ui,sans-serif;max-width:500px;width:auto;white-space:nowrap;backdrop-filter:blur(4px);">
            <span id="rag-status-spinner" style="display:inline-block;width:12px;height:12px;border:2px solid rgba(128,128,128,0.2);border-top:2px solid currentColor;border-radius:50%;animation:rag-spin 0.8s linear infinite;flex-shrink:0;"></span>
            <span id="rag-status-text"></span>
            <span id="rag-status-bar-fill" style="display:none;height:3px;border-radius:2px;transition:width 0.3s ease;flex:1;min-width:80px;opacity:0.6;"></span>
            <button id="rag-status-close" style="display:none;background:none;border:none;cursor:pointer;font-size:14px;padding:0 2px;opacity:0.5;flex-shrink:0;" onclick="document.getElementById('rag-status-bar').style.display='none'">&times;</button>
        </div>
        <style>
            @keyframes rag-spin { to { transform: rotate(360deg); } }
        </style>
        """),
        rx.box(
            AppState.rag_llm_config_json,
            id="rag-llm-config",
            display="none",
        ),
        rx.box(
            AppState.rag_doc_counter,
            id="rag-doc-counter",
            display="none",
        ),
        rx.box(
            AppState.rag_doc_text,
            id="rag-doc-text",
            display="none",
        ),
        rx.box(
            AppState.rag_query_counter,
            id="rag-query-counter",
            display="none",
        ),
        rx.box(
            AppState.rag_query_params,
            id="rag-query-params",
            display="none",
        ),
        rx.box(
            AppState.rag_reset_counter,
            id="rag-reset-counter",
            display="none",
        ),
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
            overflow_y="auto",
            overflow_x="hidden",
            id="main-scroll",
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
    )

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
        rx.cond(
            AppState.is_authenticated,
            _main_app(),
            login_card(),
        ),
    )

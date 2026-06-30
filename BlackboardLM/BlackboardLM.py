import reflex as rx
from BlackboardLM.state import AppState
import BlackboardLM.theme as _theme

_ACCEPT = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/plain": [".txt", ".md"],
    "text/html": [".html"],
}

def global_styles() -> rx.Component:
    return rx.fragment(
        rx.html(f"""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="{AppState.theme["google_fonts_url"]}" rel="stylesheet">
        <style>
            *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
            html, body {{
                font-family: {AppState.theme["font_body"]};
                background: {AppState.theme["background"]};
                color: {AppState.theme["text_primary"]};
                overflow: hidden;
                height: 100dvh;
                -webkit-overflow-scrolling: touch;
            }}
            {AppState.theme["css_extra"]}
            
            div[role="button"] {{
                border: none !important;
                background: transparent !important;
                border-radius: 0 !important;
                padding: 0 !important;
                margin: 0 !important;
                width: fit-content !important;
                display: flex !important;
            }}
            
            .rx-Upload {{ padding: 0px !important; border: none !important; }}
            .rx-Upload > div {{ padding: 0px 16px !important; }}
            ::-webkit-scrollbar {{ width: 6px; height: 3px; }}
            ::-webkit-scrollbar-track {{ background: transparent; }}
            ::-webkit-scrollbar-thumb {{
                background: {AppState.theme["text_muted"]};
                border-radius: 3px;
            }}
            
            @media (max-width: 640px) {{
                .header-subtitle {{ display: none; }}
                .header-heading {{ font-size: 18px !important; }}
                .star-chart-box {{ height: 80px !important; }}
                .header-bar {{ padding: 10px 14px !important; }}
                .doc-shelf-scroll > div {{ gap: 8px !important; }}
                .doc-card {{ min-width: 150px !important; max-width: 150px !important; }}
                .message-row {{ padding: 2px 8px !important; }}
                .input-container {{ margin: 8px 12px !important; }}
            }}
            
            ::placeholder {{ color: {AppState.theme["text_secondary"]}; opacity: 0.8; }}
            ::selection {{ background: {AppState.theme["primary"]}; color: {AppState.theme["background"]}; }}
            textarea::selection {{ background: {AppState.theme["primary"]}; color: {AppState.theme["background"]}; }}
        </style>
        """),
        rx.script("""
        (function initScroll() {
            var vp = document.querySelector('[data-radix-scroll-area-viewport]');
            if (!vp) { setTimeout(initScroll, 200); return; }
            var _auto = false;
            vp.addEventListener('wheel', function(e) { if (e.deltaY < 0) _auto = false; });
            vp.addEventListener('touchmove', function() { _auto = false; });
            new MutationObserver(function(muts) {
                for (var i = 0; i < muts.length; i++) {
                    var added = muts[i].addedNodes;
                    for (var j = 0; j < added.length; j++) {
                        if (added[j].nodeType === 1 && added[j].querySelector && added[j].querySelector('[data-radix-scroll-area-viewport] .rt-Spinner, .rt-Spinner')) {
                            _auto = true;
                        }
                    }
                }
            }).observe(vp, {childList: true, subtree: true});
            setInterval(function() {
                if (_auto) vp.scrollTop = vp.scrollHeight;
            }, 80);
        })();
        """),
        rx.script("""
        document.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'TEXTAREA' && e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                var form = e.target.closest('form');
                if (form) form.requestSubmit();
            }
        });
        
        document.addEventListener('input', function(e) {
            if (e.target.tagName === 'TEXTAREA') {
                e.target.style.height = 'auto';
                var lineH = 24;
                var pad = 16;
                var maxH = lineH * 5 + pad;
                var newH = Math.min(e.target.scrollHeight, maxH);
                e.target.style.height = newH + 'px';
                e.target.style.overflowY = e.target.scrollHeight > maxH ? 'auto' : 'hidden';
            }
        });
        document.addEventListener('click', function(e) {
            var btn = e.target.closest('.doc-scroll-left') || e.target.closest('.doc-scroll-right');
            if (!btn) return;
            var shelf = document.querySelector('.doc-shelf-scroll');
            if (!shelf) return;
            var dir = btn.classList.contains('doc-scroll-left') ? -200 : 200;
            shelf.scrollBy({left: dir, behavior: 'smooth'});
        });
        """),
    )

def theme_switch(theme_id: str) -> rx.Component:
    display = _theme.THEMES[theme_id].display_name
    return rx.box(
        rx.text(display, font_size="xs", white_space="nowrap"),
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
                theme_switch(_theme.THEME_HOGWARTS),
                theme_switch(_theme.THEME_SAKURA),
                spacing="2",
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

def hogwarts_stars() -> rx.Component:
    stars = []
    for i in range(50):
        left = (i * 37 + 13) % 100
        top = (i * 53 + 7) % 100
        delay = (i * 0.47) % 4
        duration = 2.0 + (i % 3) * 0.8
        is_float = i % 4 == 0
        size = (3 + (i % 4)) if is_float else (2 + (i % 3))
        ani = f"star-twinkle {duration}s ease-in-out {delay}s infinite"
        if i % 4 == 0:
            ani += f", float-up {duration + 1.5}s ease-out {delay}s infinite"
        stars.append(
            rx.box(
                position="absolute",
                left=f"{left}%",
                top=f"{top}%",
                width=f"{size}px",
                height=f"{size}px",
                background=AppState.theme["star_chart_node"],
                border_radius="50%",
                animation=ani,
            )
        )
    return rx.box(
        *stars,
        class_name="hogwarts-stars",
    )

def sakura_petals() -> rx.Component:
    petals = []
    for i in range(28):
        left = (i * 73 + 17) % 100
        delay = (i * 1.3) % 8
        duration = 6 + (i % 5)
        ani = f"sakura-fall {duration}s linear {delay}s infinite"
        if i % 2 == 0:
            ani += f", sakura-sway {duration * 0.6}s ease-in-out {delay}s infinite"
        petals.append(
            rx.box(
                position="absolute",
                left=f"{left}%",
                top="-24px",
                width="14px",
                height="14px",
                background="radial-gradient(circle, #f8c8d8 0%, #e8a0bf 60%, transparent 100%)",
                border_radius="50% 0 50% 50%",
                animation=ani,
            )
        )
    return rx.box(
        *petals,
        class_name="sakura-petals",
    )

def star_chart() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("sparkles", size=16, color=AppState.theme["star_chart_node"]),
                rx.text(AppState.theme["star_chart_title"], font_size="sm", color=AppState.theme["text_secondary"], font_style="italic"),
                spacing="1",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon(
                    rx.cond(AppState.star_chart_visible, "chevron-up", "chevron-down"),
                    size=14,
                ),
                on_click=AppState.toggle_star_chart,
                variant="ghost",
                color=AppState.theme["text_secondary"],
                size="1",
            ),
            width="100%",
            align="center",
        ),
        rx.box(
            rx.text(
                AppState.theme["star_chart_empty"],
                font_size="xs",
                color=AppState.theme["text_muted"],
                text_align="center",
            ),
            width="100%",
            height=rx.cond(AppState.star_chart_visible, "100px", "0px"),
            margin_top=rx.cond(AppState.star_chart_visible, "6px", "0px"),
            border_radius=AppState.theme["radius"],
            background=AppState.theme["star_chart_bg"],
            border=AppState.theme["border"],
            display="flex",
            align_items="center",
            justify_content="center",
            class_name="star-chart-box",
            overflow="hidden",
            style={"transition": "height 0.3s ease, margin 0.3s ease, opacity 0.3s ease"},
        ),
        padding="10px 12px",
        margin_x="24px",
        margin_top="8px",
        border_radius=AppState.theme["radius"],
        background=AppState.theme["surface"],
        border=AppState.theme["border"],
        flex_shrink="0",
    )

def doc_card(filename: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon("file-text", size=16, color=AppState.theme["primary"]),
            rx.text(filename, font_size="xs", font_weight="medium", color=AppState.theme["text_primary"], max_width="140px", overflow="hidden", white_space="nowrap", text_overflow="ellipsis"),
            spacing="2",
            align="center",
        ),
        on_click=AppState.toggle_doc_preview(filename),
        cursor="pointer",
        min_width="180px",
        max_width="180px",
        padding="6px 14px",
        border_radius=AppState.theme["radius"],
        background=AppState.theme["doc_card_bg"],
        border=AppState.theme["doc_card_border"],
        border_left=f"3px solid {AppState.theme["primary"]}",
        transition="all 0.2s ease",
        class_name="doc-card",
        style={"_hover": {"box_shadow": AppState.theme["doc_card_hover_shadow"], "transform": "translateY(-2px)"}},
    )

def doc_shelf() -> rx.Component:
    return rx.cond(
        AppState.uploaded_files.length() > 0,
        rx.box(
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevron-left", size=16),
                    variant="ghost",
                    size="1",
                    color=AppState.theme["text_secondary"],
                    class_name="doc-scroll-left",
                    flex_shrink="0",
                    margin_right="4px",
                ),
                rx.box(
                    rx.flex(
                        rx.foreach(AppState.uploaded_files, doc_card),
                        rx.upload(
                            rx.box(
                                rx.hstack(
                                    rx.icon("plus", size=14),
                                    rx.text(AppState.theme["doc_add_text"], font_size="xs"),
                                    spacing="1",
                                    align="center",
                                ),
                                cursor="pointer",
                                padding="4px 12px",
                                border_radius=AppState.theme["radius"],
                                border=f"1px dashed {AppState.theme["text_muted"]}",
                                color=AppState.theme["text_muted"],
                                white_space="nowrap",
                                min_width="150px",
                                max_width="150px",
                                style={"_hover": {"border_color": AppState.theme["primary"], "color": AppState.theme["primary"]}},
                            ),
                            multiple=True,
                            on_drop=AppState.upload_file,
                            accept=_ACCEPT,
                            style={"padding": "0"},
                        ),
                        spacing="3",
                        width="max-content",
                        align_items="center",
                        flex_wrap="nowrap",
                    ),
                    overflow_x="auto",
                    flex="1",
                    class_name="doc-shelf-scroll",
                    style={"height": "44px", "overflowY": "hidden", "padding": "4px 0"},
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=16),
                    variant="ghost",
                    size="1",
                    color=AppState.theme["text_secondary"],
                    class_name="doc-scroll-right",
                    flex_shrink="0",
                    margin_left="4px",
                ),
                spacing="1",
                width="100%",
                align="center",
                style={"height": "52px"},
            ),
            padding="4px 24px",
            style={"flex": "0 0 auto"},
        ),
        rx.box(
            rx.upload(
                rx.box(
                    rx.hstack(
                        rx.icon("upload", size=14, color=AppState.theme["text_muted"]),
                        rx.text(
                            f"{AppState.theme["upload_text"]} · {AppState.theme["upload_hint"]}",
                            font_size="xs",
                            color=AppState.theme["text_muted"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    cursor="pointer",
                    style={"_hover": {"color": AppState.theme["primary"]}},
                ),
                multiple=True,
                on_drop=AppState.upload_file,
                accept=_ACCEPT,
            ),
            style={
                "maxWidth": "360px",
                "margin": "8px auto 0 auto",
                "height": "64px",
                "display": "flex",
                "alignItems": "center",
                "overflow": "hidden",
                "border_radius": AppState.theme["radius"],
                "border": f"1px dashed {AppState.theme["text_muted"]}",
                "cursor": "pointer",
            },
            flex_shrink="0",
        ),
    )

def doc_preview(filename: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("file-text", size=16, color=AppState.theme["primary"]),
                rx.text(filename, font_size="sm", font_weight="medium", color=AppState.theme["text_primary"]),
                spacing="2",
            ),
            rx.spacer(),
            rx.icon_button(
                rx.icon("x", size=14),
                on_click=AppState.toggle_doc_preview(filename),
                variant="ghost",
                color_scheme="gray",
                size="1",
            ),
            width="100%",
            margin_bottom="10px",
        ),
        rx.box(
            rx.markdown(
                f"*预览功能开发中...*\n\n点击文档后，此处将展示文档内容并自动定位到与当前对话相关的段落。",
                color=AppState.theme["text_secondary"],
            ),
            padding="16px",
            background=AppState.theme["surface_alt"],
            border_radius=AppState.theme["radius"],
            border=AppState.theme["border"],
            max_height="200px",
            overflow="auto",
        ),
        padding="12px 16px",
        margin_x="24px",
        margin_top="8px",
        border_radius=AppState.theme["radius"],
        background=AppState.theme["surface"],
        border=AppState.theme["border"],
        flex_shrink="0",
        animation="expand-enter 0.3s ease",
    )

def message_bubble(msg: dict) -> rx.Component:
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
                rx.foreach(AppState.chat_messages, message_bubble),
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

def index() -> rx.Component:
    return rx.fragment(
        global_styles(),
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

app = rx.App()
app.add_page(index, route="/")
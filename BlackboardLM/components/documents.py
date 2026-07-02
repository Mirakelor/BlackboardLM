import reflex as rx
from BlackboardLM.state import AppState

_ACCEPT = {
    "application/pdf": [".pdf"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "text/plain": [".txt", ".md"],
    "text/html": [".html"],
    "application/epub+zip": [".epub"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/tiff": [".tiff", ".tif"],
    "text/csv": [".csv"],
    "application/json": [".json"],
    "application/xml": [".xml"],
}

def _doc_card(filename: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.cond(
                AppState.parsing_files.contains(filename),
                rx.spinner(size="1", color=AppState.theme["primary"]),
                rx.icon("file-text", size=16, color=AppState.theme["primary"]),
            ),
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
                        rx.foreach(AppState.uploaded_files, _doc_card),
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
                            on_drop=AppState.handle_upload,
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
                            font_size="13px",
                            color=AppState.theme["text_muted"],
                        ),
                        spacing="2",
                        align="center",
                    ),
                    cursor="pointer",
                    style={"_hover": {"color": AppState.theme["primary"]}},
                ),
                multiple=True,
                on_drop=AppState.handle_upload,
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
                color=AppState.theme["text_secondary"],
                size="1",
            ),
            width="100%",
            margin_bottom="10px",
        ),
        rx.box(
            rx.cond(
                AppState.preview_ready,
                rx.markdown(
                    AppState.preview_content,
                    color=AppState.theme["text_primary"],
                ),
                rx.markdown(
                    AppState.theme["doc_loading_text"],
                    color=AppState.theme["text_secondary"],
                ),
            ),
            padding="16px",
            background=AppState.theme["surface_alt"],
            border_radius=AppState.theme["radius"],
            border=AppState.theme["border"],
            max_height="360px",
            overflow="auto",
            class_name="doc-preview-content",
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

import reflex as rx

from BlackboardLM.state import AppState

def star_chart() -> rx.Component:
    return rx.fragment(
        rx.box(
            AppState.graph_data_json,
            id="graph-data",
            display="none",
        ),
        rx.box(
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
                    rx.cond(
                        AppState.graph_node_count > 0,
                        "",
                        rx.cond(
                            AppState.uploaded_files.length() > 0,
                            AppState.theme["star_chart_processing"],
                            AppState.theme["star_chart_empty"],
                        ),
                    ),
                    font_size="xs",
                    color=AppState.theme["text_muted"],
                    text_align="center",
                    position="absolute",
                    top="50%",
                    left="50%",
                    transform="translate(-50%, -50%)",
                    pointer_events="none",
                    z_index="0",
                ),
                rx.box(
                    id="cy-star-chart",
                    width="100%",
                    height="180px",
                    style={
                        "--cy-edge-color": AppState.theme["star_chart_edge"],
                        "--cy-label-color": AppState.theme["text_primary"],
                        "--cy-outline-color": AppState.theme["star_chart_bg"],
                    },
                ),
                width="100%",
                max_height=rx.cond(AppState.star_chart_visible, "200px", "0px"),
                margin_top=rx.cond(AppState.star_chart_visible, "6px", "0px"),
                border_radius=AppState.theme["radius"],
                background=AppState.theme["star_chart_bg"],
                border=AppState.theme["border"],
                class_name="star-chart-box",
                overflow="hidden",
                position="relative",
                style={"transition": "max-height 0.3s ease, margin 0.3s ease"},
            ),
            padding="10px 12px",
            margin_x="24px",
            margin_top="8px",
            border_radius=AppState.theme["radius"],
            background=AppState.theme["surface"],
            border=AppState.theme["border"],
            flex_shrink="0",
        ),
    )

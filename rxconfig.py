import reflex as rx

config = rx.Config(
    app_name="BlackboardLM",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="inherit",
                has_background=True,
                radius="medium",
                accent_color="gold",
            ),
        ),
    ],
)

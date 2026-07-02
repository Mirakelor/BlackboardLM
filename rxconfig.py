import os
from pathlib import Path

os.environ.setdefault(
    "REFLEX_HOT_RELOAD_EXCLUDE_PATHS",
    str(Path(__file__).resolve().parent.joinpath(".env")),
)
os.environ.setdefault("ACCESS_PASSWORD", "fDu060927")

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

import reflex as rx
from BlackboardLM.state import AppState

def hogwarts_stars() -> rx.Component:
    stars = []
    for _i in range(50):
        left = (_i * 37 + 13) % 100
        _top = (_i * 53 + 7) % 100
        delay = (_i * 0.47) % 4
        duration = 2.0 + (_i % 3) * 0.8
        is_float = _i % 4 == 0
        size = (3 + (_i % 4)) if is_float else (2 + (_i % 3))
        _ani = f"star-twinkle {duration}s ease-in-out {delay}s infinite"
        if _i % 4 == 0:
            _ani += f", float-up {duration + 1.5}s ease-out {delay}s infinite"
        stars.append(
            rx.box(
                position="absolute",
                left=f"{left}%",
                top=f"{_top}%",
                width=f"{size}px",
                height=f"{size}px",
                background=AppState.theme["star_chart_node"],
                border_radius="50%",
                animation=_ani,
            )
        )
    return rx.box(
        *stars,
        class_name="hogwarts-stars",
    )

def sakura_petals() -> rx.Component:
    petals = []
    for _i in range(28):
        left = (_i * 73 + 17) % 100
        delay = (_i * 1.3) % 8
        duration = 6 + (_i % 5)
        _ani = f"sakura-fall {duration}s linear {delay}s infinite"
        if _i % 2 == 0:
            _ani += f", sakura-sway {duration * 0.6}s ease-in-out {delay}s infinite"
        petals.append(
            rx.box(
                position="absolute",
                left=f"{left}%",
                top="-24px",
                width="14px",
                height="14px",
                background="radial-gradient(circle, #f8c8d8 0%, #e8a0bf 60%, transparent 100%)",
                border_radius="50% 0 50% 50%",
                animation=_ani,
            )
        )
    return rx.box(
        *petals,
        class_name="sakura-petals",
    )

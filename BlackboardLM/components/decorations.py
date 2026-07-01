import reflex as rx
from BlackboardLM.state import AppState

def hogwarts_stars() -> rx.Component:
    _stars = []
    for _i in range(50):
        _left = (_i * 37 + 13) % 100
        _top = (_i * 53 + 7) % 100
        _delay = (_i * 0.47) % 4
        _duration = 2.0 + (_i % 3) * 0.8
        _is_float = _i % 4 == 0
        _size = (3 + (_i % 4)) if _is_float else (2 + (_i % 3))
        _ani = f"star-twinkle {_duration}s ease-in-out {_delay}s infinite"
        if _i % 4 == 0:
            _ani += f", float-up {_duration + 1.5}s ease-out {_delay}s infinite"
        _stars.append(
            rx.box(
                position="absolute",
                left=f"{_left}%",
                top=f"{_top}%",
                width=f"{_size}px",
                height=f"{_size}px",
                background=AppState.theme["star_chart_node"],
                border_radius="50%",
                animation=_ani,
            )
        )
    return rx.box(
        *_stars,
        class_name="hogwarts-stars",
    )

def sakura_petals() -> rx.Component:
    _petals = []
    for _i in range(28):
        _left = (_i * 73 + 17) % 100
        _delay = (_i * 1.3) % 8
        _duration = 6 + (_i % 5)
        _ani = f"sakura-fall {_duration}s linear {_delay}s infinite"
        if _i % 2 == 0:
            _ani += f", sakura-sway {_duration * 0.6}s ease-in-out {_delay}s infinite"
        _petals.append(
            rx.box(
                position="absolute",
                left=f"{_left}%",
                top="-24px",
                width="14px",
                height="14px",
                background="radial-gradient(circle, #f8c8d8 0%, #e8a0bf 60%, transparent 100%)",
                border_radius="50% 0 50% 50%",
                animation=_ani,
            )
        )
    return rx.box(
        *_petals,
        class_name="sakura-petals",
    )

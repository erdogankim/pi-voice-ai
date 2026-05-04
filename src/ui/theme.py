"""
theme.py — Color palettes for the Kivy UI.

Each theme is a dict of normalized RGBA tuples (Kivy's color format).
State colors map Pipeline states to a tint used by the status indicator.
"""
from src.pipeline import State


DARK = {
    "bg":          (0.08, 0.09, 0.12, 1),
    "panel":       (0.13, 0.14, 0.18, 1),
    "fg":          (0.92, 0.94, 0.96, 1),
    "muted":       (0.55, 0.58, 0.65, 1),
    "accent":      (0.30, 0.65, 0.95, 1),
    "user_msg":    (0.20, 0.55, 0.85, 1),
    "asst_msg":    (0.30, 0.30, 0.34, 1),
    "error":       (0.90, 0.35, 0.35, 1),
    "button":      (0.20, 0.55, 0.85, 1),
    "button_down": (0.85, 0.30, 0.30, 1),
}

LIGHT = {
    "bg":          (0.96, 0.96, 0.97, 1),
    "panel":       (1.00, 1.00, 1.00, 1),
    "fg":          (0.10, 0.11, 0.13, 1),
    "muted":       (0.45, 0.48, 0.52, 1),
    "accent":      (0.10, 0.45, 0.85, 1),
    "user_msg":    (0.20, 0.55, 0.85, 1),
    "asst_msg":    (0.85, 0.86, 0.88, 1),
    "error":       (0.85, 0.20, 0.20, 1),
    "button":      (0.10, 0.45, 0.85, 1),
    "button_down": (0.80, 0.25, 0.25, 1),
}


STATE_COLORS = {
    State.IDLE:         "muted",
    State.RECORDING:    "button_down",
    State.TRANSCRIBING: "accent",
    State.THINKING:     "accent",
    State.SPEAKING:     "user_msg",
}


def get_palette(name: str) -> dict:
    return LIGHT if name.lower() == "light" else DARK


def state_color(palette: dict, state: State):
    return palette[STATE_COLORS.get(state, "muted")]

"""Tests for ButtonHandler (mock mode, no real GPIO)."""
import pytest
from src.config import load_config


def make_handler():
    from src.button_handler import ButtonHandler
    cfg = load_config()
    cfg.button.mode = "hold"
    return ButtonHandler(cfg)


def test_on_press_callback_fires():
    handler = make_handler()
    events = []
    handler.on_press = lambda: events.append("press")
    handler._handle_press()
    assert events == ["press"]


def test_on_release_callback_fires():
    handler = make_handler()
    events = []
    handler.on_release = lambda: events.append("release")
    handler._handle_release()
    assert events == ["release"]


def test_hold_mode_press_then_release():
    handler = make_handler()
    events = []
    handler.on_press = lambda: events.append("press")
    handler.on_release = lambda: events.append("release")
    handler._handle_press()
    handler._handle_release()
    assert events == ["press", "release"]


def test_toggle_mode_two_presses():
    from src.button_handler import ButtonHandler
    cfg = load_config()
    cfg.button.mode = "toggle"
    handler = ButtonHandler(cfg)
    events = []
    handler.on_press = lambda: events.append("press")
    handler.on_release = lambda: events.append("release")
    handler._handle_press()   # first press → starts
    handler._handle_press()   # second press → stops
    assert events == ["press", "release"]


def test_toggle_mode_release_is_ignored():
    from src.button_handler import ButtonHandler
    cfg = load_config()
    cfg.button.mode = "toggle"
    handler = ButtonHandler(cfg)
    events = []
    handler.on_release = lambda: events.append("release")
    handler._handle_release()  # should be ignored in toggle mode
    assert events == []

"""
screens.py — Main Kivy screen for Pi Voice AI.

Layout (top to bottom):
  +-----------------------------+
  |     Pi Voice AI            |  header
  +-----------------------------+
  | [status indicator dot]      |
  |  "Dinliyorum..."            |  status row
  +-----------------------------+
  |  Geçmiş (scroll)            |  history list
  |   Siz: ...                  |
  |   Asistan: ...              |
  +-----------------------------+
  |   [ KONUŞ — basılı tut ]    |  push-to-talk button
  +-----------------------------+

The screen exposes three callable hooks meant to be wired by the App:
  screen.set_state(state)
  screen.add_message(role, text)
  screen.show_error(stage, message)

User interaction emits two callbacks set by the App:
  screen.on_press_button   = lambda: ...
  screen.on_release_button = lambda: ...
"""
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Ellipse
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock

from src.pipeline import State, STATE_LABELS
from src.ui.theme import get_palette, state_color


class StatusDot(Widget):
    """A coloured circle that reflects the pipeline state."""

    color = ListProperty([0.5, 0.5, 0.5, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            self._color_inst = Color(*self.color)
            self._dot = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self._redraw, size=self._redraw, color=self._on_color)

    def _redraw(self, *_):
        size = min(self.width, self.height)
        x = self.center_x - size / 2
        y = self.center_y - size / 2
        self._dot.pos = (x, y)
        self._dot.size = (size, size)

    def _on_color(self, *_):
        self._color_inst.rgba = self.color


class MessageBubble(BoxLayout):
    """A single chat row: 'Siz: ...' or 'Asistan: ...'."""

    def __init__(self, role: str, text: str, palette: dict, font_size: int, **kwargs):
        super().__init__(orientation="horizontal", size_hint_y=None, padding=(8, 4), **kwargs)

        label_color = palette["fg"]
        prefix = "Siz" if role == "user" else "Asistan"
        prefix_color = palette["user_msg"] if role == "user" else palette["accent"]

        prefix_lbl = Label(
            text=f"[b]{prefix}:[/b]",
            markup=True,
            color=prefix_color,
            font_size=font_size,
            size_hint_x=None,
            width=110,
            halign="right",
            valign="top",
        )
        prefix_lbl.bind(size=lambda lbl, _: setattr(lbl, "text_size", lbl.size))

        body_lbl = Label(
            text=text,
            color=label_color,
            font_size=font_size,
            halign="left",
            valign="top",
            size_hint_x=1,
        )

        # Make the bubble grow with wrapped text height
        def _resize(label, _value):
            label.text_size = (label.width, None)
            label.texture_update()
            label.height = max(label.texture_size[1], font_size + 8)
            self.height = max(prefix_lbl.height, body_lbl.height) + 8

        body_lbl.bind(width=_resize, texture_size=_resize)

        self.add_widget(prefix_lbl)
        self.add_widget(body_lbl)
        self.height = font_size * 2


class MainScreen(BoxLayout):
    status_text = StringProperty(STATE_LABELS[State.IDLE])

    def __init__(self, ui_config, **kwargs):
        super().__init__(orientation="vertical", padding=12, spacing=10, **kwargs)
        self._ui_cfg = ui_config
        self._palette = get_palette(ui_config.theme)
        self._font_size = ui_config.font_size

        self.on_press_button = lambda: None
        self.on_release_button = lambda: None

        self._draw_background()
        self.bind(size=self._update_bg, pos=self._update_bg)

        self._build_header()
        self._build_status_row()
        self._build_history()
        self._build_button()

    # ------------------------------------------------------------------ #
    # Background                                                          #
    # ------------------------------------------------------------------ #

    def _draw_background(self):
        with self.canvas.before:
            self._bg_color = Color(*self._palette["bg"])
            self._bg_rect = Rectangle(pos=self.pos, size=self.size)

    def _update_bg(self, *_):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size

    # ------------------------------------------------------------------ #
    # Sections                                                            #
    # ------------------------------------------------------------------ #

    def _build_header(self):
        header = Label(
            text="[b]Pi Voice AI[/b]",
            markup=True,
            color=self._palette["fg"],
            font_size=self._font_size + 6,
            size_hint_y=None,
            height=40,
        )
        self.add_widget(header)

    def _build_status_row(self):
        row = BoxLayout(orientation="horizontal", size_hint_y=None, height=44, spacing=12)

        self._dot = StatusDot(size_hint_x=None, width=24)
        self._dot.color = list(state_color(self._palette, State.IDLE))

        self._status_lbl = Label(
            text=STATE_LABELS[State.IDLE],
            color=self._palette["fg"],
            font_size=self._font_size + 2,
            halign="left",
            valign="middle",
        )
        self._status_lbl.bind(size=lambda lbl, _: setattr(lbl, "text_size", lbl.size))

        row.add_widget(self._dot)
        row.add_widget(self._status_lbl)
        self.add_widget(row)

    def _build_history(self):
        if not self._ui_cfg.show_history:
            self._history_box = None
            spacer = Widget()
            self.add_widget(spacer)
            return

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        self._history_box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=4,
            padding=(4, 4),
        )
        self._history_box.bind(minimum_height=self._history_box.setter("height"))
        scroll.add_widget(self._history_box)
        self._scroll = scroll
        self.add_widget(scroll)

    def _build_button(self):
        self._button = Button(
            text="KONUŞ — basılı tut",
            font_size=self._font_size + 4,
            size_hint_y=None,
            height=80,
            background_normal="",
            background_color=self._palette["button"],
            color=(1, 1, 1, 1),
        )
        self._button.bind(
            on_press=lambda *_: self._handle_press(),
            on_release=lambda *_: self._handle_release(),
        )
        self.add_widget(self._button)

    # ------------------------------------------------------------------ #
    # Touch handlers                                                      #
    # ------------------------------------------------------------------ #

    def _handle_press(self):
        try:
            self.on_press_button()
        except Exception:
            import logging
            logging.getLogger(__name__).exception("on_press_button raised")

    def _handle_release(self):
        try:
            self.on_release_button()
        except Exception:
            import logging
            logging.getLogger(__name__).exception("on_release_button raised")

    # ------------------------------------------------------------------ #
    # Public API (must be called on Kivy main thread)                     #
    # ------------------------------------------------------------------ #

    def set_state(self, state: State):
        self._status_lbl.text = STATE_LABELS.get(state, state.name)
        self._dot.color = list(state_color(self._palette, state))
        # Press button stays down while RECORDING; reflect by changing colour.
        if state == State.RECORDING:
            self._button.background_color = self._palette["button_down"]
            self._button.text = "Bırak — kaydı durdur"
        else:
            self._button.background_color = self._palette["button"]
            self._button.text = "KONUŞ — basılı tut"

    def add_message(self, role: str, text: str):
        if not self._history_box:
            return
        bubble = MessageBubble(role, text, self._palette, self._font_size)
        self._history_box.add_widget(bubble)
        self._trim_history()
        # Scroll to bottom on next frame, after layout
        Clock.schedule_once(lambda _: setattr(self._scroll, "scroll_y", 0), 0)

    def show_error(self, stage: str, message: str):
        if not self._history_box:
            return
        err = Label(
            text=f"[HATA — {stage}] {message}",
            color=self._palette["error"],
            font_size=self._font_size,
            size_hint_y=None,
            halign="left",
            valign="top",
        )
        err.bind(
            width=lambda lbl, w: setattr(lbl, "text_size", (w, None)),
            texture_size=lambda lbl, ts: setattr(lbl, "height", ts[1] + 4),
        )
        self._history_box.add_widget(err)
        self._trim_history()
        Clock.schedule_once(lambda _: setattr(self._scroll, "scroll_y", 0), 0)

    def _trim_history(self):
        limit = self._ui_cfg.history_limit
        children = self._history_box.children  # newest first in Kivy
        if len(children) > limit:
            for old in children[limit:]:
                self._history_box.remove_widget(old)

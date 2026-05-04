"""
app.py — Kivy application root for Pi Voice AI.

Wires the touch button to the Pipeline and forwards state/message events
back to the screen via Clock.schedule_once (UI updates must happen on
the Kivy main thread).

The blocking part of the pipeline (STT -> Claude -> TTS -> playback) is
dispatched to a worker thread so the UI stays responsive.
"""
import logging
import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window

from src.pipeline import Pipeline, State
from src.ui.screens import MainScreen
from src.ui.theme import get_palette

log = logging.getLogger(__name__)


class PiVoiceApp(App):
    title = "Pi Voice AI"

    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config_obj = config
        self.pipeline: Pipeline | None = None
        self.screen: MainScreen | None = None
        self._worker: threading.Thread | None = None

    # ------------------------------------------------------------------ #

    def build(self):
        palette = get_palette(self.config_obj.ui.theme)
        Window.clearcolor = palette["bg"]

        self.pipeline = Pipeline(self.config_obj)
        self.screen = MainScreen(self.config_obj.ui)

        # Pipeline -> UI (must marshal to Kivy main thread)
        self.pipeline.on_state_change = self._on_state_change
        self.pipeline.on_message = self._on_message
        self.pipeline.on_error = self._on_error

        # UI button -> Pipeline
        self.screen.on_press_button = self._handle_press
        self.screen.on_release_button = self._handle_release

        return self.screen

    def on_stop(self):
        if self.pipeline:
            self.pipeline.shutdown()

    # ------------------------------------------------------------------ #
    # Touch handlers (Kivy main thread)                                   #
    # ------------------------------------------------------------------ #

    def _handle_press(self):
        if not self.pipeline:
            return
        # start_recording is fast; safe on the main thread
        self.pipeline.start_recording()

    def _handle_release(self):
        if not self.pipeline:
            return
        if self._worker and self._worker.is_alive():
            log.warning("Pipeline busy — release ignored")
            return
        # stop_and_process is blocking; run in a worker thread
        self._worker = threading.Thread(
            target=self.pipeline.stop_and_process,
            daemon=True,
            name="pipeline-worker",
        )
        self._worker.start()

    # ------------------------------------------------------------------ #
    # Pipeline callbacks (worker thread) -> Kivy main thread              #
    # ------------------------------------------------------------------ #

    def _on_state_change(self, state: State):
        Clock.schedule_once(lambda _: self.screen.set_state(state), 0)

    def _on_message(self, role: str, text: str):
        Clock.schedule_once(lambda _: self.screen.add_message(role, text), 0)

    def _on_error(self, stage: str, message: str):
        Clock.schedule_once(lambda _: self.screen.show_error(stage, message), 0)

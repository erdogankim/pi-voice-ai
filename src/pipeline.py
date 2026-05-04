"""
pipeline.py — Push-to-talk pipeline shared by CLI and Kivy UI.

State machine per interaction:
  IDLE -> RECORDING -> TRANSCRIBING -> THINKING -> SPEAKING -> IDLE

The caller wires a button (or UI touch) to `start_recording()` /
`stop_and_process()`. The pipeline emits events through three callbacks:

  pipeline.on_state_change(new_state)   # State enum
  pipeline.on_message(role, text)       # role: "user" | "assistant"
  pipeline.on_error(stage, message)     # stage: "record"|"stt"|"ai"|"tts"

`stop_and_process()` does blocking work (STT, Claude, TTS, playback) and
must NOT be called from a UI main thread. The UI should dispatch it to a
worker thread; the CLI calls it from the keyboard daemon thread.
"""
import logging
import threading
from enum import Enum, auto
from typing import Callable, Optional

from src.audio_recorder import AudioRecorder
from src.stt_client import STTClient
from src.ai_client import AIClient
from src.tts_client import TTSClient
from src.audio_player import AudioPlayer
from src.history import ConversationHistory

log = logging.getLogger(__name__)


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    THINKING = auto()
    SPEAKING = auto()


STATE_LABELS = {
    State.IDLE:         "Hazır",
    State.RECORDING:    "Dinliyorum...",
    State.TRANSCRIBING: "Anlıyorum...",
    State.THINKING:     "Düşünüyorum...",
    State.SPEAKING:     "Konuşuyorum...",
}


def _noop(*_args, **_kwargs):
    pass


class Pipeline:
    def __init__(self, config):
        config.paths.data_dir.mkdir(parents=True, exist_ok=True)

        self.config = config
        self.recorder = AudioRecorder(config)
        self.stt = STTClient(config)
        self.ai = AIClient(config)
        self.tts = TTSClient(config)
        self.player = AudioPlayer()
        self.history = ConversationHistory(config)

        self.state: State = State.IDLE

        # Public callbacks — set by caller (CLI or UI)
        self.on_state_change: Callable[[State], None] = _noop
        self.on_message: Callable[[str, str], None] = _noop
        self.on_error: Callable[[str, str], None] = _noop

        self._max_timer: Optional[threading.Timer] = None

    # ------------------------------------------------------------------ #
    # State helpers                                                       #
    # ------------------------------------------------------------------ #

    def _set_state(self, new_state: State):
        self.state = new_state
        try:
            self.on_state_change(new_state)
        except Exception:
            log.exception("on_state_change handler raised")

    def _emit_message(self, role: str, text: str):
        try:
            self.on_message(role, text)
        except Exception:
            log.exception("on_message handler raised")

    def _emit_error(self, stage: str, message: str):
        log.error("Pipeline error in %s: %s", stage, message)
        try:
            self.on_error(stage, message)
        except Exception:
            log.exception("on_error handler raised")

    # ------------------------------------------------------------------ #
    # Public API                                                          #
    # ------------------------------------------------------------------ #

    def start_recording(self):
        """Begin recording. Must be in IDLE state."""
        if self.state != State.IDLE:
            log.warning("start_recording in state %s — ignored", self.state)
            return

        self._set_state(State.RECORDING)
        self.recorder.start_recording()

        # Auto-stop if max duration is exceeded
        self._max_timer = threading.Timer(
            self.config.audio.recording_max_seconds,
            self._auto_stop,
        )
        self._max_timer.daemon = True
        self._max_timer.start()

    def stop_and_process(self):
        """
        Stop recording, run STT -> Claude -> TTS -> playback.
        Blocking; do not call from a UI main thread.
        """
        if self._max_timer:
            self._max_timer.cancel()
            self._max_timer = None

        if self.state != State.RECORDING:
            log.warning("stop_and_process in state %s — ignored", self.state)
            return

        # --- TRANSCRIBING ---
        self._set_state(State.TRANSCRIBING)

        try:
            wav_path = self.recorder.stop_and_save()
        except Exception as e:
            self._emit_error("record", str(e))
            self._set_state(State.IDLE)
            return

        try:
            user_text = self.stt.transcribe(wav_path)
        except Exception as e:
            self._emit_error("stt", str(e))
            self._set_state(State.IDLE)
            return

        if not user_text:
            self._emit_error("stt", "Ses algılanamadı, tekrar deneyin.")
            self._set_state(State.IDLE)
            return

        self._emit_message("user", user_text)
        self.history.add("user", user_text)

        # --- THINKING ---
        self._set_state(State.THINKING)

        prior = self.history.get_messages(
            limit=self.config.ai.history_limit * 2 + 1
        )
        context = prior[:-1] if prior else []

        try:
            reply = self.ai.send_message(user_text, context)
        except Exception as e:
            self._emit_error("ai", str(e))
            self._set_state(State.IDLE)
            return

        self._emit_message("assistant", reply)
        self.history.add("assistant", reply)

        # --- SPEAKING ---
        self._set_state(State.SPEAKING)
        try:
            mp3_path = self.tts.synthesize(reply)
            self.player.play(mp3_path)
        except Exception as e:
            # Graceful degradation: text already delivered via on_message
            self._emit_error("tts", str(e))

        self._set_state(State.IDLE)

    def shutdown(self):
        """Cancel timers, close history, stop playback."""
        if self._max_timer:
            self._max_timer.cancel()
            self._max_timer = None
        try:
            self.player.stop()
        except Exception:
            pass
        self.history.close()

    # ------------------------------------------------------------------ #

    def _auto_stop(self):
        log.info("Recording max duration reached — auto-stopping")
        self.stop_and_process()

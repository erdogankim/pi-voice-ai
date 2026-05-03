"""
main.py — Pi Voice AI entry point.

State machine per interaction:
  IDLE -> RECORDING -> TRANSCRIBING -> THINKING -> SPEAKING -> IDLE

Usage:
  python src/main.py --no-ui     # CLI mode (Phase 2)
  python src/main.py             # UI mode (Phase 3, not yet implemented)

Headless audio on Pi (no pulseaudio):
  export SDL_AUDIODRIVER=alsa
"""
import sys
import os
import argparse
import logging
import signal
import threading
from enum import Enum, auto
from pathlib import Path

# Allow running as `python src/main.py` from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set SDL audio driver hint before pygame is imported inside AudioPlayer
os.environ.setdefault("SDL_AUDIODRIVER", "alsa")

from src.config import load_config
from src.button_handler import ButtonHandler
from src.audio_recorder import AudioRecorder
from src.stt_client import STTClient
from src.ai_client import AIClient
from src.tts_client import TTSClient
from src.audio_player import AudioPlayer
from src.history import ConversationHistory


class State(Enum):
    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    THINKING = auto()
    SPEAKING = auto()


_STATE_LABELS = {
    State.IDLE:         "Hazir     — butona basin (Enter)",
    State.RECORDING:    "Dinliyorum...",
    State.TRANSCRIBING: "Anliyorum...",
    State.THINKING:     "Dusunuyorum...",
    State.SPEAKING:     "Konusuyorum...",
}


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def print_status(state: State, extra: str = ""):
    label = _STATE_LABELS.get(state, state.name)
    suffix = f" — {extra}" if extra else ""
    print(f"\n[{state.name}] {label}{suffix}", flush=True)


def run_cli(config):
    config.paths.data_dir.mkdir(parents=True, exist_ok=True)

    button   = ButtonHandler(config)
    recorder = AudioRecorder(config)
    stt      = STTClient(config)
    ai       = AIClient(config)
    tts      = TTSClient(config)
    player   = AudioPlayer()
    history  = ConversationHistory(config)

    log = logging.getLogger("main")
    state = State.IDLE
    _max_timer: threading.Timer | None = None

    def on_release():
        nonlocal state, _max_timer

        # Cancel auto-stop timer if it fired before button release
        if _max_timer:
            _max_timer.cancel()
            _max_timer = None

        if state != State.RECORDING:
            log.warning("on_release in unexpected state %s — ignoring", state)
            return

        button.set_led(False)

        # --- TRANSCRIBING ---
        state = State.TRANSCRIBING
        print_status(state)

        try:
            wav_path = recorder.stop_and_save()
        except Exception as e:
            log.error("Recording error: %s", e)
            print(f"[HATA] Kayit hatasi: {e}")
            state = State.IDLE
            print_status(State.IDLE)
            return

        try:
            user_text = stt.transcribe(wav_path)
        except Exception as e:
            log.error("STT error: %s", e)
            print(f"[HATA] Sesi anlayamadim: {e}")
            state = State.IDLE
            print_status(State.IDLE)
            return

        if not user_text:
            print("[BILGI] Ses algilanamaadi, tekrar deneyin.")
            state = State.IDLE
            print_status(State.IDLE)
            return

        print(f"\nSiz: {user_text}")
        history.add("user", user_text)

        # --- THINKING ---
        state = State.THINKING
        print_status(state)

        # Pass prior turns (excluding the one we just added)
        prior = history.get_messages(limit=config.ai.history_limit * 2 + 1)
        context = prior[:-1] if prior else []

        try:
            reply = ai.send_message(user_text, context)
        except Exception as e:
            log.error("Claude error: %s", e)
            print(f"[HATA] Cevap alinamaadi: {e}")
            state = State.IDLE
            print_status(State.IDLE)
            return

        print(f"\nAsistan: {reply}")
        history.add("assistant", reply)

        # --- SPEAKING ---
        state = State.SPEAKING
        print_status(state)

        try:
            mp3_path = tts.synthesize(reply)
            player.play(mp3_path)
        except Exception as e:
            log.error("TTS/playback error: %s", e)
            print(f"[UYARI] Ses calinamaadi: {e}")
            # Graceful degradation: text already printed above

        state = State.IDLE
        print_status(State.IDLE)

    def on_press():
        nonlocal state, _max_timer
        if state != State.IDLE:
            log.warning("on_press in state %s — ignoring", state)
            return

        state = State.RECORDING
        print_status(state)
        button.set_led(True)
        recorder.start_recording()

        # Auto-stop if max duration reached without button release
        _max_timer = threading.Timer(config.audio.recording_max_seconds, on_release)
        _max_timer.daemon = True
        _max_timer.start()

    button.on_press   = on_press
    button.on_release = on_release

    def shutdown(signum=None, frame=None):
        print("\n[INFO] Kapaniyor...")
        button.stop()
        history.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    button.start()
    print_status(State.IDLE)
    print("[INFO] Cikis icin Ctrl+C\n")

    # Keep main thread alive — events arrive on daemon/GPIO threads
    try:
        signal.pause()          # Unix / Pi
    except AttributeError:
        import time
        while True:             # Windows fallback
            time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(description="Pi Voice AI")
    parser.add_argument("--no-ui", action="store_true",
                        help="CLI modu (Kivy UI olmadan)")
    parser.add_argument("--config", default=None,
                        help="config.yaml yolu (varsayilan: config/config.yaml)")
    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config.log_level)

    if args.no_ui:
        run_cli(config)
    else:
        print("[BILGI] UI modu henuz uygulanmadi. --no-ui kullanin.")
        sys.exit(1)


if __name__ == "__main__":
    main()

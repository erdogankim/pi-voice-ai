"""
main.py — Pi Voice AI entry point.

Usage:
  python src/main.py             # Kivy UI mode (Phase 3)
  python src/main.py --no-ui     # CLI mode (Phase 2)

Headless audio on Pi (no pulseaudio):
  export SDL_AUDIODRIVER=alsa
"""
import sys
import os
import platform
import argparse
import logging
import signal
from pathlib import Path

# Allow running as `python src/main.py` from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set SDL audio driver hint before pygame is imported inside AudioPlayer.
# - On Pi / Linux without pulseaudio: alsa
# - On Windows: directsound (alsa would fail with "Audio target not available")
# - User can override with the env var before launching.
if "SDL_AUDIODRIVER" not in os.environ:
    if platform.system() == "Windows":
        os.environ["SDL_AUDIODRIVER"] = "directsound"
    else:
        os.environ["SDL_AUDIODRIVER"] = "alsa"

from src.config import load_config
from src.button_handler import ButtonHandler
from src.pipeline import Pipeline, State, STATE_LABELS


def setup_logging(level: str):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def run_cli(config):
    pipeline = Pipeline(config)
    button = ButtonHandler(config)

    def print_state(state: State):
        label = STATE_LABELS.get(state, state.name)
        print(f"\n[{state.name}] {label}", flush=True)

    def print_message(role: str, text: str):
        prefix = "Siz" if role == "user" else "Asistan"
        print(f"\n{prefix}: {text}")

    def print_error(stage: str, message: str):
        print(f"[HATA] ({stage}) {message}")

    pipeline.on_state_change = print_state
    pipeline.on_message = print_message
    pipeline.on_error = print_error

    button.on_press = pipeline.start_recording
    button.on_release = pipeline.stop_and_process

    def shutdown(signum=None, frame=None):
        print("\n[INFO] Kapanıyor...")
        button.stop()
        pipeline.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    button.start()
    print_state(State.IDLE)
    print("[INFO] Çıkış için Ctrl+C\n")

    try:
        signal.pause()          # Unix / Pi
    except AttributeError:
        import time
        while True:             # Windows fallback
            time.sleep(0.1)


def run_ui(config):
    # Lazy import so CLI mode doesn't pay Kivy startup cost
    from src.ui.app import PiVoiceApp
    PiVoiceApp(config).run()


def main():
    parser = argparse.ArgumentParser(description="Pi Voice AI")
    parser.add_argument("--no-ui", action="store_true",
                        help="CLI modu (Kivy UI olmadan)")
    parser.add_argument("--config", default=None,
                        help="config.yaml yolu (varsayılan: config/config.yaml)")
    args = parser.parse_args()

    config = load_config(Path(args.config) if args.config else None)
    setup_logging(config.log_level)

    if args.no_ui:
        run_cli(config)
    else:
        run_ui(config)


if __name__ == "__main__":
    main()

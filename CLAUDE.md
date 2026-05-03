# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pi Voice AI is a push-to-talk AI assistant running on Raspberry Pi 4. The user holds a physical button, speaks Turkish, and the device transcribes via OpenAI Whisper, gets a response from Anthropic Claude, and plays it back via OpenAI TTS — all shown on a Kivy touchscreen UI.

**Current status: Phase 0 (planning) complete. No `src/` code exists yet** — the next step is building the CLI prototype (Phase 2).

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # add ANTHROPIC_API_KEY and OPENAI_API_KEY
```

## Running

```bash
python src/main.py          # Full UI mode (Kivy)
python src/main.py --no-ui  # CLI-only mode (Phase 2 target)
```

## Testing

```bash
pytest                          # all tests
pytest tests/test_audio.py      # single test file
pytest tests/test_api.py -v     # verbose
```

## Linting / Formatting

```bash
black src/ tests/
```

## Architecture

The pipeline is linear and event-driven:

```
[GPIO Button press] → [sounddevice recording] → [OpenAI Whisper STT]
  → [Anthropic Claude] → [OpenAI TTS] → [pygame audio playback]
                       ↕
                  [Kivy UI] (status display + conversation history)
```

### Planned modules (`src/`)

| File | Responsibility |
|---|---|
| `main.py` | Entry point; wires all modules together |
| `button_handler.py` | `gpiozero` Button on GPIO 17, LED on GPIO 27 |
| `audio_recorder.py` | `sounddevice` + `numpy` → saves `kayit.wav` |
| `stt_client.py` | OpenAI Whisper (`whisper-1`, `language="tr"`) |
| `ai_client.py` | Anthropic Claude (`claude-sonnet-4-5`, multi-turn history) |
| `tts_client.py` | OpenAI TTS (`tts-1`, voice configurable) |
| `audio_player.py` | `pygame.mixer` plays the TTS mp3 |
| `history.py` | `sqlite3` local conversation history |
| `config.py` | Loads `config/config.yaml` + `.env` via `python-dotenv` |
| `ui/app.py` | Kivy application root |
| `ui/screens.py` | Main screen: status indicator + scrolling history |
| `ui/theme.py` | Dark/light theme constants |

### Configuration

- **`config/config.yaml`** — all tunable settings (model, voice, GPIO pins, UI theme). Committed to git.
- **`.env`** — API keys only. Never committed. Copy from `.env.example`.

Key config values:
- `ai.model`: `claude-sonnet-4-5`
- `button.gpio_pin`: `17` (GND on Pin 9; LED on GPIO 27)
- `audio.sample_rate`: `16000`, mono
- `stt.language`: `"tr"` — must always be set for Turkish accuracy

### State machine (per interaction)

`IDLE → RECORDING → TRANSCRIBING → THINKING → SPEAKING → IDLE`

Each state maps to a UI status label: "Dinliyorum / Anlıyorum / Düşünüyorum / Konuşuyorum"

### Error handling

- No Wi-Fi → disable button, show message
- Whisper / Claude / TTS API error → show error on screen; TTS failures fall back to text-only display
- Missing microphone → warn on startup, block recording

## Target Platform

- **Raspberry Pi 4 Model B (4GB)**, Raspberry Pi OS Bookworm (64-bit)
- **Python 3.11+**
- `gpiozero` and `RPi.GPIO` are only installed on ARM (`armv7l` / `aarch64`) — guard GPIO calls accordingly when developing on x86

## systemd Service

```bash
sudo cp scripts/pi-voice-ai.service /etc/systemd/system/
sudo systemctl enable --now pi-voice-ai
journalctl -u pi-voice-ai -f   # live logs
```

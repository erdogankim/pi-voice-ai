"""
config.py — Loads config/config.yaml + .env, exposes a Config dataclass.

All paths are resolved relative to the project root (parent of src/).
API keys come exclusively from environment variables, never from yaml.
"""
import os
import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

import yaml
from dotenv import load_dotenv

log = logging.getLogger(__name__)

SRC_DIR = Path(__file__).parent
PROJECT_ROOT = SRC_DIR.parent


@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    recording_max_seconds: int = 30
    dtype: str = "float32"


@dataclass
class AIConfig:
    model: str = "claude-sonnet-4-5"
    max_tokens: int = 1024
    system_prompt: str = "Sen yardimci bir asistansin."
    history_limit: int = 20


@dataclass
class STTConfig:
    model: str = "whisper-1"
    language: str = "tr"


@dataclass
class TTSConfig:
    model: str = "tts-1"
    voice: str = "alloy"
    speed: float = 1.0


@dataclass
class ButtonConfig:
    gpio_pin: int = 17
    led_pin: int = 27
    mode: str = "hold"


@dataclass
class PathsConfig:
    data_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "data")
    history_db: Path = field(default_factory=lambda: PROJECT_ROOT / "data" / "history.db")


@dataclass
class Config:
    audio: AudioConfig = field(default_factory=AudioConfig)
    ai: AIConfig = field(default_factory=AIConfig)
    stt: STTConfig = field(default_factory=STTConfig)
    tts: TTSConfig = field(default_factory=TTSConfig)
    button: ButtonConfig = field(default_factory=ButtonConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    log_level: str = "INFO"


def _apply(dataclass_instance, raw_dict: dict):
    """Return a new instance with fields from raw_dict that exist in the dataclass."""
    fields = dataclass_instance.__class__.__dataclass_fields__
    kwargs = {k: v for k, v in raw_dict.items() if k in fields}
    return dataclass_instance.__class__(**{
        **{f: getattr(dataclass_instance, f) for f in fields},
        **kwargs,
    })


def load_config(config_file: Optional[Path] = None) -> Config:
    """Load config.yaml + .env and return a populated Config instance."""
    load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

    if config_file is None:
        config_file = PROJECT_ROOT / "config" / "config.yaml"

    raw: dict = {}
    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    else:
        log.warning("config.yaml not found at %s — using defaults", config_file)

    paths_raw = raw.get("paths", {})
    data_dir = PROJECT_ROOT / paths_raw.get("data_dir", "data")
    history_db = PROJECT_ROOT / paths_raw.get("history_db", "data/history.db")

    cfg = Config(
        audio=_apply(AudioConfig(), raw.get("audio", {})),
        ai=_apply(AIConfig(), raw.get("ai", {})),
        stt=_apply(STTConfig(), raw.get("stt", {})),
        tts=_apply(TTSConfig(), raw.get("tts", {})),
        button=_apply(ButtonConfig(), raw.get("button", {})),
        paths=PathsConfig(data_dir=data_dir, history_db=history_db),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )

    if not cfg.anthropic_api_key:
        log.warning("ANTHROPIC_API_KEY is not set")
    if not cfg.openai_api_key:
        log.warning("OPENAI_API_KEY is not set")

    return cfg

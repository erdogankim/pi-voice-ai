"""
tts_client.py — OpenAI TTS client. Converts text to an mp3 file.
"""
import logging
from pathlib import Path

from openai import OpenAI

log = logging.getLogger(__name__)


class TTSClient:
    def __init__(self, config):
        self._cfg = config.tts
        self._data_dir = config.paths.data_dir
        self._client = OpenAI(api_key=config.openai_api_key)
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str) -> Path:
        """Convert text to speech, save as data/cevap.mp3, return Path."""
        out_path = self._data_dir / "cevap.mp3"
        log.info("TTS: model=%s voice=%s speed=%.1f len=%d chars",
                 self._cfg.model, self._cfg.voice, self._cfg.speed, len(text))
        response = self._client.audio.speech.create(
            model=self._cfg.model,
            voice=self._cfg.voice,
            input=text,
            speed=self._cfg.speed,
            response_format="mp3",
        )
        response.write_to_file(str(out_path))
        log.info("TTS saved to %s", out_path)
        return out_path

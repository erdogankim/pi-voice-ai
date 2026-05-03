"""
stt_client.py — OpenAI Whisper speech-to-text client.
"""
import logging
from pathlib import Path

from openai import OpenAI

log = logging.getLogger(__name__)


class STTClient:
    def __init__(self, config):
        self._cfg = config.stt
        self._client = OpenAI(api_key=config.openai_api_key)

    def transcribe(self, audio_path: Path) -> str:
        """Transcribe audio file. Returns stripped text."""
        log.info("Transcribing %s (model=%s language=%s)",
                 audio_path, self._cfg.model, self._cfg.language)
        with open(audio_path, "rb") as f:
            response = self._client.audio.transcriptions.create(
                model=self._cfg.model,
                file=f,
                language=self._cfg.language,
            )
        text = response.text.strip()
        log.info("Transcription: %r", text)
        return text

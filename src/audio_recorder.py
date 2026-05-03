"""
audio_recorder.py — Push-to-talk audio recorder using sounddevice.

Usage:
  recorder = AudioRecorder(config)
  recorder.start_recording()   # non-blocking
  path = recorder.stop_and_save()  # returns Path to .wav file
"""
import logging
import time
from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
import soundfile as sf

log = logging.getLogger(__name__)


class AudioRecorder:
    def __init__(self, config):
        self._cfg = config.audio
        self._data_dir = config.paths.data_dir
        self._frames: list = []
        self._stream: Optional[sd.InputStream] = None
        self._recording = False
        self._start_time: float = 0.0
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def start_recording(self):
        if self._recording:
            log.warning("Already recording — ignoring start_recording()")
            return
        self._frames = []
        self._recording = True
        self._start_time = time.monotonic()
        self._stream = sd.InputStream(
            samplerate=self._cfg.sample_rate,
            channels=self._cfg.channels,
            dtype=self._cfg.dtype,
            callback=self._callback,
        )
        self._stream.start()
        log.info("Recording started (max %ds, %dHz, %dch)",
                 self._cfg.recording_max_seconds, self._cfg.sample_rate, self._cfg.channels)

    def stop_and_save(self) -> Path:
        """Stop recording and write to data/kayit.wav. Returns Path."""
        if not self._recording:
            log.warning("stop_and_save() called while not recording")
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        elapsed = time.monotonic() - self._start_time
        log.info("Recording stopped after %.1fs, %d chunks captured", elapsed, len(self._frames))

        if self._frames:
            audio_data = np.concatenate(self._frames, axis=0)
        else:
            log.warning("No audio frames — saving silence")
            audio_data = np.zeros(
                (self._cfg.sample_rate, self._cfg.channels), dtype=self._cfg.dtype
            )

        out_path = self._data_dir / "kayit.wav"
        sf.write(str(out_path), audio_data, self._cfg.sample_rate)
        log.info("Saved to %s (%.1fs)", out_path, elapsed)
        return out_path

    def is_recording(self) -> bool:
        return self._recording

    def elapsed_seconds(self) -> float:
        if not self._recording:
            return 0.0
        return time.monotonic() - self._start_time

    def _callback(self, indata: np.ndarray, frames: int, time_info, status):
        if status:
            log.warning("sounddevice status: %s", status)
        if self._recording:
            self._frames.append(indata.copy())

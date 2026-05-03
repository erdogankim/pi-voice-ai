"""Tests for AudioRecorder."""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from pathlib import Path


def make_config(tmp_path):
    from src.config import load_config
    cfg = load_config()
    cfg.paths.data_dir = tmp_path / "data"
    cfg.paths.history_db = tmp_path / "data" / "history.db"
    return cfg


def test_recorder_creates_data_dir(tmp_path):
    cfg = make_config(tmp_path)
    with patch("sounddevice.InputStream"):
        from src.audio_recorder import AudioRecorder
        AudioRecorder(cfg)
    assert cfg.paths.data_dir.exists()


def test_stop_without_frames_saves_silence(tmp_path):
    cfg = make_config(tmp_path)
    from src.audio_recorder import AudioRecorder
    with patch("sounddevice.InputStream"):
        recorder = AudioRecorder(cfg)
        path = recorder.stop_and_save()
    assert path.exists()
    assert path.suffix == ".wav"


def test_stop_with_frames_saves_audio(tmp_path):
    cfg = make_config(tmp_path)
    from src.audio_recorder import AudioRecorder
    with patch("sounddevice.InputStream"):
        recorder = AudioRecorder(cfg)
        # Simulate captured frames
        recorder._frames = [
            np.zeros((1600, 1), dtype="float32"),
            np.zeros((1600, 1), dtype="float32"),
        ]
        path = recorder.stop_and_save()
    assert path.exists()

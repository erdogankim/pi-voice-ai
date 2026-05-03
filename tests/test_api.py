"""Unit tests for API clients — all external calls are mocked."""
import pytest
from unittest.mock import MagicMock, patch, call
from pathlib import Path


def make_config(tmp_path=None):
    from src.config import load_config
    cfg = load_config()
    cfg.anthropic_api_key = "test-anthropic-key"
    cfg.openai_api_key = "test-openai-key"
    if tmp_path:
        cfg.paths.data_dir = tmp_path
        cfg.paths.history_db = tmp_path / "history.db"
    return cfg


# ------------------------------------------------------------------ #
# STTClient                                                            #
# ------------------------------------------------------------------ #

def test_stt_transcribes_and_strips(tmp_path):
    cfg = make_config(tmp_path)
    mock_resp = MagicMock()
    mock_resp.text = "  Merhaba dunya  "

    with patch("src.stt_client.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.audio.transcriptions.create.return_value = mock_resp
        from src.stt_client import STTClient
        client = STTClient(cfg)
        wav = tmp_path / "test.wav"
        wav.write_bytes(b"RIFF" + b"\x00" * 36)
        result = client.transcribe(wav)

    assert result == "Merhaba dunya"


def test_stt_passes_language(tmp_path):
    cfg = make_config(tmp_path)
    cfg.stt.language = "tr"
    mock_resp = MagicMock()
    mock_resp.text = "test"

    with patch("src.stt_client.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.audio.transcriptions.create.return_value = mock_resp
        from src.stt_client import STTClient
        client = STTClient(cfg)
        wav = tmp_path / "test.wav"
        wav.write_bytes(b"RIFF" + b"\x00" * 36)
        client.transcribe(wav)

    kwargs = instance.audio.transcriptions.create.call_args.kwargs
    assert kwargs["language"] == "tr"


# ------------------------------------------------------------------ #
# AIClient                                                             #
# ------------------------------------------------------------------ #

def test_ai_client_appends_user_message():
    cfg = make_config()
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="Cevap")]

    with patch("src.ai_client.Anthropic") as MockAnthro:
        MockAnthro.return_value.messages.create.return_value = mock_resp
        from src.ai_client import AIClient
        client = AIClient(cfg)
        client.send_message("Soru", history=[])

    sent = MockAnthro.return_value.messages.create.call_args.kwargs["messages"]
    assert sent == [{"role": "user", "content": "Soru"}]


def test_ai_client_trims_history_to_limit():
    cfg = make_config()
    cfg.ai.history_limit = 2  # keep only 2 pairs
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="ok")]

    history = []
    for i in range(5):
        history.append({"role": "user", "content": f"soru{i}"})
        history.append({"role": "assistant", "content": f"cevap{i}"})

    with patch("src.ai_client.Anthropic") as MockAnthro:
        MockAnthro.return_value.messages.create.return_value = mock_resp
        from src.ai_client import AIClient
        client = AIClient(cfg)
        client.send_message("yeni", history)

    sent = MockAnthro.return_value.messages.create.call_args.kwargs["messages"]
    # 2 pairs (4 msgs) trimmed from history + 1 current = 5
    assert len(sent) == 5
    assert sent[-1] == {"role": "user", "content": "yeni"}


def test_ai_client_strips_leading_assistant():
    cfg = make_config()
    mock_resp = MagicMock()
    mock_resp.content = [MagicMock(text="ok")]

    # History that starts with assistant (corrupted)
    history = [
        {"role": "assistant", "content": "orphan"},
        {"role": "user", "content": "soru"},
        {"role": "assistant", "content": "cevap"},
    ]

    with patch("src.ai_client.Anthropic") as MockAnthro:
        MockAnthro.return_value.messages.create.return_value = mock_resp
        from src.ai_client import AIClient
        client = AIClient(cfg)
        client.send_message("yeni", history)

    sent = MockAnthro.return_value.messages.create.call_args.kwargs["messages"]
    assert sent[0]["role"] == "user"


# ------------------------------------------------------------------ #
# TTSClient                                                            #
# ------------------------------------------------------------------ #

def test_tts_calls_write_to_file(tmp_path):
    cfg = make_config(tmp_path)
    mock_resp = MagicMock()

    with patch("src.tts_client.OpenAI") as MockOpenAI:
        MockOpenAI.return_value.audio.speech.create.return_value = mock_resp
        from src.tts_client import TTSClient
        client = TTSClient(cfg)
        path = client.synthesize("Merhaba")

    mock_resp.write_to_file.assert_called_once()
    assert path.name == "cevap.mp3"


def test_tts_passes_correct_params(tmp_path):
    cfg = make_config(tmp_path)
    cfg.tts.voice = "nova"
    cfg.tts.speed = 1.2
    mock_resp = MagicMock()

    with patch("src.tts_client.OpenAI") as MockOpenAI:
        instance = MockOpenAI.return_value
        instance.audio.speech.create.return_value = mock_resp
        from src.tts_client import TTSClient
        client = TTSClient(cfg)
        client.synthesize("test")

    kwargs = instance.audio.speech.create.call_args.kwargs
    assert kwargs["voice"] == "nova"
    assert kwargs["speed"] == 1.2

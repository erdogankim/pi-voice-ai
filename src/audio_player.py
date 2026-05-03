"""
audio_player.py — pygame.mixer based audio playback.

Only pygame.mixer is initialized (not pygame.display) to avoid
SDL_VIDEODRIVER errors on headless systems.

On headless Linux / Pi without pulseaudio:
  Set SDL_AUDIODRIVER=alsa before importing this module, or export it
  in the shell:  export SDL_AUDIODRIVER=alsa
"""
import logging
import os
import time
from pathlib import Path

log = logging.getLogger(__name__)

_mixer_ready = False


def _ensure_mixer():
    global _mixer_ready
    if _mixer_ready:
        return
    import pygame
    try:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.init()
        _mixer_ready = True
        log.info("pygame.mixer initialized")
    except pygame.error as e:
        log.error("pygame.mixer init failed: %s", e)
        raise


class AudioPlayer:
    def __init__(self):
        _ensure_mixer()

    def play(self, mp3_path) -> None:
        """Play mp3 synchronously — blocks until playback finishes."""
        import pygame
        path = Path(mp3_path)
        if not path.exists():
            log.error("Audio file not found: %s", path)
            return
        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play()
            log.info("Playing %s", path.name)
            while pygame.mixer.music.get_busy():
                time.sleep(0.05)
            log.info("Playback complete")
        except pygame.error as e:
            log.error("Playback error: %s", e)
            raise

    def stop(self):
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

    def set_volume(self, volume: float):
        import pygame
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

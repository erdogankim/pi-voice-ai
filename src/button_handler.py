"""
button_handler.py — GPIO button on Pi; keyboard (Enter) fallback on x86/Windows.

On Raspberry Pi (armv7l / aarch64):
  Uses gpiozero.Button(gpio_pin) + LED(led_pin) with real GPIO.

On x86 / Windows (development):
  Uses gpiozero with MockFactory (no real GPIO).
  A daemon thread reads stdin — pressing Enter simulates press/release.

Public API:
  handler = ButtonHandler(config)
  handler.on_press   = callable()
  handler.on_release = callable()
  handler.start()
  handler.stop()
  handler.set_led(state: bool)
"""
import platform
import logging
import threading
from typing import Optional, Callable

log = logging.getLogger(__name__)

IS_PI = platform.machine() in ("armv7l", "aarch64")


class ButtonHandler:
    def __init__(self, config):
        self._cfg = config.button
        self._mode = self._cfg.mode
        self._on_press: Optional[Callable] = None
        self._on_release: Optional[Callable] = None
        self._toggle_held = False
        self._button = None
        self._led = None
        self._factory = None
        self._running = False
        self._kb_thread: Optional[threading.Thread] = None

    @property
    def on_press(self):
        return self._on_press

    @on_press.setter
    def on_press(self, fn: Callable):
        self._on_press = fn

    @property
    def on_release(self):
        return self._on_release

    @on_release.setter
    def on_release(self, fn: Callable):
        self._on_release = fn

    def start(self):
        self._running = True
        if IS_PI:
            self._start_gpio()
        else:
            self._start_mock()

    def stop(self):
        self._running = False
        if self._button:
            self._button.close()
        if self._led:
            self._led.close()
        if self._factory:
            self._factory.close()

    def set_led(self, state: bool):
        if self._led:
            self._led.on() if state else self._led.off()

    # ------------------------------------------------------------------ #

    def _handle_press(self):
        if self._mode == "toggle":
            if not self._toggle_held:
                self._toggle_held = True
                if self._on_press:
                    self._on_press()
            else:
                self._toggle_held = False
                if self._on_release:
                    self._on_release()
        else:  # hold
            if self._on_press:
                self._on_press()

    def _handle_release(self):
        if self._mode == "hold":
            if self._on_release:
                self._on_release()

    def _start_gpio(self):
        from gpiozero import Button, LED
        self._button = Button(self._cfg.gpio_pin, pull_up=True)
        self._led = LED(self._cfg.led_pin)
        self._button.when_pressed = self._handle_press
        if self._mode == "hold":
            self._button.when_released = self._handle_release
        log.info("GPIO button pin=%d LED pin=%d mode=%s",
                 self._cfg.gpio_pin, self._cfg.led_pin, self._mode)

    def _start_mock(self):
        from gpiozero import Device, Button, LED
        from gpiozero.pins.mock import MockFactory
        self._factory = MockFactory()
        Device.pin_factory = self._factory
        self._button = Button(self._cfg.gpio_pin, pin_factory=self._factory)
        self._led = LED(self._cfg.led_pin, pin_factory=self._factory)
        log.info("Mock button (keyboard) pin=%d mode=%s", self._cfg.gpio_pin, self._mode)
        print("[MOCK] Klavye modu aktif. Enter = bas / tekrar Enter = birak. Ctrl+C = cikis.")
        self._kb_thread = threading.Thread(target=self._keyboard_loop, daemon=True)
        self._kb_thread.start()

    def _keyboard_loop(self):
        held = False
        while self._running:
            try:
                input()
            except EOFError:
                break
            if not held:
                held = True
                log.debug("Mock: button pressed")
                self._handle_press()
                if self._mode == "hold":
                    print("[MOCK] Kayit yapiliyor... tekrar Enter = birak")
            else:
                if self._mode == "hold":
                    held = False
                    log.debug("Mock: button released")
                    self._handle_release()
                else:
                    held = False

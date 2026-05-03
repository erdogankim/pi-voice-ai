"""
ai_client.py — Anthropic Claude client with multi-turn conversation history.

History trimming:
  - Receives the full prior history from the caller.
  - Trims to the last history_limit pairs (user+assistant) before sending.
  - Enforces the alternating user/assistant invariant required by the API.
"""
import logging
from typing import List, Dict

from anthropic import Anthropic

log = logging.getLogger(__name__)


class AIClient:
    def __init__(self, config):
        self._cfg = config.ai
        self._client = Anthropic(api_key=config.anthropic_api_key)

    def send_message(self, user_text: str, history: List[Dict[str, str]]) -> str:
        """
        Send user_text to Claude with conversation history.

        Args:
            user_text: The new user message.
            history:   Prior turns as [{"role": "user"|"assistant", "content": str}].
                       Should NOT include the current user_text — it is appended here.

        Returns:
            Assistant reply text.
        """
        # Trim to last N complete pairs (2 messages per pair)
        trimmed = history[-(self._cfg.history_limit * 2):]

        # API requires messages to start with "user"
        while trimmed and trimmed[0]["role"] != "user":
            trimmed = trimmed[1:]

        messages = trimmed + [{"role": "user", "content": user_text}]

        log.info("Claude request: model=%s, %d messages (%d history)",
                 self._cfg.model, len(messages), len(trimmed))

        response = self._client.messages.create(
            model=self._cfg.model,
            max_tokens=self._cfg.max_tokens,
            system=self._cfg.system_prompt,
            messages=messages,
        )
        reply = response.content[0].text.strip()
        log.info("Claude reply: %r", reply[:100])
        return reply

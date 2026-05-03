"""
history.py — SQLite-backed conversation history.

Each process run gets a unique session UUID. History for the current
session is what gets passed to Claude; all sessions are stored in the
DB for future UI display.
"""
import sqlite3
import uuid
import logging
from typing import List, Dict

log = logging.getLogger(__name__)

CURRENT_SESSION = str(uuid.uuid4())


class ConversationHistory:
    def __init__(self, config):
        self._db_path = config.paths.history_db
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._create_table()
        log.info("History DB: %s  session=%s", self._db_path, CURRENT_SESSION[:8])

    def _create_table(self):
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                session    TEXT NOT NULL,
                role       TEXT NOT NULL,
                content    TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._conn.commit()

    def add(self, role: str, content: str):
        """Append a message to the current session."""
        self._conn.execute(
            "INSERT INTO conversations (session, role, content) VALUES (?, ?, ?)",
            (CURRENT_SESSION, role, content),
        )
        self._conn.commit()

    def get_messages(self, limit: int = 200) -> List[Dict[str, str]]:
        """
        Return up to `limit` messages from the current session, oldest first.
        Suitable for passing directly to AIClient.send_message() as history.
        """
        rows = self._conn.execute(
            """
            SELECT role, content FROM conversations
            WHERE session = ?
            ORDER BY id DESC LIMIT ?
            """,
            (CURRENT_SESSION, limit),
        ).fetchall()
        return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

    def close(self):
        self._conn.close()

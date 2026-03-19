import sqlite3
import os


class EventDB:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else ".", exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                event_type TEXT NOT NULL,
                state_from TEXT,
                state_to TEXT,
                sensor TEXT,
                details TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
            CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
        """)
        self.conn.commit()

    def log_event(self, event_type: str, state_from: str = None,
                  state_to: str = None, sensor: str = None, details: str = None):
        self.conn.execute(
            "INSERT INTO events (event_type, state_from, state_to, sensor, details) VALUES (?, ?, ?, ?, ?)",
            (event_type, state_from, state_to, sensor, details),
        )
        self.conn.commit()

    def get_recent_events(self, limit: int = 50) -> list[dict]:
        cursor = self.conn.execute(
            "SELECT * FROM events ORDER BY id DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_daily_alarm_count(self) -> int:
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM events
            WHERE event_type = 'state_change' AND state_to = 'ALARM'
            AND date(timestamp) = date('now', 'localtime')
        """)
        return cursor.fetchone()[0]

    def close(self):
        self.conn.close()

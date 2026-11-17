"""SQLite persistence. Stores routing + status only — never message text."""
from __future__ import annotations

import sqlite3
import time

KIND_LETTER = {"counseling": "C", "booking": "A", "prayer": "P", "testimony": "T"}

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    lang        TEXT,
    last_submit REAL NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tickets (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    kind      TEXT    NOT NULL,
    user_id   INTEGER NOT NULL,
    created   REAL    NOT NULL,
    root_msg  INTEGER
);
CREATE TABLE IF NOT EXISTS admin_msgs (
    msg_id    INTEGER PRIMARY KEY,
    ticket_id INTEGER NOT NULL
);
"""

# Columns added in v2 — applied automatically to databases created by v1.
MIGRATIONS = {
    "users": {
        "onboarded": "INTEGER NOT NULL DEFAULT 0",
        "verse_sub": "INTEGER NOT NULL DEFAULT 0",
        "created": "REAL",
    },
    "tickets": {
        "topic": "TEXT",
        "status": "TEXT NOT NULL DEFAULT 'open'",
        "urgent": "INTEGER NOT NULL DEFAULT 0",
        "rating": "INTEGER",
        "updated": "REAL",
        "claimed_by": "TEXT",
    },
}


def label(kind: str, ticket_id: int) -> str:
    return f"#{KIND_LETTER[kind]}{ticket_id:04d}"


class DB:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        for table, cols in MIGRATIONS.items():
            have = {r["name"] for r in self.conn.execute(f"PRAGMA table_info({table})")}
            for col, ddl in cols.items():
                if col not in have:
                    self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {ddl}")
        self.conn.commit()

    # ------------------------------------------------------------------ users
    def user(self, user_id: int):
        return self.conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()

    def get_lang(self, user_id: int) -> str | None:
        row = self.user(user_id)
        return row["lang"] if row else None

    def set_lang(self, user_id: int, lang: str) -> None:
        self.conn.execute(
            "INSERT INTO users(user_id, lang, created) VALUES(?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang=excluded.lang",
            (user_id, lang, time.time()),
        )
        self.conn.commit()

    def set_onboarded(self, user_id: int) -> None:
        self.conn.execute("UPDATE users SET onboarded=1 WHERE user_id=?", (user_id,))
        self.conn.commit()

    def set_verse_sub(self, user_id: int, on: bool) -> None:
        self.conn.execute("UPDATE users SET verse_sub=? WHERE user_id=?", (int(on), user_id))
        self.conn.commit()

    def verse_subscribers(self) -> list[tuple[int, str]]:
        rows = self.conn.execute("SELECT user_id, COALESCE(lang,'en') lang FROM users WHERE verse_sub=1").fetchall()
        return [(r["user_id"], r["lang"]) for r in rows]

    def seconds_since_submit(self, user_id: int) -> float:
        row = self.user(user_id)
        return time.time() - (row["last_submit"] if row else 0)

    def touch_submit(self, user_id: int) -> None:
        self.conn.execute("UPDATE users SET last_submit=? WHERE user_id=?", (time.time(), user_id))
        self.conn.commit()

    def delete_user(self, user_id: int) -> None:
        """Erase the person and sever every ticket from them (counselors can no longer reach them)."""
        self.conn.execute("UPDATE tickets SET user_id=0, status='closed', updated=? WHERE user_id=?", (time.time(), user_id))
        self.conn.execute("DELETE FROM users WHERE user_id=?", (user_id,))
        self.conn.commit()

    # ---------------------------------------------------------------- tickets
    def new_ticket(self, kind: str, topic: str | None, user_id: int, urgent: bool) -> int:
        now = time.time()
        cur = self.conn.execute(
            "INSERT INTO tickets(kind, topic, user_id, urgent, status, created, updated) VALUES(?,?,?,?,?,?,?)",
            (kind, topic, user_id, int(urgent), "open", now, now),
        )
        self.conn.commit()
        return cur.lastrowid

    def delete_ticket(self, ticket_id: int) -> None:
        self.conn.execute("DELETE FROM tickets WHERE id=?", (ticket_id,))
        self.conn.commit()

    def get_ticket(self, ticket_id: int):
        return self.conn.execute("SELECT * FROM tickets WHERE id=?", (ticket_id,)).fetchone()

    def tickets_for_user(self, user_id: int, limit: int = 10):
        return self.conn.execute(
            "SELECT * FROM tickets WHERE user_id=? ORDER BY updated DESC, id DESC LIMIT ?", (user_id, limit)
        ).fetchall()

    def set_root(self, ticket_id: int, msg_id: int) -> None:
        self.conn.execute("UPDATE tickets SET root_msg=? WHERE id=? AND root_msg IS NULL", (msg_id, ticket_id))
        self.conn.commit()

    def set_status(self, ticket_id: int, status: str) -> None:
        self.conn.execute("UPDATE tickets SET status=?, updated=? WHERE id=?", (status, time.time(), ticket_id))
        self.conn.commit()

    def set_urgent(self, ticket_id: int) -> None:
        self.conn.execute("UPDATE tickets SET urgent=1 WHERE id=?", (ticket_id,))
        self.conn.commit()

    def set_claimed(self, ticket_id: int, who: str) -> None:
        self.conn.execute("UPDATE tickets SET claimed_by=? WHERE id=?", (who, ticket_id))
        self.conn.commit()

    def set_rating(self, ticket_id: int, rating: int) -> bool:
        cur = self.conn.execute("UPDATE tickets SET rating=? WHERE id=? AND rating IS NULL", (rating, ticket_id))
        self.conn.commit()
        return cur.rowcount > 0

    # ------------------------------------------------------------ admin links
    def link_admin_msg(self, msg_id: int, ticket_id: int) -> None:
        self.conn.execute("INSERT OR REPLACE INTO admin_msgs VALUES(?,?)", (msg_id, ticket_id))
        self.conn.commit()

    def ticket_for_admin_msg(self, msg_id: int) -> int | None:
        row = self.conn.execute("SELECT ticket_id FROM admin_msgs WHERE msg_id=?", (msg_id,)).fetchone()
        return row["ticket_id"] if row else None

    def open_tickets(self, limit: int = 15):
        return self.conn.execute(
            "SELECT * FROM tickets WHERE status='open' AND user_id!=0 ORDER BY urgent DESC, id ASC LIMIT ?", (limit,)
        ).fetchall()

    def stats(self) -> dict:
        q = self.conn.execute
        by_kind = {r["kind"]: r["n"] for r in q("SELECT kind, COUNT(*) n FROM tickets GROUP BY kind")}
        return {
            "users": q("SELECT COUNT(*) n FROM users").fetchone()["n"],
            "subs": q("SELECT COUNT(*) n FROM users WHERE verse_sub=1").fetchone()["n"],
            "open": q("SELECT COUNT(*) n FROM tickets WHERE status='open' AND user_id!=0").fetchone()["n"],
            "urgent_open": q("SELECT COUNT(*) n FROM tickets WHERE status='open' AND urgent=1 AND user_id!=0").fetchone()["n"],
            "avg_rating": q("SELECT AVG(rating) a FROM tickets WHERE rating IS NOT NULL").fetchone()["a"],
            "by_kind": by_kind,
        }
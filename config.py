from __future__ import annotations

import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    token: str
    admin_group_id: int
    admin_topic_id: int | None
    contacts: list[str]
    service_hours: str
    tg_counselor_link: str
    db_path: str
    cooldown: int
    max_chars: int
    sla_hours: int
    verse_hour: int
    tz: ZoneInfo

    def sla(self, lang: str) -> str:
        return f"{self.sla_hours} ሰዓት" if lang == "am" else f"{self.sla_hours} hours"


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token or token.startswith("put-your") or token.startswith("123456789"):
        raise RuntimeError("BOT_TOKEN is missing or still a placeholder. Check your .env file.")
    topic = os.getenv("ADMIN_TOPIC_ID", "").strip()
    return Config(
        token=token,
        admin_group_id=int(os.getenv("ADMIN_GROUP_ID", "-1003708384374")),
        admin_topic_id=int(topic) if topic else None,
        contacts=[c.strip() for c in os.getenv("COUNSELOR_CONTACTS", "").split(";") if c.strip()],
        service_hours=os.getenv("SERVICE_HOURS", "").strip(),
        tg_counselor_link=os.getenv("TG_COUNSELOR_LINK", "https://t.me/your_counselor_username"),
        db_path=os.getenv("DB_PATH", "acu_bot.sqlite3"),
        cooldown=int(os.getenv("SUBMIT_COOLDOWN_SECONDS", "20")),
        max_chars=int(os.getenv("MAX_MESSAGE_CHARS", "3000")),
        sla_hours=int(os.getenv("REPLY_SLA_HOURS", "24")),
        verse_hour=int(os.getenv("DAILY_VERSE_HOUR", "6")),
        tz=ZoneInfo(os.getenv("TIMEZONE", "Africa/Addis_Ababa")),
    )
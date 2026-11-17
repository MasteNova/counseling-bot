"""Presentation layer: screens, keyboards, admin cards. Pure functions — no network calls."""
from __future__ import annotations

import html
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from texts import t

DIV = "──────────────────"
LANG_SCREEN = f"✝️ <b>ACU Counseling · የምክር አገልግሎት</b>\n{DIV}\n<b>🌐 Choose your language · ቋንቋዎን ይምረጡ</b>"

PTYPES = ["prayer", "testimony"]
PCATS = ["heal", "study", "family", "guide", "other"]
DAYS = ["0", "1", "2", "3", "4", "5", "6", "any"]
SLOTS = ["morning", "afternoon", "evening", "any"]
WHO = ["brother", "sister", "any"]

# English labels for the counselor-side cards (counselors read English)
PCAT_EN = {"heal": "Healing & health", "study": "Studies & exams", "family": "Family", "guide": "Guidance", "other": "Other"}
DAY_EN = {"0": "Monday", "1": "Tuesday", "2": "Wednesday", "3": "Thursday", "4": "Friday", "5": "Saturday",
          "6": "Sunday", "any": "Any day"}
SLOT_EN = {"morning": "Morning", "afternoon": "Afternoon", "evening": "Evening", "any": "Any time"}
WHO_EN = {"brother": "Brother", "sister": "Sister", "any": "No preference"}
KIND_ICON = {"counseling": "💬", "booking": "📅", "prayer": "🙏", "testimony": "🕊"}
KIND_EN = {"counseling": "Counseling", "booking": "Appointment", "prayer": "Prayer request", "testimony": "Testimony"}


def esc(s: str | None) -> str:
    return html.escape(s or "", quote=False)


def screen(lang: str, title: str, body: str = "", step: tuple[int, int] | None = None) -> str:
    head = f"{t(lang, 'brand')}\n{DIV}\n<b>{title}</b>"
    if step:
        head += f"  ·  <i>{t(lang, 'step', i=step[0], n=step[1])}</i>"
    return head + (f"\n\n{body}" if body else "")


def preview(text: str, limit: int = 600) -> str:
    return esc(text if len(text) <= limit else text[:limit].rstrip() + "…")


def fmt_date(ts: float, tz) -> str:
    return datetime.fromtimestamp(ts, tz).strftime("%d/%m/%Y")


# ------------------------------------------------------------------ keyboards
def kb(rows: list[list[tuple[str, str]]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton(txt, callback_data=cb) for txt, cb in row] for row in rows])


def chunk(items: list, n: int) -> list[list]:
    return [items[i:i + n] for i in range(0, len(items), n)]


def lang_keyboard(back: bool) -> InlineKeyboardMarkup:
    rows = [[("🇬🇧 English", "lang:en"), ("🇪🇹 አማርኛ", "lang:am")]]
    if back:
        rows.append([("⬅️", "go:set")])
    return kb(rows)


def main_menu(lang: str) -> InlineKeyboardMarkup:
    return kb([
        [(t(lang, "opt_inperson"), "go:book"), (t(lang, "opt_phone"), "go:call")],
        [(t(lang, "opt_tg"), "go:tgchat"), (t(lang, "opt_web"), "go:webform")],
        [(t(lang, "btn_verse"), "go:verse"), (t(lang, "btn_settings"), "go:set")],
    ])


def nav_row(lang: str) -> list[tuple[str, str]]:
    return [(t(lang, "btn_back"), "fl:back"), (t(lang, "btn_cancel"), "go:home")]


def home_only(lang: str) -> InlineKeyboardMarkup:
    return kb([[(t(lang, "btn_home"), "go:home")]])


def after_send(lang: str) -> InlineKeyboardMarkup:
    return kb([[(t(lang, "btn_conv"), "go:conv"), (t(lang, "btn_home"), "go:home")]])


def onoff(lang: str, flag: bool) -> str:
    return t(lang, "on" if flag else "off")


# ------------------------------------------------------------- admin (English)
def build_card(kind: str, ref: str, lines: list[str], body: str | None = None) -> str:
    out = [f"{KIND_ICON[kind]} {KIND_EN[kind].upper()} · {ref}", *lines]
    if body:
        out += ["━━━━━━━━━━━━", body, "━━━━━━━━━━━━"]
    out.append("↩️ Reply to this message to respond.")
    return "\n".join(out)


def admin_buttons(ticket_id: int, *, claimed: bool = False, show_flag: bool = False) -> InlineKeyboardMarkup:
    row = []
    if not claimed:
        row.append(("🙋 Take", f"adm:claim:{ticket_id}"))
    row.append(("✅ Resolve", f"adm:resolve:{ticket_id}"))
    rows = [row]
    if show_flag:
        rows.append([("🚨 Flag urgent", f"adm:flag:{ticket_id}")])
    return kb(rows)
"""Student-facing flows: onboarding, menu, guided wizards, conversations, settings, daily verse."""
from __future__ import annotations

import asyncio
import logging
import os
import re
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ChatType, ParseMode
from telegram.error import BadRequest, Forbidden
from telegram.ext import ContextTypes

import ui
from admin import post_to_admin
from db import DB, label
from texts import t
from ui import esc, kb, screen
from verses import VERSES

logger = logging.getLogger("acu_bot.student")
HTML = ParseMode.HTML

# --------------------------------------------------------------------------- helpers
def D(ctx) -> DB:
    return ctx.application.bot_data["db"]


def C(ctx):
    return ctx.application.bot_data["cfg"]


def L(ctx, uid: int) -> str:
    return D(ctx).get_lang(uid) or "en"


def is_private(update: Update) -> bool:
    chat = update.effective_chat
    return chat is not None and chat.type == ChatType.PRIVATE


async def strip_prompt(ctx) -> None:
    """Remove buttons from the previous screen so stale keyboards never pile up."""
    p = ctx.user_data.pop("prompt", None)
    if p:
        try:
            await ctx.bot.edit_message_reply_markup(p[0], p[1], reply_markup=None)
        except Exception:
            pass


async def render(update: Update, ctx, text: str, markup=None, *, new: bool = False) -> None:
    """Button taps edit the screen in place (app-like feel); typed input gets a fresh message."""
    q = update.callback_query
    if q and not new:
        try:
            await q.edit_message_text(text, parse_mode=HTML, reply_markup=markup)
            ctx.user_data["prompt"] = (q.message.chat_id, q.message.message_id)
            return
        except BadRequest as e:
            if "not modified" in str(e).lower():
                return
            logger.info("edit failed (%s); sending a new message", e)
    await strip_prompt(ctx)
    chat_id = update.effective_chat.id
    m = await ctx.bot.send_message(chat_id, text, parse_mode=HTML, reply_markup=markup)
    ctx.user_data["prompt"] = (chat_id, m.message_id)


async def clear_reply_kb(ctx, chat_id: int) -> None:
    if not ctx.user_data.pop("reply_kb", False):
        return
    try:
        m = await ctx.bot.send_message(chat_id, "…", reply_markup=ReplyKeyboardRemove())
        await m.delete()
    except Exception:
        pass


def contacts_block(ctx, lang: str) -> str:
    items = C(ctx).contacts
    return "\n".join(f"👤 {esc(c)}" for c in items) if items else t(lang, "no_contacts")


def today_index(ctx) -> int:
    return datetime.now(C(ctx).tz).date().toordinal() % len(VERSES)


# --------------------------------------------------------------------------- entry points
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_private(update):
        return
    ctx.user_data.clear()
    row = D(ctx).user(update.effective_user.id)
    if row is None or row["lang"] is None:
        await render(update, ctx, ui.LANG_SCREEN, ui.lang_keyboard(back=False))
    elif not row["onboarded"]:
        await show_welcome(update, ctx)
    else:
        await show_menu(update, ctx)


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_private(update):
        await show_menu(update, ctx)


async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_private(update):
        back = bool((D(ctx).user(update.effective_user.id) or {"onboarded": 0})["onboarded"])
        await render(update, ctx, ui.LANG_SCREEN, ui.lang_keyboard(back=back))


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_private(update):
        return
    lang = L(ctx, update.effective_user.id)
    await render(update, ctx, screen(lang, t(lang, "help_title"), t(lang, "help_body")), ui.main_menu(lang))


async def cmd_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_private(update):
        return
    lang = L(ctx, update.effective_user.id)
    had_flow = ctx.user_data.pop("flow", None) is not None
    await clear_reply_kb(ctx, update.effective_chat.id)
    if had_flow:
        await update.message.reply_text(t(lang, "cancelled"))
    await show_menu(update, ctx)


async def show_welcome(update: Update, ctx):
    user = update.effective_user
    lang = L(ctx, user.id)
    await render(
        update, ctx,
        screen(lang, t(lang, "welcome_title", name=esc(user.first_name)), t(lang, "welcome_body")),
        kb([[(t(lang, "btn_start"), "go:start")]]),
    )


async def show_menu(update: Update, ctx, *, first: bool = False, new: bool = False):
    user = update.effective_user
    lang = L(ctx, user.id)
    ctx.user_data.pop("flow", None)
    await clear_reply_kb(ctx, update.effective_chat.id)
    title = t(lang, "menu_title_new") if first else t(lang, "menu_title_back", name=esc(user.first_name))
    await render(update, ctx, screen(lang, title, t(lang, "menu_body")), ui.main_menu(lang), new=new)


async def on_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    choice = q.data.split(":", 1)[1]
    D(ctx).set_lang(q.from_user.id, choice)
    row = D(ctx).user(q.from_user.id)
    if row["onboarded"]:
        await show_settings(update, ctx)
    else:
        await show_welcome(update, ctx)


async def on_go(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data.split(":", 1)[1]
    uid = q.from_user.id
    if D(ctx).get_lang(uid) is None:  # e.g. data was deleted
        await render(update, ctx, ui.LANG_SCREEN, ui.lang_keyboard(back=False))
        return
    if action == "start":
        D(ctx).set_onboarded(uid)
        await show_menu(update, ctx, first=True)
    elif action == "home":
        await show_menu(update, ctx)
    elif action == "book":
        await start_flow(update, ctx, "book", "day")
    elif action == "pray":
        await start_flow(update, ctx, "pray", "type")
    elif action == "call":
        await show_call(update, ctx)
    elif action == "tgchat":
        await show_tg_chat(update, ctx)
    elif action == "webform":
        await show_web_form(update, ctx)
    elif action == "verse":
        await show_verse(update, ctx, today_index(ctx))
    elif action == "conv":
        await show_conversations(update, ctx)
    elif action == "set":
        await show_settings(update, ctx)


async def show_call(update: Update, ctx):
    lang = L(ctx, update.effective_user.id)
    hours = C(ctx).service_hours
    body = t(lang, "call_body", contacts=contacts_block(ctx, lang),
             hours=t(lang, "hours_line", hours=esc(hours)) if hours else "")
    await render(update, ctx, screen(lang, t(lang, "call_title"), body), ui.home_only(lang))


# --------------------------------------------------------------------------- wizard engine
FLOW_STEPS = {
    "pray": ["type", "cat", "write", "review"],
    "book": ["day", "time", "who", "contact", "note", "review"],
    "reply": ["write"],
}
FIELD_KIND = {"ptype": "pray", "pcat": "pray", "day": "book", "slot": "book", "who": "book"}
FIELD_STEP = {"ptype": "type", "pcat": "cat", "day": "day", "slot": "time", "who": "who"}
FIELD_ALLOWED = {"ptype": ui.PTYPES, "pcat": ui.PCATS, "day": ui.DAYS, "slot": ui.SLOTS, "who": ui.WHO}
PHONE_RE = re.compile(r"^\+?[\d\s\-()]{9,16}$")


def steps_for(flow: dict) -> list[str]:
    steps = list(FLOW_STEPS[flow["kind"]])
    if flow["kind"] == "pray" and flow["data"].get("ptype") == "testimony":
        steps.remove("cat")
    return steps


def build_view(lang: str, flow: dict, user, cfg) -> tuple[str, object]:
    """Pure function: (flow state) -> (screen text, keyboard)."""
    kind, step, d = flow["kind"], flow["step"], flow["data"]
    order = steps_for(flow)
    prog = None if kind in ("reply", "talk") else (order.index(step) + 1, len(order))
    nav = ui.nav_row(lang)

    def choice_rows(field: str, keys: list[str], label_key, per_row: int):
        btns = [(t(lang, label_key(k)), f"fl:set:{field}:{k}") for k in keys]
        return ui.chunk(btns, per_row) + [nav]

    # ---------------- prayer & testimony
    if kind == "pray":
        title = t(lang, "pray_title")
        if step == "type":
            return screen(lang, title, t(lang, "pray_type_body"), prog), kb(
                choice_rows("ptype", ui.PTYPES, lambda k: f"ptype_{k}", 2))
        if step == "cat":
            return screen(lang, title, t(lang, "pray_cat_body"), prog), kb(
                choice_rows("pcat", ui.PCATS, lambda k: f"pcat_{k}", 2))
        testimony = d["ptype"] == "testimony"
        if step == "write":
            body = (t(lang, "pray_write_testimony") if testimony
                    else t(lang, "pray_write_prayer", topic=t(lang, f"pcat_{d['cat']}")))
            return screen(lang, title, body, prog), kb([nav])
        d.setdefault("anon", True)
        d.setdefault("share", False)
        head = "" if testimony else f"<b>{t(lang, 'lbl_topic')}:</b> {t(lang, 'pcat_' + d['cat'])}\n\n"
        body = (f"{head}<blockquote>{ui.preview(d['text'])}</blockquote>\n\n"
                f"{t(lang, 'note_anon_on' if d['anon'] else 'note_anon_off')}")
        rows = [[(t(lang, "btn_send"), "fl:send")],
                [(t(lang, "opt_anon_on" if d["anon"] else "opt_anon_off"), "fl:opt:anon")]]
        if testimony:
            body += f"\n{t(lang, 'note_share' if d['share'] else 'note_noshare')}"
            rows.append([(t(lang, "opt_share_on" if d["share"] else "opt_share_off"), "fl:opt:share")])
        rows.append([(t(lang, "btn_rewrite"), "fl:back"), (t(lang, "btn_cancel"), "go:home")])
        return screen(lang, t(lang, "review_title"), body, prog), kb(rows)

    # ---------------- book a meeting
    if kind == "book":
        title = t(lang, "book_title")
        if step == "day":
            btns = [(t(lang, f"day_{k}"), f"fl:set:day:{k}") for k in ui.DAYS]
            rows = ui.chunk(btns[:7], 4) + [btns[7:]] + [nav]
            return screen(lang, title, t(lang, "book_day_body"), prog), kb(rows)
        if step == "time":
            return screen(lang, title, t(lang, "book_time_body"), prog), kb(
                choice_rows("slot", ui.SLOTS, lambda k: f"slot_{k}", 2))
        if step == "who":
            return screen(lang, title, t(lang, "book_who_body"), prog), kb(
                choice_rows("who", ui.WHO, lambda k: f"who_{k}", 1))
        if step == "contact":
            return screen(lang, title, t(lang, "book_contact_body"), prog), kb([nav])
        if step == "note":
            return screen(lang, title, t(lang, "book_note_body"), prog), kb([[(t(lang, "btn_skip"), "fl:skip")], nav])
        contact = d.get("contact") or (t(lang, "contact_tg", u=esc(user.username)) if user.username else "—")
        body = (f"<b>{t(lang, 'lbl_day')}:</b> {t(lang, 'day_' + d['day'])}\n"
                f"<b>{t(lang, 'lbl_time')}:</b> {t(lang, 'slot_' + d['slot'])}\n"
                f"<b>{t(lang, 'lbl_who')}:</b> {t(lang, 'who_' + d['who'])}\n"
                f"<b>{t(lang, 'lbl_contact')}:</b> {esc(contact)}\n")
        if d.get("note"):
            body += f"<b>{t(lang, 'lbl_note')}:</b> {ui.preview(d['note'], 300)}\n"
        body += f"\n<i>{t(lang, 'book_review_foot')}</i>"
        return screen(lang, t(lang, "review_title"), body, prog), kb([
            [(t(lang, "btn_send_request"), "fl:send")],
            [(t(lang, "btn_restart"), "fl:restart"), (t(lang, "btn_cancel"), "go:home")],
        ])

    # ---------------- reply to a counselor
    ref = label(d["kind"], d["ticket_id"])
    return screen(lang, t(lang, "reply_title"), t(lang, "reply_body", ref=ref)), kb([[(t(lang, "btn_cancel"), "go:home")]])


async def render_step(update: Update, ctx, *, new: bool = False):
    flow = ctx.user_data.get("flow")
    user = update.effective_user
    if not flow:
        await show_menu(update, ctx, new=new)
        return
    lang = L(ctx, user.id)
    text, markup = build_view(lang, flow, user, C(ctx))
    await render(update, ctx, text, markup, new=new)
    if flow["kind"] == "book" and flow["step"] == "contact":
        rows = [[KeyboardButton(t(lang, "kb_share"), request_contact=True)]]
        if user.username:
            rows.append([KeyboardButton(t(lang, "kb_skip"))])
        await ctx.bot.send_message(
            update.effective_chat.id, t(lang, "kb_hint"),
            reply_markup=ReplyKeyboardMarkup(rows, resize_keyboard=True, one_time_keyboard=True),
        )
        ctx.user_data["reply_kb"] = True


async def start_flow(update: Update, ctx, kind: str, first: str, data: dict | None = None, *, new: bool = False):
    await clear_reply_kb(ctx, update.effective_chat.id)
    ctx.user_data["flow"] = {"kind": kind, "step": first, "data": data or {}}
    await render_step(update, ctx, new=new)


def advance(flow: dict) -> None:
    order = steps_for(flow)
    i = order.index(flow["step"])
    if i + 1 < len(order):
        flow["step"] = order[i + 1]


async def expired(update: Update, ctx):
    lang = L(ctx, update.effective_user.id)
    await show_menu(update, ctx)
    await ctx.bot.send_message(update.effective_chat.id, t(lang, "err_expired"))


async def on_back(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    flow = ctx.user_data.get("flow")
    if not flow:
        return await expired(update, ctx)
    order = steps_for(flow)
    i = order.index(flow["step"])
    if flow["step"] == "contact":
        await clear_reply_kb(ctx, q.message.chat_id)
    if i == 0:
        return await show_menu(update, ctx)
    flow["step"] = order[i - 1]
    await render_step(update, ctx)


async def on_choice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, _, field, value = q.data.split(":")
    flow = ctx.user_data.get("flow")
    if not flow:
        return await expired(update, ctx)
    if flow["kind"] != FIELD_KIND[field] or flow["step"] != FIELD_STEP[field] or value not in FIELD_ALLOWED[field]:
        return await render_step(update, ctx)  # stale button: just redraw the current screen
    flow["data"]["cat" if field == "pcat" else field] = value
    advance(flow)
    await render_step(update, ctx)


async def on_option(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    opt = q.data.split(":")[2]
    flow = ctx.user_data.get("flow")
    if not flow:
        return await expired(update, ctx)
    if flow["step"] == "review":
        flow["data"][opt] = not flow["data"].get(opt, opt == "anon")
    await render_step(update, ctx)


async def on_skip(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    flow = ctx.user_data.get("flow")
    if not flow:
        return await expired(update, ctx)
    if flow["kind"] == "book" and flow["step"] == "note":
        flow["data"]["note"] = ""
        advance(flow)
    await render_step(update, ctx)


async def on_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await start_flow(update, ctx, "book", "day")


# --------------------------------------------------------------------------- typed input
async def on_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_private(update):
        return
    msg, user = update.message, update.effective_user
    lang = L(ctx, user.id)
    flow = ctx.user_data.get("flow")
    text = (msg.text or "").strip()

    if not flow:
        await render(update, ctx, screen(lang, t(lang, "menu_title_new"), t(lang, "no_flow")), ui.main_menu(lang), new=True)
        return

    kind, step = flow["kind"], flow["step"]

    if step == "write":
        if not text:
            await msg.reply_text(t(lang, "err_empty"))
            return
        if len(text) > C(ctx).max_chars:
            await msg.reply_text(t(lang, "err_long", max=C(ctx).max_chars))
            return
        if kind == "reply":
            return await submit_reply(update, ctx, text)
        flow["data"]["text"] = text
        flow["step"] = "review"
        return await render_step(update, ctx, new=True)

    if kind == "book" and step == "contact":
        skip_labels = {t("en", "kb_skip"), t("am", "kb_skip")}
        if text in skip_labels and user.username:
            flow["data"]["contact"] = None
            ack = t(lang, "contact_skip_ok")
        elif PHONE_RE.match(text):
            flow["data"]["contact"] = text
            ack = t(lang, "contact_ok")
        else:
            await msg.reply_text(t(lang, "contact_bad"))
            return
        ctx.user_data.pop("reply_kb", None)
        await msg.reply_text(ack, reply_markup=ReplyKeyboardRemove())
        advance(flow)
        return await render_step(update, ctx, new=True)

    if kind == "book" and step == "note":
        flow["data"]["note"] = text[:500]
        advance(flow)
        return await render_step(update, ctx, new=True)

    await msg.reply_text(t(lang, "hint_buttons"))


async def on_contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not is_private(update):
        return
    msg, user = update.message, update.effective_user
    lang = L(ctx, user.id)
    flow = ctx.user_data.get("flow")
    if not flow or flow["kind"] != "book" or flow["step"] != "contact":
        return
    c = msg.contact
    if c.user_id and c.user_id != user.id:  # only accept the sender's own number
        await msg.reply_text(t(lang, "contact_bad"))
        return
    flow["data"]["contact"] = "+" + c.phone_number.lstrip("+")
    ctx.user_data.pop("reply_kb", None)
    await msg.reply_text(t(lang, "contact_ok"), reply_markup=ReplyKeyboardRemove())
    advance(flow)
    await render_step(update, ctx, new=True)


async def on_other_media(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if is_private(update):
        await update.message.reply_text(t(L(ctx, update.effective_user.id), "err_text_only"))


# --------------------------------------------------------------------------- submitting
def _who_line(user, anon: bool) -> str:
    if anon:
        return "🔒 Anonymous"
    return f"👤 {user.full_name} (@{user.username})" if user.username else f"👤 {user.full_name} (no username)"


async def on_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    user = q.from_user
    flow = ctx.user_data.get("flow")
    lang = L(ctx, user.id)
    if not flow or flow["step"] != "review":
        await q.answer()
        return await expired(update, ctx)

    store, cfg = D(ctx), C(ctx)
    wait = cfg.cooldown - store.seconds_since_submit(user.id)
    if wait > 0:
        await q.answer(t(lang, "err_cooldown", s=int(wait) + 1), show_alert=True)
        return
    await q.answer()
    d, kind = flow["data"], flow["kind"]
    if kind == "pray":
        tkind = "testimony" if d["ptype"] == "testimony" else "prayer"
        topic, anon, urgent = d.get("cat"), d.get("anon", True), False
    else:
        tkind, topic, anon, urgent = "booking", None, False, False

    ticket_id = store.new_ticket(tkind, topic, user.id, urgent)
    ref = label(tkind, ticket_id)
    lang_en = "Amharic" if lang == "am" else "English"

    if tkind == "prayer":
        lines = [f"Topic: {ui.PCAT_EN[topic]}", f"From: {_who_line(user, anon)}", f"Language: {lang_en}"]
        card, markup = ui.build_card(tkind, ref, lines, d["text"]), ui.admin_buttons(ticket_id)
    elif tkind == "testimony":
        lines = [f"From: {_who_line(user, anon)}", f"Language: {lang_en}",
                 "Sharing: ✅ OK to share with the fellowship" if d.get("share") else "Sharing: 🔒 Team only"]
        card, markup = ui.build_card(tkind, ref, lines, d["text"]), ui.admin_buttons(ticket_id)
    else:
        contact = d.get("contact") or ("Telegram only" + (f" (@{user.username})" if user.username else ""))
        lines = [f"From: 👤 {user.full_name}" + (f" (@{user.username})" if user.username else ""),
                 f"Phone/contact: {contact}",
                 f"Preferred: {ui.DAY_EN[d['day']]} · {ui.SLOT_EN[d['slot']]}",
                 f"Counselor: {ui.WHO_EN[d['who']]}", f"Language: {lang_en}"]
        if d.get("note"):
            lines.append(f"Note: {d['note']}")
        card, markup = ui.build_card(tkind, ref, lines), ui.admin_buttons(ticket_id)

    try:
        sent = await post_to_admin(ctx, card, markup)
    except Exception:
        logger.exception("Could not post %s to the admin group", ref)
        store.delete_ticket(ticket_id)
        await q.message.reply_text(t(lang, "err_send"))
        return

    store.set_root(ticket_id, sent.message_id)
    store.link_admin_msg(sent.message_id, ticket_id)
    store.touch_submit(user.id)
    ctx.user_data.pop("flow", None)
    await clear_reply_kb(ctx, q.message.chat_id)
    sla = cfg.sla(lang)
    if tkind == "prayer":
        s_title, s_body = t(lang, "sent_prayer_title"), t(lang, "sent_prayer_body", ref=ref)
    elif tkind == "testimony":
        s_title, s_body = t(lang, "sent_testi_title"), t(lang, "sent_testi_body", ref=ref)
    else:
        s_title, s_body = t(lang, "sent_book_title"), t(lang, "sent_book_body", ref=ref, sla=sla)
    await render(update, ctx, screen(lang, "✅ " + s_title, s_body), ui.after_send(lang))

async def submit_reply(update: Update, ctx, text: str):
    msg, user = update.message, update.effective_user
    lang = L(ctx, user.id)
    store, cfg = D(ctx), C(ctx)
    flow = ctx.user_data["flow"]
    ticket = store.get_ticket(flow["data"]["ticket_id"])
    if ticket is None or ticket["user_id"] != user.id:
        return await expired(update, ctx)
    wait = cfg.cooldown - store.seconds_since_submit(user.id)
    if wait > 0:
        await msg.reply_text(t(lang, "err_cooldown", s=int(wait) + 1))
        return

    ref = label(ticket["kind"], ticket["id"])
    reopened = "\n🔁 Reopened by the student." if ticket["status"] == "closed" else ""
    try:
        sent = await post_to_admin(
            ctx, f"💬 FOLLOW-UP · {ref}{reopened}\n━━━━━━━━━━━━\n{text}\n━━━━━━━━━━━━\n↩️ Reply to this message to respond.",
            reply_to=ticket["root_msg"],
        )
    except Exception:
        logger.exception("Could not post follow-up for %s", ref)
        await msg.reply_text(t(lang, "err_send"))
        return
    store.link_admin_msg(sent.message_id, ticket["id"])
    store.set_status(ticket["id"], "open")
    store.touch_submit(user.id)
    ctx.user_data.pop("flow", None)
    await render(update, ctx, screen(lang, "✅ " + t(lang, "reply_sent_title"), t(lang, "reply_sent_body")),
                 ui.after_send(lang), new=True)


# --------------------------------------------------------------------------- conversations
STATUS_ICON = {"open": "🟡", "answered": "🟢", "closed": "✅"}


async def show_conversations(update: Update, ctx):
    user = update.effective_user
    lang, cfg = L(ctx, user.id), C(ctx)
    rows = D(ctx).tickets_for_user(user.id)
    if not rows:
        await render(update, ctx, screen(lang, t(lang, "conv_title"), t(lang, "conv_empty")),
                     kb([[(t(lang, "btn_home"), "go:home")]]))
        return
    buttons = [[(f"{STATUS_ICON[r['status']]} {label(r['kind'], r['id'])} · {t(lang, 'kind_' + r['kind'])} · "
                 f"{ui.fmt_date(r['created'], cfg.tz)}", f"cv:open:{r['id']}")] for r in rows]
    buttons.append([(t(lang, "btn_home"), "go:home")])
    await render(update, ctx, screen(lang, t(lang, "conv_title"), t(lang, "conv_body")), kb(buttons))


async def close_ticket(ctx, ticket) -> None:
    store = D(ctx)
    store.set_status(ticket["id"], "closed")
    try:
        await post_to_admin(ctx, f"✅ The student closed {label(ticket['kind'], ticket['id'])}.", reply_to=ticket["root_msg"])
    except Exception:
        pass


async def on_conv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, action, tid = q.data.split(":")
    user = q.from_user
    lang, cfg, store = L(ctx, user.id), C(ctx), D(ctx)
    ticket = store.get_ticket(int(tid))
    if ticket is None or ticket["user_id"] != user.id:
        await q.answer()
        return

    ref = label(ticket["kind"], ticket["id"])
    if action == "open":
        await q.answer()
        body = (f"<b>{t(lang, 'lbl_type')}:</b> {t(lang, 'kind_' + ticket['kind'])}\n"
                f"<b>{t(lang, 'lbl_started')}:</b> {ui.fmt_date(ticket['created'], cfg.tz)}\n"
                f"<b>{t(lang, 'lbl_status')}:</b> {t(lang, 'status_' + ticket['status'])}")
        rows = [[(t(lang, "btn_reply"), f"cv:reply:{ticket['id']}")]]
        if ticket["status"] != "closed":
            rows.append([(t(lang, "btn_close"), f"cv:close:{ticket['id']}")])
        rows.append([(t(lang, "btn_back"), "go:conv")])
        await render(update, ctx, screen(lang, ref, body), kb(rows))
    elif action == "reply":
        await q.answer()
        await start_flow(update, ctx, "reply", "write", {"ticket_id": ticket["id"], "kind": ticket["kind"]}, new=True)
    elif action == "close":
        await q.answer(t(lang, "closed_toast"))
        await close_ticket(ctx, ticket)
        await show_conversations(update, ctx)
    elif action == "nclose":
        await q.answer(t(lang, "closed_toast"))
        await close_ticket(ctx, ticket)
        try:
            await q.edit_message_reply_markup(ui.home_only(lang))
        except Exception:
            pass


async def on_feedback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    _, tid, n = q.data.split(":")
    lang = L(ctx, q.from_user.id)
    ticket = D(ctx).get_ticket(int(tid))
    if ticket and ticket["user_id"] == q.from_user.id:
        D(ctx).set_rating(int(tid), int(n))
        await q.answer()
        try:
            await q.edit_message_text(t(lang, "fb_thanks"), reply_markup=ui.home_only(lang))
        except Exception:
            pass
    else:
        await q.answer()


# --------------------------------------------------------------------------- verse
async def show_verse(update: Update, ctx, idx: int):
    user = update.effective_user
    lang = L(ctx, user.id)
    v = VERSES[idx % len(VERSES)]
    sub = bool(D(ctx).user(user.id)["verse_sub"])
    body = f"“{esc(v[lang])}”\n\n— <b>{v['ref_' + lang]}</b>"
    await render(update, ctx, screen(lang, "📖 " + t(lang, "verse_title"), body), kb([
        [(t(lang, "btn_more_verse"), f"vs:{(idx + 1) % len(VERSES)}")],
        [(t(lang, "btn_sub_off" if sub else "btn_sub_on"), "sub:verse")],
        [(t(lang, "btn_home"), "go:home")],
    ]))


async def on_verse_nav(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await show_verse(update, ctx, int(q.data.split(":")[1]))


async def on_subscribe(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id
    lang = L(ctx, uid)
    where = q.data.split(":")[1]
    row = D(ctx).user(uid)
    if row is None:
        await q.answer()
        return
    new_state = False if where == "off" else not bool(row["verse_sub"])
    D(ctx).set_verse_sub(uid, new_state)
    await q.answer(t(lang, "sub_on_toast" if new_state else "sub_off_toast"))
    if where == "off":
        try:
            await q.edit_message_reply_markup(ui.home_only(lang))
        except Exception:
            pass
    elif where == "set":
        await show_settings(update, ctx)
    else:
        await show_verse(update, ctx, today_index(ctx))


async def send_daily_verse(ctx: ContextTypes.DEFAULT_TYPE):
    idx = datetime.now(C(ctx).tz).date().toordinal() % len(VERSES)
    v = VERSES[idx]
    for uid, lang in D(ctx).verse_subscribers():
        text = f"{t(lang, 'daily_head')}\n{ui.DIV}\n“{esc(v[lang])}”\n\n— <b>{v['ref_' + lang]}</b>"
        markup = kb([[(t(lang, "btn_home"), "go:home"), (t(lang, "btn_sub_off"), "sub:off")]])
        try:
            await ctx.bot.send_message(uid, text, parse_mode=HTML, reply_markup=markup)
        except Forbidden:
            D(ctx).set_verse_sub(uid, False)
        except Exception:
            logger.exception("Daily verse failed for %s", uid)
        await asyncio.sleep(0.05)  # stay far below Telegram's broadcast limits


# --------------------------------------------------------------------------- settings
async def show_tg_chat(update: Update, ctx):
    user = update.effective_user
    lang = L(ctx, user.id)
    link = C(ctx).tg_counselor_link
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_open_tg"), url=link)],
        [InlineKeyboardButton(t(lang, "btn_back"), callback_data="go:home")],
    ])
    await render(update, ctx, screen(lang, t(lang, "tg_title"), t(lang, "tg_body")), markup)


async def show_web_form(update: Update, ctx):
    user = update.effective_user
    lang = L(ctx, user.id)
    link = os.getenv("WEB_FORM_URL", "https://tally.so/r/your_form_id")
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(t(lang, "btn_open_web"), url=link)],
        [InlineKeyboardButton(t(lang, "btn_back"), callback_data="go:home")],
    ])
    await render(update, ctx, screen(lang, t(lang, "web_title"), t(lang, "web_body")), markup)


async def show_settings(update: Update, ctx):
    user = update.effective_user
    lang = L(ctx, user.id)
    sub = bool(D(ctx).user(user.id)["verse_sub"])
    body = t(lang, "set_body", language=t(lang, "lang_name"), verse=ui.onoff(lang, sub))
    await render(update, ctx, screen(lang, "⚙️ " + t(lang, "set_title"), body), kb([
        [(t(lang, "btn_set_lang"), "st:lang"), (t(lang, "btn_set_verse_on" if sub else "btn_set_verse_off"), "sub:set")],
        [(t(lang, "btn_privacy"), "st:privacy"), (t(lang, "btn_about"), "st:about")],
        [(t(lang, "btn_delete"), "st:delete")],
        [(t(lang, "btn_home"), "go:home")],
    ]))


async def on_settings(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    action = q.data.split(":")[1]
    uid = q.from_user.id
    lang = L(ctx, uid)
    back = kb([[(t(lang, "btn_back"), "go:set")]])
    if action == "lang":
        await render(update, ctx, ui.LANG_SCREEN, ui.lang_keyboard(back=True))
    elif action == "privacy":
        await render(update, ctx, screen(lang, "🔒 " + t(lang, "privacy_title"), t(lang, "privacy_body")), back)
    elif action == "about":
        await render(update, ctx, screen(lang, "ℹ️ " + t(lang, "about_title"), t(lang, "about_body")), back)
    elif action == "delete":
        await render(update, ctx, screen(lang, "🗑 " + t(lang, "delete_title"), t(lang, "delete_body")), kb([
            [(t(lang, "btn_delete_yes"), "st:delete_yes")], [(t(lang, "btn_cancel"), "go:set")]]))
    elif action == "delete_yes":
        D(ctx).delete_user(uid)
        ctx.user_data.clear()
        await render(update, ctx, t(lang, "deleted_msg"), None)
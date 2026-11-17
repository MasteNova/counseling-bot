"""Counselor-side handlers (admin forum group)."""
from __future__ import annotations

import logging

from telegram import InlineKeyboardMarkup, LinkPreviewOptions, ReplyParameters, Update
from telegram.constants import ParseMode, ReactionEmoji
from telegram.error import Forbidden
from telegram.ext import ContextTypes

import ui
from db import DB, label
from texts import t

logger = logging.getLogger("acu_bot.admin")
HTML = ParseMode.HTML


def D(ctx) -> DB:
    return ctx.application.bot_data["db"]


def C(ctx):
    return ctx.application.bot_data["cfg"]


async def post_to_admin(ctx, text: str, markup: InlineKeyboardMarkup | None = None, reply_to: int | None = None):
    c = C(ctx)
    kwargs = dict(chat_id=c.admin_group_id, text=text, reply_markup=markup)
    if c.admin_topic_id:
        kwargs["message_thread_id"] = c.admin_topic_id
    if reply_to:
        kwargs["reply_parameters"] = ReplyParameters(message_id=reply_to, allow_sending_without_reply=True)
    return await ctx.bot.send_message(**kwargs)


def student_buttons(lang: str, ticket_id: int) -> InlineKeyboardMarkup:
    return ui.kb([[(t(lang, "btn_reply"), f"cv:reply:{ticket_id}"), (t(lang, "btn_close"), f"cv:nclose:{ticket_id}")]])


# --------------------------------------------------------------- reply routing
async def on_admin_reply(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    original = msg.reply_to_message
    if original is None:
        return
    store = D(ctx)
    ticket_id = store.ticket_for_admin_msg(original.message_id)

    if ticket_id is None:
        if original.from_user and original.from_user.id == ctx.bot.id:
            await msg.reply_text("⚠️ I can't find the student for this message (it predates the database).")
        return

    ticket = store.get_ticket(ticket_id)
    ref = label(ticket["kind"], ticket_id)
    if ticket["user_id"] == 0:
        await msg.reply_text(f"⚠️ {ref}: the student deleted their data, so they can't be reached.")
        return

    lang = store.get_lang(ticket["user_id"]) or "en"
    text = f"{t(lang, 'from_counselor', ref=ref)}\n{ui.DIV}\n{ui.esc(msg.text)}"
    try:
        await ctx.bot.send_message(ticket["user_id"], text, parse_mode=HTML, reply_markup=student_buttons(lang, ticket_id))
    except Forbidden:
        await msg.reply_text(f"⚠️ {ref}: the student has blocked the bot or deleted the chat.")
        return
    except Exception as e:
        logger.exception("Failed to deliver counselor reply")
        await msg.reply_text(f"⚠️ Failed to deliver: {e}")
        return

    store.link_admin_msg(msg.message_id, ticket_id)  # lets counselors reply to each other's replies too
    store.set_status(ticket_id, "answered")
    try:
        await ctx.bot.set_message_reaction(msg.chat_id, msg.message_id, reaction=ReactionEmoji.THUMBS_UP)
    except Exception:
        await msg.reply_text(f"✅ Delivered ({ref}).")


# ------------------------------------------------------------- card actions
async def on_admin_action(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if q.message is None or q.message.chat_id != C(ctx).admin_group_id:
        await q.answer()
        return
    _, action, tid = q.data.split(":")
    ticket_id = int(tid)
    store = D(ctx)
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        await q.answer("Ticket not found.", show_alert=True)
        return

    who = q.from_user.full_name
    text = q.message.text or ""
    ref = label(ticket["kind"], ticket_id)
    student_id = ticket["user_id"]
    lang = (store.get_lang(student_id) or "en") if student_id else "en"

    if action == "claim":
        if ticket["claimed_by"]:
            await q.answer(f"Already taken by {ticket['claimed_by']}.", show_alert=True)
            return
        store.set_claimed(ticket_id, who)
        await q.answer("It's yours 🙏")
        await q.edit_message_text(
            f"{text}\n🙋 Taken by {who}",
            reply_markup=ui.admin_buttons(ticket_id, claimed=True, show_flag="Priority: Normal" in text),
        )
        if student_id and ticket["kind"] in ("counseling", "booking"):
            try:
                await ctx.bot.send_message(student_id, t(lang, "taken_note", ref=ref), disable_notification=True)
            except Exception:
                pass

    elif action == "flag":
        store.set_urgent(ticket_id)
        await q.answer("Flagged urgent 🚨")
        await q.edit_message_text(
            text.replace("Priority: Normal", "Priority: 🚨 URGENT"),
            reply_markup=ui.admin_buttons(ticket_id, claimed=bool(ticket["claimed_by"]), show_flag=False),
        )

    elif action == "resolve":
        store.set_status(ticket_id, "closed")
        await q.answer("Marked resolved ✅")
        await q.edit_message_text(f"{text}\n✅ Resolved by {who}", reply_markup=None)
        if student_id:
            markup = ui.kb([[(t(lang, f"fb_{n}"), f"fb:{ticket_id}:{n}") for n in (3, 2, 1)]])
            try:
                await ctx.bot.send_message(student_id, t(lang, "resolved_note", ref=ref), reply_markup=markup)
            except Exception:
                logger.info("Could not notify student for %s", ref)


# --------------------------------------------------------------- admin commands
async def cmd_chatinfo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = update.effective_message
    await m.reply_text(f"Chat ID: {m.chat_id}\nTopic ID: {m.message_thread_id}")


async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    s = D(ctx).stats()
    k = s["by_kind"]
    rating = f"{s['avg_rating']:.1f}/3" if s["avg_rating"] else "—"
    await update.effective_message.reply_text(
        "📊 ACU Counseling Bot\n"
        f"Students: {s['users']}  ·  Daily-verse subscribers: {s['subs']}\n\n"
        f"Open now: {s['open']}  (🚨 urgent: {s['urgent_open']})\n"
        f"All time — Counseling: {k.get('counseling', 0)} · Appointments: {k.get('booking', 0)} · "
        f"Prayers: {k.get('prayer', 0)} · Testimonies: {k.get('testimony', 0)}\n"
        f"Average feedback: {rating}"
    )


async def cmd_open(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    rows = D(ctx).open_tickets()
    if not rows:
        await update.effective_message.reply_text("🎉 No open conversations. Well done, team!")
        return
    gid = str(C(ctx).admin_group_id)
    cid = gid[4:] if gid.startswith("-100") else gid.lstrip("-")
    lines = ["📋 Waiting for a counselor (urgent first):", ""]
    for r in rows:
        link = f"https://t.me/c/{cid}/{r['root_msg']}" if r["root_msg"] else ""
        flag = "🚨 " if r["urgent"] else ""
        taken = f" — {r['claimed_by']}" if r["claimed_by"] else ""
        lines.append(f"{flag}{label(r['kind'], r['id'])} · {ui.KIND_EN[r['kind']]}{taken}\n{link}")
    await update.effective_message.reply_text("\n".join(lines), link_preview_options=LinkPreviewOptions(is_disabled=True))
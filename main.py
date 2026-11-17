"""
ACU Counseling Bot — Arba Minch University Christian Fellowship
Run:  python main.py
"""
from __future__ import annotations

import logging
from datetime import time as dtime

import httpx
from telegram import BotCommand, Update
from telegram.error import NetworkError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

import admin
import student
from config import Config, load_config
from db import DB
from texts import check_parity

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("acu_bot")


async def on_error(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    if isinstance(ctx.error, NetworkError):
        logger.warning("Telegram network error while handling update: %s", ctx.error)
        return
    logger.error("Unhandled exception", exc_info=ctx.error)


async def post_init(app: Application):
    cfg: Config = app.bot_data["cfg"]
    await app.bot.set_my_commands([
        BotCommand("start", "Main menu"), BotCommand("menu", "Back to menu"),
        BotCommand("language", "Change language"), BotCommand("cancel", "Cancel"), BotCommand("help", "Help"),
    ])
    await app.bot.set_my_commands([
        BotCommand("start", "ዋና ማውጫ"), BotCommand("menu", "ወደ ማውጫ"),
        BotCommand("language", "ቋንቋ ቀይር"), BotCommand("cancel", "ሰርዝ"), BotCommand("help", "እገዛ"),
    ], language_code="am")
    try:
        chat = await app.bot.get_chat(cfg.admin_group_id)
        logger.info("Admin group OK: %s (forum=%s) topic=%s", chat.title, getattr(chat, "is_forum", None), cfg.admin_topic_id)
    except Exception:
        logger.exception("Cannot reach admin group %s — add the bot to it and give it permission to post.", cfg.admin_group_id)


def main():
    check_parity()
    cfg = load_config()
    request = HTTPXRequest(
        connect_timeout=20.0,
        read_timeout=20.0,
        write_timeout=20.0,
        pool_timeout=20.0,
        media_write_timeout=60.0,
        http_version="1.1",
        # HTTPX transport retries connection failures, not ambiguous request timeouts.
        httpx_kwargs={"transport": httpx.AsyncHTTPTransport(retries=3)},
    )
    app = ApplicationBuilder().token(cfg.token).request(request).post_init(post_init).build()
    app.bot_data["cfg"] = cfg
    app.bot_data["db"] = DB(cfg.db_path)

    in_admin = filters.Chat(chat_id=cfg.admin_group_id)
    private = filters.ChatType.PRIVATE

    # ---- counselors (admin group)
    app.add_handler(CommandHandler("stats", admin.cmd_stats, filters=in_admin))
    app.add_handler(CommandHandler("open", admin.cmd_open, filters=in_admin))
    app.add_handler(CommandHandler("chatinfo", admin.cmd_chatinfo))
    app.add_handler(CallbackQueryHandler(admin.on_admin_action, pattern=r"^adm:(claim|resolve|flag):\d+$"))
    app.add_handler(MessageHandler(in_admin & filters.REPLY & filters.TEXT & ~filters.COMMAND, admin.on_admin_reply))

    # ---- students (private chats)
    for name, fn in [("start", student.cmd_start), ("menu", student.cmd_menu), ("language", student.cmd_language),
                     ("help", student.cmd_help), ("cancel", student.cmd_cancel)]:
        app.add_handler(CommandHandler(name, fn))

    cb = app.add_handler
    cb(CallbackQueryHandler(student.on_lang, pattern=r"^lang:(en|am)$"))
    cb(CallbackQueryHandler(student.on_go, pattern=r"^go:(start|home|book|pray|call|tgchat|webform|verse|conv|set)$"))
    cb(CallbackQueryHandler(student.on_back, pattern=r"^fl:back$"))
    cb(CallbackQueryHandler(student.on_choice, pattern=r"^fl:set:(topic|ptype|pcat|day|slot|who):\w+$"))
    cb(CallbackQueryHandler(student.on_option, pattern=r"^fl:opt:(anon|urgent|share)$"))
    cb(CallbackQueryHandler(student.on_skip, pattern=r"^fl:skip$"))
    cb(CallbackQueryHandler(student.on_restart, pattern=r"^fl:restart$"))
    cb(CallbackQueryHandler(student.on_send, pattern=r"^fl:send$"))
    cb(CallbackQueryHandler(student.on_conv, pattern=r"^cv:(open|reply|close|nclose):\d+$"))
    cb(CallbackQueryHandler(student.on_feedback, pattern=r"^fb:\d+:[123]$"))
    cb(CallbackQueryHandler(student.on_verse_nav, pattern=r"^vs:\d+$"))
    cb(CallbackQueryHandler(student.on_subscribe, pattern=r"^sub:(verse|set|off)$"))
    cb(CallbackQueryHandler(student.on_settings, pattern=r"^st:(lang|privacy|about|delete|delete_yes)$"))

    app.add_handler(MessageHandler(private & filters.CONTACT, student.on_contact))
    app.add_handler(MessageHandler(private & filters.TEXT & ~filters.COMMAND, student.on_text))
    app.add_handler(MessageHandler(private & ~filters.TEXT & ~filters.COMMAND & ~filters.CONTACT, student.on_other_media))

    app.add_error_handler(on_error)

    if app.job_queue:
        app.job_queue.run_daily(student.send_daily_verse, time=dtime(cfg.verse_hour, 0, tzinfo=cfg.tz), name="daily_verse")
        logger.info("Daily verse scheduled for %02d:00 %s", cfg.verse_hour, cfg.tz.key)
    else:
        logger.warning("JobQueue unavailable — install python-telegram-bot[job-queue] to enable the daily verse.")

    logger.info("ACU bot starting…")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
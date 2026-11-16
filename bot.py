import os
import logging
from datetime import date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ---------- Logging ----------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ---------- Config ----------
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_GROUP_ID = int(os.getenv("ADMIN_GROUP_ID", "-1003708384374"))

if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set!")

# ---------- State constants ----------
WAITING_COUNSELING = "WAITING_FOR_COUNSELING_MSG"
WAITING_BOOKING    = "WAITING_FOR_BOOKING"
WAITING_PRAYER     = "WAITING_FOR_PRAYER"

# In-memory map: admin_group_message_id -> student_chat_id
# (Wiped on restart — acceptable tradeoff, see notes below)
reply_map: dict[int, int] = {}

# ---------- Daily verses ----------
VERSES = [
    ("Do not be anxious about anything, but in everything, by prayer and petition, "
     "with thanksgiving, present your requests to God.", "Philippians 4:6"),
    ("The Lord is my shepherd; I shall not want.", "Psalm 23:1"),
    ("I can do all things through him who strengthens me.", "Philippians 4:13"),
    ("Cast all your anxiety on him because he cares for you.", "1 Peter 5:7"),
    ("Be strong and courageous. Do not be afraid; do not be discouraged.", "Joshua 1:9"),
    ("Come to me, all who labor and are heavy laden, and I will give you rest.", "Matthew 11:28"),
    ("Trust in the Lord with all your heart and lean not on your own understanding.", "Proverbs 3:5"),
]

# ---------- Main menu keyboard ----------
def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Share My Problem Anonymously", callback_data="counseling")],
        [InlineKeyboardButton("📞 Talk Directly by Phone", callback_data="phone")],
        [InlineKeyboardButton("📅 Request a Face-to-Face Appointment", callback_data="booking")],
        [InlineKeyboardButton("🙏 Submit a Prayer Request", callback_data="prayer")],
        [InlineKeyboardButton("📖 Automatic Words of Comfort", callback_data="verse")],
        [InlineKeyboardButton("ℹ️ About the Service", callback_data="about")],
    ])

# ---------- /start ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user = update.effective_user
    text = (
        f"Hello, hello **{user.first_name}**! ✝️✨\n\n"
        "Welcome to the Arba Minch University Christian Fellowship (ACU) Counseling Bot.\n\n"
        "Here, you can share any psychological struggles, academic stress, or spiritual "
        "questions with complete confidentiality (anonymous). You are never alone! 🤝\n\n"
        "Please select what you would like to do from the options below:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu())

# ---------- Button handler ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "counseling":
        context.user_data["state"] = WAITING_COUNSELING
        await query.edit_message_text(
            "✍️ That's great!\n\n"
            "Please write down your feelings, worries, or questions here.\n\n"
            "(Your message will be forwarded confidentially to our counselors, "
            "and they will reply to you through this same bot.)"
        )

    elif data == "phone":
        await query.edit_message_text(
            "📞 If You Want to Talk by Phone:\n\n"
            "If your situation is urgent, you can contact the fellowship counselors "
            "on campus directly by phone. (Your call will be treated with complete confidentiality.)\n\n"
            "👨‍💻 Brother [Name]: 0911223344\n"
            "👩‍💻 Sister [Name]: 0998877665\n\n"
            "(Please call only during convenient service hours.)",
            reply_markup=main_menu(),
        )

    elif data == "booking":
        context.user_data["state"] = WAITING_BOOKING
        await query.edit_message_text(
            "📅 Face-to-Face Appointment Request:\n\n"
            "If you would like to meet with a counselor in person on campus, please "
            "briefly write down your preferred day and time (e.g., Saturday afternoon) "
            "and your contact phone number here."
        )

    elif data == "prayer":
        context.user_data["state"] = WAITING_PRAYER
        await query.edit_message_text(
            "🙏 Prayer Request Box:\n\n"
            "Please write your prayer request or whatever burden you are carrying.\n\n"
            "Your message will be delivered only to the Fellowship's Prayer Department."
        )

    elif data == "verse":
        verse, ref = VERSES[date.today().toordinal() % len(VERSES)]
        await query.edit_message_text(
            f"📖 Today's Bible Verse and Words of Comfort:\n\n"
            f"\"{verse}\"\n\n— {ref}\n\n"
            "God is with you! Remain strong in prayer. ✨",
            reply_markup=main_menu(),
        )

    elif data == "about":
        await query.edit_message_text(
            "ℹ️ About the Service:\n\n"
            "This bot was developed by the Counseling Department of Arba Minch University "
            "Christian Fellowship (ACU).\n\n"
            "It is a free platform designed to help students receive spiritual and "
            "psychological support.\n\nIf you have any questions or suggestions, you can "
            "share them through this bot.\n\nGod bless you! 🙏",
            reply_markup=main_menu(),
        )

# ---------- Text message handler ----------
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")
    user = update.effective_user
    text = update.message.text

    if state == WAITING_COUNSELING:
        sent = await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=f"📩 New Counseling Request (Anonymous):\n\n{text}",
        )
        reply_map[sent.message_id] = user.id
        context.user_data.clear()
        await update.message.reply_text(
            "✅ Your message has been sent confidentially to our counselors.\n\n"
            "You will receive a response soon.\n\nGod bless you! 🙏"
        )

    elif state == WAITING_BOOKING:
        sent = await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=(
                f"📅 New Appointment Request:\n"
                f"- Student Username: @{user.username or 'N/A'}\n"
                f"- Details: {text}"
            ),
        )
        reply_map[sent.message_id] = user.id
        context.user_data.clear()
        await update.message.reply_text(
            "✅ Your appointment request has been received!\n\n"
            "The responsible counselors will contact you privately soon. 🙏"
        )

    elif state == WAITING_PRAYER:
        sent = await context.bot.send_message(
            chat_id=ADMIN_GROUP_ID,
            text=f"🙏 New Prayer Request (Anonymous):\n\n{text}",
        )
        reply_map[sent.message_id] = user.id
        context.user_data.clear()
        await update.message.reply_text(
            "✅ Your prayer request has been delivered to the prayer team.\n\n"
            "We will pray together! ✝️"
        )

    else:
        await update.message.reply_text(
            "Please press /start first and select what you need from the menu. 📌"
        )

# ---------- Admin reply handler ----------
async def admin_reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if msg is None or msg.reply_to_message is None:
        return
    if msg.chat_id != ADMIN_GROUP_ID:
        return

    original_id = msg.reply_to_message.message_id
    student_chat_id = reply_map.get(original_id)

    if student_chat_id is None:
        await msg.reply_text(
            "⚠️ Could not find the original student for this reply. "
            "(The bot may have restarted since the student's message was received.)"
        )
        return

    try:
        await context.bot.send_message(
            chat_id=student_chat_id,
            text=f"💬 Reply from counselor:\n\n{msg.text}",
        )
        await msg.reply_text("✅ Reply delivered to the student.")
    except Exception as e:
        logger.exception("Failed to deliver reply")
        await msg.reply_text(f"⚠️ Failed to deliver: {e}")

# ---------- Main ----------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, message_handler
    ))
    # Admin replies come as group messages that are replies — this catches them
    app.add_handler(MessageHandler(
        filters.Chat(chat_id=ADMIN_GROUP_ID) & filters.REPLY, admin_reply_handler
    ))

    logger.info("Bot starting...")
    app.run_polling()

if __name__ == "__main__":
    main()
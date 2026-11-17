"""All user-facing copy. Every key must exist in BOTH languages (verified at startup and in tests)."""
from __future__ import annotations

EN: dict[str, str] = {
    # ---- chrome
    "brand": "✝️ <b>ACU Counseling</b>",
    "step": "Step {i} of {n}",
    "lang_name": "English",
    "on": "On",
    "off": "Off",
    # ---- buttons (global)
    "btn_home": "🏠 Menu",
    "btn_back": "⬅️ Back",
    "btn_cancel": "✖️ Cancel",
    "btn_send": "✅ Send",
    "btn_rewrite": "✏️ Rewrite",
    "btn_restart": "🔄 Start over",
    "btn_skip": "Skip →",
    "btn_reply": "↩️ Reply",
    "btn_close": "✅ Close conversation",
    "btn_start": "▶️ Get started",
    # ---- welcome & menu
    "welcome_title": "Welcome, {name}",
    "welcome_body": (
        "You are not alone, and you don't have to carry this by yourself.\n\n"
        "🔒 <b>Private</b> — anonymous by default. Counselors never see your name unless you choose to share it.\n"
        "🤝 <b>Caring</b> — brothers and sisters from the fellowship reply to you personally.\n"
        "🆓 <b>Free</b> — for every student, always.\n\n"
        "Ready when you are."
    ),
    "menu_title_new": "How can we support you?",
    "menu_title_back": "Welcome back, {name}",
    "menu_body": "You are safe here. Choose the way that feels most comfortable for you.",
    "btn_verse": "📖 Verse of the day",
    "btn_conv": "🗂 My conversations",
    "btn_settings": "⚙️ Settings",
    "opt_inperson": "🤝 Meet in Person",
    "opt_phone": "📞 Phone Call",
    "opt_tg": "💬 Telegram Chat",
    "opt_web": "🌐 Web Form",
    "tg_title": "Chat with a Counselor",
    "tg_body": (
        "You are about to connect directly with a counselor from our fellowship team. "
        "We are here to listen and support you with care.\n\n"
        "🤝 <b>Who will I talk to?</b>\nA trusted brother or sister from the ACU counseling team.\n\n"
        "🔒 <b>Is it private?</b>\nYour Telegram profile name may be visible. Standard Telegram chats are not "
        "end-to-end encrypted by default, and Telegram handles messages under its own privacy practices. "
        "Please share only what you feel comfortable sending.\n\n"
        "Tap below to start chatting. We are ready to listen. 🤍"
    ),
    "btn_open_tg": "💬 Start Telegram Chat",
    "web_title": "Web Form",
    "web_body": (
        "Prefer to use a form? Open it below. Whether identifying details are requested depends on the form settings. "
        "The form provider may process technical data and submissions; review its privacy information and share only "
        "what you're comfortable sending."
    ),
    "btn_open_web": "🌐 Open Web Form",
    # ---- review screen
    "review_title": "Review & send",
    "lbl_topic": "Topic",
    "lbl_type": "Type",
    "lbl_day": "Day",
    "lbl_time": "Time",
    "lbl_who": "Counselor",
    "lbl_contact": "Contact",
    "lbl_note": "Note",
    "lbl_started": "Started",
    "lbl_status": "Status",
    "note_anon_on": "🔒 Sent anonymously — counselors won't see your name.",
    "note_anon_off": "👤 Counselors will see your name and Telegram username.",
    "note_urgent": "🔔 Marked as urgent.",
    "note_share": "📣 You allow the team to share this testimony with the fellowship.",
    "note_noshare": "🔒 This testimony stays with the team only.",
    "opt_anon_on": "🔒 Anonymous: On",
    "opt_anon_off": "👤 Anonymous: Off",
    "opt_urgent_on": "🔔 Urgent: On",
    "opt_urgent_off": "🔔 Urgent: Off",
    "opt_share_on": "📣 Share with fellowship: On",
    "opt_share_off": "📣 Share with fellowship: Off",
    "crisis_title": "You matter",
    "crisis_body": (
        "We read that you may be hurting deeply, so we marked your message <b>urgent</b> "
        "and a counselor will respond as soon as possible.\n\n"
        "If you are in immediate danger or thinking of harming yourself, please don't wait — "
        "call emergency services or go to someone near you right now.\n\n{contacts}"
    ),
    # ---- call
    "call_title": "Talk by Phone",
    "call_body": (
        "Sometimes hearing a friendly voice can help. You can call our counselors directly.\n\n"
        "📞 <b>Counselor contacts:</b>\n{contacts}\n\n"
        "{hours}"
        "⚠️ <i>If you are in immediate danger or facing a life-threatening emergency, contact local emergency "
        "services right away.</i>"
    ),
    "hours_line": "🕘 <b>Service Hours:</b> {hours}\n\n",
    "no_contacts": "(Contact numbers will be added soon.)",
    # ---- booking
    "book_title": "Book a meeting",
    "book_day_body": "Which day suits you best?",
    "day_0": "Mon", "day_1": "Tue", "day_2": "Wed", "day_3": "Thu", "day_4": "Fri", "day_5": "Sat", "day_6": "Sun",
    "day_any": "Any day",
    "book_time_body": "What time of day works for you?",
    "slot_morning": "🌅 Morning",
    "slot_afternoon": "☀️ Afternoon",
    "slot_evening": "🌇 Evening",
    "slot_any": "🕐 Any time",
    "book_who_body": "Would you prefer to meet a brother or a sister?",
    "who_brother": "👨 Brother",
    "who_sister": "👩 Sister",
    "who_any": "🤝 No preference",
    "book_contact_body": (
        "How can we reach you to confirm?\n"
        "Tap <b>Share my phone number</b> below, or simply type your number."
    ),
    "kb_hint": "👇 Use the buttons below",
    "kb_share": "📱 Share my phone number",
    "kb_skip": "Skip — contact me on Telegram",
    "contact_ok": "✅ Got it, thank you.",
    "contact_skip_ok": "👌 We'll contact you here on Telegram.",
    "contact_bad": "That doesn't look like a phone number. Please use the button or type digits only (e.g. 0911 223 344).",
    "contact_tg": "Telegram (@{u})",
    "book_note_body": "Anything you'd like the counselor to know beforehand?\n<i>(optional)</i>",
    "book_review_foot": "A counselor will confirm your appointment privately.",
    "btn_send_request": "✅ Send request",
    "sent_book_title": "Request sent",
    "sent_book_body": (
        "Your reference: <b>{ref}</b>\n\n"
        "A counselor will contact you privately to confirm the time. 🙏\n\n"
        "⏱ We usually reply within {sla}."
    ),
    # ---- prayer & testimony
    "pray_title": "Prayer & testimony",
    "pray_type_body": "What would you like to share with us?",
    "ptype_prayer": "🙏 Prayer request",
    "ptype_testimony": "🕊 Testimony",
    "pray_cat_body": "What is your prayer about?",
    "pcat_heal": "🩹 Healing & health",
    "pcat_study": "🎓 Studies & exams",
    "pcat_family": "🏠 Family",
    "pcat_guide": "🧭 Guidance",
    "pcat_other": "🧩 Other",
    "pray_write_prayer": (
        "<b>Topic:</b> {topic}\n\n"
        "✍️ Write your prayer request, or whatever burden you are carrying. Our prayer team will lift it up.\n\n"
        "🔒 Your name stays hidden unless you choose otherwise."
    ),
    "pray_write_testimony": "✍️ Tell us what God has done in your life.\nYour story can encourage others!",
    "sent_prayer_title": "Prayer received",
    "sent_prayer_body": (
        "Your reference: <b>{ref}</b>\n\n"
        "🙏 Our prayer team will pray for you. You are not alone. "
        "If someone wishes to encourage you, their message will appear right here."
    ),
    "sent_testi_title": "Thank you for sharing",
    "sent_testi_body": "Your reference: <b>{ref}</b>\n\n🕊 Praise God! Your testimony has reached the team.",
    # ---- follow-up reply
    "reply_title": "Your reply",
    "reply_body": "✍️ Write your reply to the counselor ({ref}):",
    "reply_sent_title": "Reply sent",
    "reply_sent_body": "A counselor will get back to you. 🙏",
    # ---- conversations
    "conv_title": "My conversations",
    "conv_body": "Tap a conversation to reply or close it.\n\n🟡 waiting for a counselor · 🟢 reply received · ✅ closed",
    "conv_empty": "You have no conversations yet.\nWhenever you're ready, we're here. 🤍",
    "kind_counseling": "Counseling",
    "kind_booking": "Appointment",
    "kind_prayer": "Prayer request",
    "kind_testimony": "Testimony",
    "status_open": "🟡 Waiting for a counselor",
    "status_answered": "🟢 Reply received — your turn",
    "status_closed": "✅ Closed",
    "closed_toast": "✅ Conversation closed",
    "from_counselor": "💬 <b>Reply from your counselor</b> · {ref}",
    "taken_note": "👀 A counselor has picked up your message ({ref}) and will reply soon.",
    "resolved_note": "✅ Your conversation {ref} was marked complete by the team.\n\nHow was your experience?",
    "fb_3": "😊 Helpful",
    "fb_2": "😐 Okay",
    "fb_1": "😕 Not really",
    "fb_thanks": "🙏 Thank you for your feedback.",
    # ---- verse
    "verse_title": "Verse of the day",
    "btn_more_verse": "➡️ Another verse",
    "btn_sub_on": "🔔 Send me a verse every morning",
    "btn_sub_off": "🔕 Stop the daily verse",
    "daily_head": "☀️ <b>Good morning</b>",
    "sub_on_toast": "🔔 Daily verse is on",
    "sub_off_toast": "🔕 Daily verse is off",
    # ---- settings
    "set_title": "Settings",
    "set_body": "<b>Language:</b> {language}\n<b>Daily verse:</b> {verse}",
    "btn_set_lang": "🌐 Language",
    "btn_set_verse_on": "🔔 Daily verse: On",
    "btn_set_verse_off": "🔕 Daily verse: Off",
    "btn_privacy": "🔒 Privacy & data",
    "btn_about": "ℹ️ About",
    "btn_delete": "🗑 Delete my data",
    "privacy_title": "Privacy & data",
    "privacy_body": (
        "<b>What we keep</b>\n"
        "• Your Telegram ID — only to deliver replies to you\n"
        "• Your language and settings\n"
        "• Conversation status (the bot does not store message text)\n\n"
        "<b>What counselors see</b>\n"
        "• Anonymous: only your message and its topic\n"
        "• Shared: your name and Telegram username\n\n"
        "Messages are visible only to counselors in the private team group. "
        "You can delete your data at any time from Settings."
    ),
    "about_title": "About the service",
    "about_body": (
        "This bot was developed by the Counseling Department of Arba Minch University "
        "Christian Fellowship (ACU).\n\n"
        "It is a free space for students to receive spiritual and emotional support — "
        "with care, confidentiality and prayer.\n\n"
        "God bless you! 🙏"
    ),
    "delete_title": "Delete my data",
    "delete_body": (
        "This deletes your settings and disconnects all your conversations, so counselors "
        "will no longer be able to reply to you.\n\nThis cannot be undone."
    ),
    "btn_delete_yes": "🗑 Yes, delete everything",
    "deleted_msg": "✅ Your data was deleted. Send /start any time to begin again.",
    # ---- help & errors
    "help_title": "Help",
    "help_body": (
        "/start – main menu\n/menu – back to the menu\n/language – change language\n"
        "/cancel – cancel what you're doing\n/help – this message"
    ),
    "cancelled": "Cancelled.",
    "err_send": "⚠️ Sorry, we couldn't deliver that right now. Please try again in a moment.",
    "err_expired": "That session expired — let's start again from the menu.",
    "err_cooldown": "⏳ Please wait {s}s before sending again.",
    "err_long": "⚠️ That's a bit too long. Please keep it under {max} characters.",
    "err_empty": "Please write a message before sending.",
    "err_text_only": "Please send text only for now. ✍️",
    "hint_buttons": "Please use the buttons above 👆",
    "no_flow": "To write to us, tap <b>Talk to a counselor</b> below. 🤍",
}

AM: dict[str, str] = {
    "brand": "✝️ <b>ACU የምክር አገልግሎት</b>",
    "step": "ደረጃ {i} ከ{n}",
    "lang_name": "አማርኛ",
    "on": "በርቷል",
    "off": "ጠፍቷል",
    "btn_home": "🏠 ማውጫ",
    "btn_back": "⬅️ ተመለስ",
    "btn_cancel": "✖️ ሰርዝ",
    "btn_send": "✅ ላክ",
    "btn_rewrite": "✏️ እንደገና ጻፍ",
    "btn_restart": "🔄 እንደገና ጀምር",
    "btn_skip": "ዝለል →",
    "btn_reply": "↩️ ምላሽ ስጥ",
    "btn_close": "✅ ንግግሩን ዝጋ",
    "btn_start": "▶️ እንጀምር",
    "welcome_title": "እንኳን ደህና መጡ፣ {name}",
    "welcome_body": (
        "ብቻዎን አይደሉም፤ ይህን ሸክም ብቻዎን መሸከም የለብዎትም።\n\n"
        "🔒 <b>ምስጢራዊ</b> — በነባሪ ስምዎ አይገለጥም። እርስዎ ካልፈቀዱ አማካሪዎች ስምዎን አያዩም።\n"
        "🤝 <b>አሳቢ</b> — ከኅብረቱ የሆኑ ወንድሞችና እህቶች በግል ምላሽ ይሰጡዎታል።\n"
        "🆓 <b>ነጻ</b> — ለሁሉም ተማሪ ሁልጊዜ ነጻ ነው።\n\n"
        "ዝግጁ ሲሆኑ ይጀምሩ።"
    ),
    "menu_title_new": "እንዴት ልንረዳዎት እንችላለን?",
    "menu_title_back": "እንኳን ደህና መጡ፣ {name}",
    "menu_body": "እዚህ ደህና ነዎት። ለእርስዎ ምቹ የሆነውን መንገድ ይምረጡ።",
    "btn_verse": "📖 የዕለቱ ጥቅስ",
    "btn_conv": "🗂 ንግግሮቼ",
    "btn_settings": "⚙️ ቅንብሮች",
    "opt_inperson": "🤝 ፊት ለፊት መገናኘት",
    "opt_phone": "📞 ስልክ ለስልክ",
    "opt_tg": "💬 የቴሌግራም ቻት",
    "opt_web": "🌐 የድረ-ገጽ ቅጽ",
    "tg_title": "ከአማካሪ ጋር መወያየት",
    "tg_body": (
        "በቀጥታ ከኅብረታችን አማካሪ ጋር ይገናኛሉ። በጥንቃቄ ለማዳመጥና ለመደገፍ ዝግጁ ነን።\n\n"
        "🤝 <b>ከማን ጋር ነው የማወያየው?</b>\nከታመነ የ ACU የምክር ቡድን ወንድም ወይም እህት ጋር።\n\n"
        "🔒 <b>ምስጢራዊ ነው?</b>\nየቴሌግራም መገለጫ ስምዎ ሊታይ ይችላል። መደበኛ የቴሌግራም ውይይቶች "
        "በነባሪ ከጫፍ እስከ ጫፍ የተመሰጠሩ አይደሉም፤ ቴሌግራምም መልእክቶችን በራሱ የግላዊነት መመሪያ "
        "መሠረት ያስተናግዳል። ለመላክ የሚመችዎትን ብቻ ያካፍሉ።\n\n"
        "ውይይቱን ለመጀመር ከታች ይጫኑ። ለማዳመጥ ዝግጁ ነን። 🤍"
    ),
    "btn_open_tg": "💬 የቴሌግራም ውይይት ጀምር",
    "web_title": "የድረ-ገጽ ቅጽ",
    "web_body": (
        "ቅጽ መጠቀም ይመርጣሉ? ከታች ይክፈቱት። መለያ መረጃ መጠየቁ በቅጹ ቅንብሮች ላይ ይመረኮዛል። "
        "የቅጹ አቅራቢ ቴክኒካዊ መረጃዎችንና የተላኩ መልእክቶችን ሊያስተናግድ ይችላል፤ ስለዚህ ስለ ግላዊነት መረጃውን ይመልከቱና "
        "ለመጋራት የሚመችዎትን ብቻ ያካፍሉ።"
    ),
    "btn_open_web": "🌐 የድረ-ገጽ ቅጽ ክፈት",
    "review_title": "ይፈትሹና ይላኩ",
    "lbl_topic": "ርዕስ",
    "lbl_type": "ዓይነት",
    "lbl_day": "ቀን",
    "lbl_time": "ሰዓት",
    "lbl_who": "አማካሪ",
    "lbl_contact": "መገናኛ",
    "lbl_note": "ማስታወሻ",
    "lbl_started": "የተጀመረው",
    "lbl_status": "ሁኔታ",
    "note_anon_on": "🔒 ማንነትዎ ሳይገለጥ ይላካል።",
    "note_anon_off": "👤 አማካሪዎች ስምዎንና የቴሌግራም መጠሪያዎን ያያሉ።",
    "note_urgent": "🔔 አስቸኳይ ተብሎ ምልክት ይደረግበታል።",
    "note_share": "📣 ቡድኑ ይህን ምስክርነት ለኅብረቱ እንዲያካፍል ፈቅደዋል።",
    "note_noshare": "🔒 ይህ ምስክርነት ለቡድኑ ብቻ ይቀራል።",
    "opt_anon_on": "🔒 ስም መደበቅ፦ አዎ",
    "opt_anon_off": "👤 ስም መደበቅ፦ አይ",
    "opt_urgent_on": "🔔 አስቸኳይ፦ አዎ",
    "opt_urgent_off": "🔔 አስቸኳይ፦ አይ",
    "opt_share_on": "📣 ለኅብረቱ ይጋራ፦ አዎ",
    "opt_share_off": "📣 ለኅብረቱ ይጋራ፦ አይ",
    "crisis_title": "እርስዎ ዋጋ አለዎት",
    "crisis_body": (
        "በጣም እየተጎዱ እንደሆነ ስላነበብን መልእክትዎን <b>አስቸኳይ</b> ብለን ምልክት አድርገናል፤ "
        "አማካሪ በተቻለ ፍጥነት ይመልስልዎታል።\n\n"
        "አፋጣኝ አደጋ ላይ ከሆኑ ወይም ራስዎን ለመጉዳት እያሰቡ ከሆነ አይጠብቁ — "
        "አሁኑኑ ለድንገተኛ አገልግሎት ይደውሉ ወይም በአቅራቢያዎ ወዳለ ሰው ይሂዱ።\n\n{contacts}"
    ),
    "call_title": "በስልክ ማውራት",
    "call_body": (
        "አንዳንድ ጊዜ ወዳጃዊ ድምፅ መስማት ሊያጽናና ይችላል። አማካሪዎቻችንን በቀጥታ መደወል ይችላሉ።\n\n"
        "📞 <b>የአማካሪዎች ስልክ:</b>\n{contacts}\n\n"
        "{hours}"
        "⚠️ <i>አፋጣኝ አደጋ ላይ ከሆኑ ወይም ሕይወትዎን በሚያስፈራ ሁኔታ ውስጥ ከሆኑ፣ "
        "እባክዎን ወዲያውኑ የአካባቢውን የአስቸኳይ አገልግሎት ያነጋግሩ።</i>"
    ),
    "hours_line": "🕘 <b>የአገልግሎት ሰዓት:</b> {hours}\n\n",
    "no_contacts": "(የስልክ ቁጥሮች በቅርቡ ይጨመራሉ።)",
    "book_title": "ቀጠሮ መያዝ",
    "book_day_body": "የትኛው ቀን ይመችዎታል?",
    "day_0": "ሰኞ", "day_1": "ማክሰኞ", "day_2": "ረቡዕ", "day_3": "ሐሙስ", "day_4": "አርብ", "day_5": "ቅዳሜ", "day_6": "እሑድ",
    "day_any": "ማንኛውም ቀን",
    "book_time_body": "የቀኑ የትኛው ክፍል ይመችዎታል?",
    "slot_morning": "🌅 ጠዋት",
    "slot_afternoon": "☀️ ከሰዓት",
    "slot_evening": "🌇 ምሽት",
    "slot_any": "🕐 ማንኛውም ሰዓት",
    "book_who_body": "ከወንድም ወይስ ከእህት አማካሪ ጋር መገናኘት ይመርጣሉ?",
    "who_brother": "👨 ወንድም",
    "who_sister": "👩 እህት",
    "who_any": "🤝 ልዩነት የለውም",
    "book_contact_body": (
        "ቀጠሮውን ለማረጋገጥ እንዴት እናገኝዎ?\n"
        "ከታች ያለውን <b>ስልክ ቁጥሬን አጋራ</b> ይጫኑ፤ ወይም ቁጥርዎን ብቻ ይጻፉ።"
    ),
    "kb_hint": "👇 ከታች ያሉትን ቁልፎች ይጠቀሙ",
    "kb_share": "📱 ስልክ ቁጥሬን አጋራ",
    "kb_skip": "ዝለል — በቴሌግራም ያግኙኝ",
    "contact_ok": "✅ ተቀብለናል፣ አመሰግናለሁ።",
    "contact_skip_ok": "👌 እዚሁ በቴሌግራም እናነጋግርዎታለን።",
    "contact_bad": "ይህ የስልክ ቁጥር አይመስልም። እባክዎ ቁልፉን ይጠቀሙ ወይም ቁጥሮቹን ብቻ ይጻፉ (ለምሳሌ 0911 223 344)።",
    "contact_tg": "ቴሌግራም (@{u})",
    "book_note_body": "አማካሪው አስቀድሞ እንዲያውቀው የሚፈልጉት ነገር አለ?\n<i>(አማራጭ)</i>",
    "book_review_foot": "አማካሪ ቀጠሮዎን በግል ያረጋግጣል።",
    "btn_send_request": "✅ ጥያቄውን ላክ",
    "sent_book_title": "ጥያቄዎ ተልኳል",
    "sent_book_body": (
        "የማጣቀሻ ቁጥርዎ፦ <b>{ref}</b>\n\n"
        "አማካሪ ሰዓቱን ለማረጋገጥ በግል ያነጋግርዎታል። 🙏\n\n"
        "⏱ ብዙውን ጊዜ በ{sla} ውስጥ እንመልሳለን።"
    ),
    "pray_title": "ጸሎትና ምስክርነት",
    "pray_type_body": "ምን ማካፈል ይፈልጋሉ?",
    "ptype_prayer": "🙏 የጸሎት ጥያቄ",
    "ptype_testimony": "🕊 ምስክርነት",
    "pray_cat_body": "ጸሎቱ ስለ ምንድን ነው?",
    "pcat_heal": "🩹 ፈውስና ጤና",
    "pcat_study": "🎓 ትምህርትና ፈተና",
    "pcat_family": "🏠 ቤተሰብ",
    "pcat_guide": "🧭 መመሪያ",
    "pcat_other": "🧩 ሌላ",
    "pray_write_prayer": (
        "<b>ርዕስ፦</b> {topic}\n\n"
        "✍️ የጸሎት ጥያቄዎን ወይም የተሸከሙትን ሸክም ይጻፉ። የጸሎት ቡድናችን ያቀርበዋል።\n\n"
        "🔒 እርስዎ ካልመረጡ በቀር ስምዎ አይገለጥም።"
    ),
    "pray_write_testimony": "✍️ እግዚአብሔር በሕይወትዎ ያደረገውን ይንገሩን።\nታሪክዎ ሌሎችን ሊያበረታታ ይችላል!",
    "sent_prayer_title": "ጸሎትዎ ደርሶናል",
    "sent_prayer_body": (
        "የማጣቀሻ ቁጥርዎ፦ <b>{ref}</b>\n\n"
        "🙏 የጸሎት ቡድናችን ስለ እርስዎ ይጸልያል። ብቻዎን አይደሉም። "
        "አንድ ሰው ሊያበረታዎት ከፈለገ መልእክቱ እዚሁ ይደርስዎታል።"
    ),
    "sent_testi_title": "ስላካፈሉን እናመሰግናለን",
    "sent_testi_body": "የማጣቀሻ ቁጥርዎ፦ <b>{ref}</b>\n\n🕊 እግዚአብሔር ይመስገን! ምስክርነትዎ ለቡድኑ ደርሷል።",
    "reply_title": "ምላሽዎ",
    "reply_body": "✍️ ለአማካሪው ምላሽዎን ይጻፉ ({ref})፦",
    "reply_sent_title": "ምላሽ ተልኳል",
    "reply_sent_body": "አማካሪ በቅርቡ ይመልስልዎታል። 🙏",
    "conv_title": "ንግግሮቼ",
    "conv_body": "ለመመለስ ወይም ለመዝጋት አንዱን ንግግር ይጫኑ።\n\n🟡 የአማካሪ ምላሽ በመጠበቅ ላይ · 🟢 ምላሽ ደርሷል · ✅ ተዘግቷል",
    "conv_empty": "እስካሁን ምንም ንግግር የለዎትም።\nዝግጁ ሲሆኑ እዚህ ነን። 🤍",
    "kind_counseling": "ምክር",
    "kind_booking": "ቀጠሮ",
    "kind_prayer": "የጸሎት ጥያቄ",
    "kind_testimony": "ምስክርነት",
    "status_open": "🟡 የአማካሪ ምላሽ በመጠበቅ ላይ",
    "status_answered": "🟢 ምላሽ ደርሷል — የእርስዎ ተራ",
    "status_closed": "✅ ተዘግቷል",
    "closed_toast": "✅ ንግግሩ ተዘግቷል",
    "from_counselor": "💬 <b>ከአማካሪዎ የተላከ ምላሽ</b> · {ref}",
    "taken_note": "👀 አማካሪ መልእክትዎን ({ref}) አይቶ እየተከታተለው ነው፤ በቅርቡ ይመልስልዎታል።",
    "resolved_note": "✅ ንግግር {ref} በቡድኑ ተጠናቅቋል።\n\nተሞክሮዎ እንዴት ነበር?",
    "fb_3": "😊 ጠቃሚ ነበር",
    "fb_2": "😐 መካከለኛ",
    "fb_1": "😕 አልረዳኝም",
    "fb_thanks": "🙏 ስለ አስተያየትዎ እናመሰግናለን።",
    "verse_title": "የዕለቱ ጥቅስ",
    "btn_more_verse": "➡️ ሌላ ጥቅስ",
    "btn_sub_on": "🔔 በየጠዋቱ ጥቅስ ላክልኝ",
    "btn_sub_off": "🔕 የዕለት ጥቅስ ይቁም",
    "daily_head": "☀️ <b>እንደምን አደሩ</b>",
    "sub_on_toast": "🔔 የዕለት ጥቅስ በርቷል",
    "sub_off_toast": "🔕 የዕለት ጥቅስ ጠፍቷል",
    "set_title": "ቅንብሮች",
    "set_body": "<b>ቋንቋ፦</b> {language}\n<b>የዕለት ጥቅስ፦</b> {verse}",
    "btn_set_lang": "🌐 ቋንቋ",
    "btn_set_verse_on": "🔔 የዕለት ጥቅስ፦ በርቷል",
    "btn_set_verse_off": "🔕 የዕለት ጥቅስ፦ ጠፍቷል",
    "btn_privacy": "🔒 ግላዊነትና መረጃ",
    "btn_about": "ℹ️ ስለ አገልግሎቱ",
    "btn_delete": "🗑 መረጃዬን ሰርዝ",
    "privacy_title": "ግላዊነትና መረጃ",
    "privacy_body": (
        "<b>የምንይዘው መረጃ</b>\n"
        "• የቴሌግራም መታወቂያዎ — ምላሽ ለማድረስ ብቻ\n"
        "• ቋንቋዎና ቅንብሮችዎ\n"
        "• የንግግሩ ሁኔታ (ቦቱ የመልእክት ጽሑፍ አያስቀምጥም)\n\n"
        "<b>አማካሪዎች የሚያዩት</b>\n"
        "• ስም ሳይገለጥ ሲልኩ፦ መልእክትዎንና ርዕሱን ብቻ\n"
        "• ስም ሲያጋሩ፦ ስምዎንና የቴሌግራም መጠሪያዎን\n\n"
        "መልእክቶች በግል የአማካሪዎች ቡድን ውስጥ ብቻ ይታያሉ። "
        "መረጃዎን በማንኛውም ጊዜ ከቅንብሮች መሰረዝ ይችላሉ።"
    ),
    "about_title": "ስለ አገልግሎቱ",
    "about_body": (
        "ይህ ቦት በአርባ ምንጭ ዩኒቨርሲቲ ክርስቲያን ኅብረት (ACU) የምክር ክፍል የተሰራ ነው።\n\n"
        "ተማሪዎች መንፈሳዊና ስሜታዊ ድጋፍ በእንክብካቤ፣ በምስጢርና በጸሎት የሚያገኙበት ነጻ መድረክ ነው።\n\n"
        "እግዚአብሔር ይባርክዎ! 🙏"
    ),
    "delete_title": "መረጃዬን ሰርዝ",
    "delete_body": (
        "ይህ ቅንብሮችዎን ይሰርዛል፤ ሁሉንም ንግግሮችዎን ከእርስዎ ያላቅቃል፤ ከዚያ በኋላ አማካሪዎች "
        "ሊመልሱልዎ አይችሉም።\n\nይህ ድርጊት አይመለስም።"
    ),
    "btn_delete_yes": "🗑 አዎ፣ ሁሉንም ሰርዝ",
    "deleted_msg": "✅ መረጃዎ ተሰርዟል። እንደገና ለመጀመር በማንኛውም ጊዜ /start ይላኩ።",
    "help_title": "እገዛ",
    "help_body": (
        "/start – ዋና ማውጫ\n/menu – ወደ ማውጫ ተመለስ\n/language – ቋንቋ ቀይር\n"
        "/cancel – የጀመሩትን ሰርዝ\n/help – ይህ መልእክት"
    ),
    "cancelled": "ተሰርዟል።",
    "err_send": "⚠️ ይቅርታ፣ አሁን ማድረስ አልተቻለም። እባክዎ ከጥቂት ጊዜ በኋላ እንደገና ይሞክሩ።",
    "err_expired": "ይህ ክፍለ ጊዜ አብቅቷል — ከማውጫው እንጀምር።",
    "err_cooldown": "⏳ እባክዎ ከመላክዎ በፊት {s} ሰከንድ ይጠብቁ።",
    "err_long": "⚠️ ይህ በጣም ረጅም ነው። እባክዎ ከ{max} ቁምፊ በታች ያድርጉት።",
    "err_empty": "እባክዎ መልእክት ይጻፉ።",
    "err_text_only": "እባክዎ እስካሁን በጽሑፍ ብቻ ይላኩ። ✍️",
    "hint_buttons": "እባክዎ ከላይ ያሉትን ቁልፎች ይጠቀሙ 👆",
    "no_flow": "ሊጽፉልን ሲፈልጉ ከታች <b>ከአማካሪ ጋር ልናገር</b> ይጫኑ። 🤍",
}

T = {"en": EN, "am": AM}


def t(lang: str, key: str, **kw) -> str:
    table = T.get(lang) or EN
    s = table.get(key)
    if s is None:  # never crash a user flow over a missing translation
        s = EN[key]
    return s.format(**kw) if kw else s


def check_parity() -> None:
    missing_am = set(EN) - set(AM)
    missing_en = set(AM) - set(EN)
    if missing_am or missing_en:
        raise RuntimeError(f"Translation mismatch. Missing in AM: {sorted(missing_am)}; missing in EN: {sorted(missing_en)}")
"""Run with:  python -m pytest -q   (or simply: python tests/test_core.py)"""
import os
import re
import sqlite3
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import crisis
import texts
import ui
from db import DB, label


def test_main_menu_has_three_two_button_rows():
    rows = ui.main_menu("en").inline_keyboard
    assert len(rows) == 3
    assert all(len(row) == 2 for row in rows)
    assert [button.callback_data for row in rows for button in row] == [
        "go:book", "go:call", "go:tgchat", "go:webform", "go:verse", "go:set"
    ]


def test_translations_have_same_keys_and_placeholders():
    texts.check_parity()
    ph = re.compile(r"{(\w+)}")
    for key in texts.EN:
        assert set(ph.findall(texts.EN[key])) == set(ph.findall(texts.AM[key])), key


def test_html_tags_balanced():
    tag = re.compile(r"</?(b|i|blockquote)>")
    for lang in texts.T.values():
        for key, s in lang.items():
            opens = len(re.findall(r"<(b|i|blockquote)>", s))
            closes = len(re.findall(r"</(b|i|blockquote)>", s))
            assert opens == closes, key


def test_crisis_detection_en_am():
    assert crisis.is_crisis("Sometimes I want to die")
    assert crisis.is_crisis("ራሴን ማጥፋት እፈልጋለሁ")
    assert not crisis.is_crisis("I am stressed about my exam")


def test_db_migrates_v1_database():
    path = os.path.join(tempfile.mkdtemp(), "old.db")
    old = sqlite3.connect(path)
    old.executescript(
        "CREATE TABLE users(user_id INTEGER PRIMARY KEY, lang TEXT, last_submit REAL NOT NULL DEFAULT 0);"
        "CREATE TABLE tickets(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, user_id INTEGER NOT NULL,"
        " created REAL NOT NULL, root_msg INTEGER);"
        "CREATE TABLE admin_msgs(msg_id INTEGER PRIMARY KEY, ticket_id INTEGER NOT NULL);"
        "INSERT INTO users(user_id, lang) VALUES(7, 'am');"
        "INSERT INTO tickets(kind, user_id, created, root_msg) VALUES('counseling', 7, 1, 5);"
    )
    old.commit()
    old.close()
    db = DB(path)
    assert db.get_lang(7) == "am"
    t = db.get_ticket(1)
    assert t["status"] == "open" and t["urgent"] == 0
    assert label("counseling", 1) == "#C0001"


def test_delete_user_severs_tickets():
    db = DB(os.path.join(tempfile.mkdtemp(), "t.db"))
    db.set_lang(1, "en")
    tid = db.new_ticket("prayer", "heal", 1, False)
    db.delete_user(1)
    assert db.user(1) is None and db.get_ticket(tid)["user_id"] == 0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok ", name)
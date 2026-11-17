"""Lightweight safety net: flags messages that may signal self-harm so counselors see them first.
This is NOT a diagnosis tool — it only raises priority. Humans make every decision."""
_EN = [
    "suicide", "suicidal", "kill myself", "end my life", "want to die", "wanna die", "self harm", "self-harm",
    "hurt myself", "cut myself", "no reason to live", "better off dead", "end it all", "take my own life",
]
_AM = [
    "ራሴን ማጥፋት", "ራሴን ለማጥፋት", "ራሴን ልገድል", "ራሴን ልጎዳ", "ራሴን መጉዳት", "ራሴን አጠፋለሁ",
    "መሞት እፈልጋለሁ", "መሞት እፈልጋለው", "መኖር አልፈልግም",
    "ሕይወቴን ማጥፋት", "ህይወቴን ማጥፋት", "ሕይወቴን ለማጥፋት", "ህይወቴን ለማጥፋት",
]
_KEYWORDS = [k.casefold() for k in _EN + _AM]


def is_crisis(text: str) -> bool:
    low = (text or "").casefold()
    return any(k in low for k in _KEYWORDS)
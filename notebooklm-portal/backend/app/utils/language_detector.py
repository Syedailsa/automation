import re
from typing import Optional

ROMAN_URDU_INDICATORS = {
    "hai", "hain", "ho", "tha", "thi", "thin",
    "ko", "ka", "ke", "ki", "kay",
    "mein", "mai", "se", "par", "pe",
    "aur", "ya", "lekin", "magar",
    "yeh", "woh", "jo", "kya", "kaise",
    "nahi", "na", "mat",
    "acha", "accha", "theek", "sahi",
    "chahiye", "karna", "karo", "karein",
    "jao", "ja", "jaa", "aao", "aao", "ao",
    "mera", "meri", "mere", "tera", "teri", "tere",
    "apna", "apni", "apne",
    "kuch", "kucch", "bahut", "bohat",
    "thoda", "thodi", "zyada",
    "ye", "wo", "us", "un", "is", "in",
    "han", "haan", "nahin",
    "sakta", "sakti", "sakte", "sakta",
    "raha", "rahi", "rahe",
    "diya", "diye", "dijiye",
    "liya", "liye", "lijiye",
    "kiya", "kiye", "kijiye",
    "bataye", "batao", "bata",
    "samajh", "samjho",
    "dekho", "dekh", "dekhen",
    "sunno", "sun", "suno",
    "plzz", "plz", "thnkx", "thnx",
}

URDU_SCRIPT_RANGE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]")


def contains_urdu_script(text: str) -> bool:
    return bool(URDU_SCRIPT_RANGE.search(text))


def has_roman_urdu_vocabulary(text: str, threshold: float = 0.15) -> bool:
    words = re.findall(r"\w+", text.lower())
    if not words:
        return False
    indicator_count = sum(1 for w in words if w in ROMAN_URDU_INDICATORS)
    return indicator_count / len(words) >= threshold


def detect_language(text: str) -> str:
    if not text or not text.strip():
        return "unknown"
    if contains_urdu_script(text):
        return "ur"
    if has_roman_urdu_vocabulary(text):
        return "roman_urdu"
    return "en"


def translate_roman_urdu_hints(text: str) -> Optional[str]:
    pairs = {
        r"\bmujhe\b": "I need",
        r"\bchahiye\b": "want",
        r"\bkarna\b": "to do",
        r"\bbanao\b": "create",
        r"\bnikalo\b": "extract",
        r"\bdikhao\b": "show",
        r"\bkholo\b": "open",
        r"\bband\b": "close",
        r"\bdaalo\b": "add",
        r"\bhatao\b": "remove",
        r"\bsearch\b": "search",
    }
    result = text
    for pattern, replacement in pairs.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result if result != text else None

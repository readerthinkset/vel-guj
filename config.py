"""VELOCITY GUJARATI - language pack, brand and motion design constants."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

OUTPUT_DIR = BASE_DIR / "output"
LESSONS_DIR = OUTPUT_DIR / "lessons"
HISTORY_DIR = OUTPUT_DIR / "history"
SCENE_DIR = BASE_DIR / "scene"

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# ---------------------------------------------------------------- brand

BRAND = "VELOCITY GUJARATI"
BRAND_LOCKUP_TOP = "VELOCITY"
BRAND_LOCKUP_BOTTOM = "GUJARATI"
HANDLE = "@velocitygujarati"
MASCOT_NAME = "Velo"

# ==== LANGUAGE PACK START ====
LANGUAGE = {
    "code": "gu",
    "name": "Gujarati",
    "native_name": "ગુજરાતી",
    "history_key": "gujarati",
    "english_voice": "en-US-AvaNeural",
    "english_fallback_voice": "en-US-GuyNeural",
    "native_voice": "gu-IN-NiranjanNeural",
    "native_fallback_voice": "gu-IN-DhwaniNeural",
    "native_engine": "edge",
    "native_lang_code": "gu",
    "english_rate": "-2%",
    "native_rate": "-6%",
    "english_pitch": "+0Hz",
    "native_pitch": "+0Hz",
    "native_label": "ગુજરાતી",
    "translit_label": "SAY IT LIKE",
    "greeting": "નમસ્તે!",
    "encouragement": "સરસ!",
    "rtl": False,
    "char_tiles": False,
    "script_font": "NotoSansGujarati-Bold.ttf",
}
# ==== LANGUAGE PACK END ====

AI_MODEL = os.getenv("AI_MODEL", "gemini-fast")
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY", "")

# ---------------------------------------------------------------- timing (seconds)

INTRO_DURATION = 4.0
OUTRO_DURATION = 5.2
EN_CARD_IN = 0.55
GAP_EN_NATIVE = 0.5
NATIVE_CARD_LEAD = 0.35
GAP_BEFORE_REPEAT = 0.8
TAIL_HOLD = 1.4
MAX_REEL_DURATION = 88.0

# ---------------------------------------------------------------- palette

INK = "#3C3C3C"
MUTED = "#8A8A8A"
CREAM = "#FFF8E7"
GREEN = "#58CC02"
GREEN_DARK = "#46A302"
GREEN_DEEP = "#3D8F00"
BLUE = "#1CB0F6"
PURPLE = "#A560E8"
ORANGE = "#FF7A00"
RED = "#FF4B4B"
YELLOW = "#F5A700"
TEAL = "#00A889"
PINK = "#E056A0"

PALETTE = [GREEN, BLUE, PURPLE, ORANGE, RED, YELLOW, TEAL, PINK]

# ---------------------------------------------------------------- categories
# (english, native, icon, accent)

# ==== CATEGORY TABLE START ====
CATEGORY_TABLE = [
    ("Greetings", "નમસ્કાર", "hand", "#1CB0F6"),
    ("Basic Phrases", "મૂળભૂત શબ્દસમૂહો", "chat", "#58CC02"),
    ("Common Expressions", "સામાન્ય અભિવ્યક્તિઓ", "chat", "#1CB0F6"),
    ("Travel", "મુસાફરી", "plane", "#1CB0F6"),
    ("Restaurant", "રેસ્ટોરન્ટ", "fork", "#FF7A00"),
    ("Shopping", "ખરીદી", "bag", "#E056A0"),
    ("Emergency", "કટોકટી", "siren", "#FF4B4B"),
    ("Family Terms", "કુટુંબ શબ્દો", "heart", "#E056A0"),
    ("Numbers", "સંખ્યાઓ", "hash", "#A560E8"),
    ("Time", "સમય", "clock", "#00A889"),
    ("Motivation", "પ્રેરણા", "rocket", "#A560E8"),
    ("Love", "પ્રેમ", "heart", "#FF4B4B"),
    ("Success", "સફળતા", "trophy", "#F5A700"),
    ("Wisdom", "શાણપણ", "book", "#A560E8"),
    ("Happiness", "ખુશી", "smile", "#F5A700"),
    ("Self Improvement", "સ્વ-સુધારણા", "leaf", "#58CC02"),
    ("Gratitude", "આભાર", "heart", "#FF7A00"),
    ("Friendship", "મિત્રતા", "users", "#00A889"),
    ("Hope", "આશા", "sun", "#FF7A00"),
    ("Creativity", "સર્જનાત્મકતા", "palette", "#E056A0"),
    ("Inner Peace", "આંતરિક શાંતિ", "lotus", "#00A889"),
    ("Confidence", "આત્મવિશ્વાસ", "shield", "#1CB0F6"),
    ("Perseverance", "દ્રઢતા", "mountain", "#FF7A00"),
    ("Inspiration", "પ્રેરણા", "sparkles", "#A560E8"),
    ("Positive Life", "સકારાત્મક જીવન", "sun", "#58CC02"),
    ("Courage", "હિંમત", "shield", "#FF4B4B"),
    ("Kindness", "દયા", "heart", "#E056A0"),
    ("Patience", "ધીરજ", "hourglass", "#00A889"),
    ("Forgiveness", "ક્ષમા", "hands", "#FF7A00"),
    ("Strength", "શક્તિ", "dumbbell", "#FF4B4B"),
    ("Joy", "આનંદ", "smile", "#F5A700"),
    ("Balance", "સંતુલન", "scale", "#00A889"),
    ("Growth", "વૃદ્ધિ", "sprout", "#58CC02"),
    ("Purpose", "હેતુ", "target", "#A560E8"),
    ("Mindfulness", "સજાગતા", "lotus", "#00A889"),
    ("Daily Routine", "દૈનિક દિનચર્યા", "calendar", "#1CB0F6"),
    ("Weather", "હવામાન", "cloud", "#1CB0F6"),
    ("Feelings", "ભાવનાઓ", "smile", "#E056A0"),
    ("Food", "ખોરાક", "fork", "#FF7A00"),
    ("Health", "સ્વાસ્થ્ય", "heart", "#58CC02"),
    ("Work", "કામ", "briefcase", "#1CB0F6"),
    ("Technology", "ટેકનોલોજી", "chip", "#A560E8"),
    ("Nature", "પ્રકૃતિ", "leaf", "#58CC02"),
    ("Animals", "પ્રાણીઓ", "paw", "#FF7A00"),
    ("Colors", "રંગો", "palette", "#E056A0"),
    ("Directions", "દિશાઓ", "compass", "#1CB0F6"),
    ("Body Parts", "શરીરના અંગો", "hand", "#00A889"),
    ("Clothes", "કપડાં", "shirt", "#E056A0"),
    ("Music", "સંગીત", "music", "#A560E8"),
    ("Sports", "રમતગમત", "ball", "#FF7A00"),
    ("Holidays", "રજાઓ", "gift", "#FF4B4B"),
    ("Education", "શિક્ષણ", "book", "#1CB0F6"),
    ("Culture", "સંસ્કૃતિ", "globe", "#00A889"),
    ("Finance", "નાણાકીય", "coin", "#58CC02"),
    ("Relationships", "સંબંધો", "users", "#E056A0"),
]
# ==== CATEGORY TABLE END ====

CATEGORIES = [c[0] for c in CATEGORY_TABLE]
CATEGORIES_NATIVE = {c[0]: c[1] for c in CATEGORY_TABLE}
CATEGORY_META = {c[0]: {"native": c[1], "icon": c[2], "accent": c[3]} for c in CATEGORY_TABLE}
MAX_RECENT_CATEGORIES = 25

# ==== HASHTAGS START ====
HASHTAGS = [
    "#learngujarati",
    "#gujaratilessons",
    "#gujaratiforbeginners",
    "#languagelearning",
    "#gujarativocabulary",
    "#velocitygujarati",
    "#dailygujarati",
    "#gujarati",
    "#learnlanguages",
    "#speakgujarati",
    "#bilingual",
    "#languagetips",
]
# ==== HASHTAGS END ====

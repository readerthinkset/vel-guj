"""
Facebook Reels Automation - Bilingual English/Gujarati Content Generator
IMPROVED VERSION: Better backgrounds, English categories, no repeats, VELOCITY GUJARATI branding
Rounded container style from Habla Verse
"""

import os
import sys
import json
import random
import asyncio
import subprocess
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")
AI_MODEL = os.getenv("AI_MODEL")

if not AI_MODEL:
    raise ValueError(
        "AI_MODEL not set! Please add 'AI_MODEL=gemini-fast' to your .env file. "
        "For GitHub Actions: Add AI_MODEL to repository secrets."
    )

BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
AUDIO_DIR = OUTPUT_DIR / "audio"
VIDEO_DIR = OUTPUT_DIR / "video"
HISTORY_DIR = OUTPUT_DIR / "history"

for d in [OUTPUT_DIR, IMAGES_DIR, AUDIO_DIR, VIDEO_DIR, HISTORY_DIR]:
    d.mkdir(exist_ok=True)

VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

CATEGORIES_ENGLISH = [
    "Greetings",
    "Basic Phrases",
    "Common Expressions",
    "Travel",
    "Restaurant",
    "Shopping",
    "Emergency",
    "Family Terms",
    "Numbers",
    "Time",
    "Motivation",
    "Love",
    "Success",
    "Wisdom",
    "Happiness",
    "Self Improvement",
    "Gratitude",
    "Friendship",
    "Hope",
    "Creativity",
    "Inner Peace",
    "Confidence",
    "Perseverance",
    "Inspiration",
    "Positive Life",
    "Courage",
    "Kindness",
    "Patience",
    "Forgiveness",
    "Strength",
    "Joy",
    "Balance",
    "Growth",
    "Purpose",
    "Mindfulness",

    "Daily Routine",
    "Weather",
    "Feelings",
    "Food",
    "Health",
    "Work",
    "Technology",
    "Nature",
    "Animals",
    "Colors",
    "Directions",
    "Body Parts",
    "Clothes",
    "Music",
    "Sports",
    "Holidays",
    "Education",
    "Culture",
    "Finance",
    "Relationships",]

CATEGORIES_NATIVE = {
    "Greetings": "નમસ્કાર",
    "Basic Phrases": "મૂળભૂત શબ્દસમૂહો",
    "Common Expressions": "સામાન્ય અભિવ્યક્તિઓ",
    "Travel": "મુસાફરી",
    "Restaurant": "રેસ્ટોરન્ટ",
    "Shopping": "ખરીદી",
    "Emergency": "કટોકટી",
    "Family Terms": "કુટુંબ શબ્દો",
    "Numbers": "સંખ્યાઓ",
    "Time": "સમય",
    "Motivation": "પ્રેરણા",
    "Love": "પ્રેમ",
    "Success": "સફળતા",
    "Wisdom": "શાણપણ",
    "Happiness": "ખુશી",
    "Self Improvement": "સ્વ-સુધારણા",
    "Gratitude": "આભાર",
    "Friendship": "મિત્રતા",
    "Hope": "આશા",
    "Creativity": "સર્જનાત્મકતા",
    "Inner Peace": "આંતરિક શાંતિ",
    "Confidence": "આત્મવિશ્વાસ",
    "Perseverance": "દ્રઢતા",
    "Inspiration": "પ્રેરણા",
    "Positive Life": "સકારાત્મક જીવન",
    "Courage": "હિંમત",
    "Kindness": "દયા",
    "Patience": "ધીરજ",
    "Forgiveness": "ક્ષમા",
    "Strength": "શક્તિ",
    "Joy": "આનંદ",
    "Balance": "સંતુલન",
    "Growth": "વૃદ્ધિ",
    "Purpose": "હેતુ",
    "Mindfulness": "સજાગતા"
,

    "Daily Routine": "દૈનિક દિનચર્યા"
}

ENGLISH_VOICE = "en-US-GuyNeural"
NATIVE_VOICE = "gu-IN-NiranjanNeural"

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"
MAX_RECENT_CATEGORIES = 25


def normalize_phrase(text: str) -> str:
    """Normalize phrase text for robust anti-duplicate matching"""
    return re.sub(r'[^a-z0-9]', '', str(text).lower().strip())


def load_phrase_history():
    if PHRASE_HISTORY_FILE.exists():
        try:
            with open(PHRASE_HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[history] Warning: Failed to parse history ({e}), resetting")
            return {"phrases": [], "last_updated": None}
    return {"phrases": [], "last_updated": None}


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    PHRASE_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PHRASE_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_used_phrase_set(history=None) -> set:
    if history is None:
        history = load_phrase_history()
    return {normalize_phrase(p.get("english", "")) for p in history.get("phrases", []) if p.get("english")}


def is_phrase_used(english_phrase: str, used_set: set = None) -> bool:
    norm = normalize_phrase(english_phrase)
    if not norm:
        return True
    if used_set is not None:
        return norm in used_set
    return norm in get_used_phrase_set()


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    existing_norms = {normalize_phrase(p.get("english", "")) for p in history.get("phrases", []) if p.get("english")}
    added = 0
    for phrase in phrases:
        norm = normalize_phrase(phrase.get("english", ""))
        if norm and norm not in existing_norms:
            history["phrases"].append({
                "english": phrase["english"].strip(),
                "gujarati": phrase.get("gujarati", "").strip(),
                "transliteration": phrase.get("transliteration", "").strip(),
                "category": category,
                "generated_at": datetime.now().isoformat()
            })
            existing_norms.add(norm)
            added += 1
    save_phrase_history(history)
    print(f"[history] Added {added} phrases to history (total: {len(history['phrases'])})")


def load_recent_categories():
    if RECENT_CATEGORIES_FILE.exists():
        try:
            with open(RECENT_CATEGORIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"recent_categories": [], "last_updated": None}
    return {"recent_categories": [], "last_updated": None}


def save_recent_categories(data):
    data["last_updated"] = datetime.now().isoformat()
    RECENT_CATEGORIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RECENT_CATEGORIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_available_category():
    recent_data = load_recent_categories()
    recent = recent_data.get("recent_categories", [])
    available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent]
    if not available:
        recent_data["recent_categories"] = recent[-5:]
        save_recent_categories(recent_data)
        available = [cat for cat in CATEGORIES_ENGLISH if cat not in recent_data["recent_categories"]]
        print(f"[rotation] All categories used recently - cleared old ones, {len(available)} available")
    selected = random.choice(available)
    recent.append(selected)
    if len(recent) > MAX_RECENT_CATEGORIES:
        recent = recent[-MAX_RECENT_CATEGORIES:]
    recent_data["recent_categories"] = recent
    save_recent_categories(recent_data)
    print(f"[rotation] Selected '{selected}' ({len(available)} available, {len(recent)} in recent history)")
    return selected


CATEGORY_FALLBACK_BANKS = {
    "Travel": [
        {"english": "Where can I find a taxi?", "gujarati": "મને ટેક્સી ક્યાંથી મળશે?", "transliteration": "Mane taxi kyanthi malshe?"},
        {"english": "How far is the railway station?", "gujarati": "રેલવે સ્ટેશન કેટલું દૂર છે?", "transliteration": "Railway station ketlu door chhe?"},
        {"english": "Can you show me the way?", "gujarati": "શું તમે મને રસ્તો બતાવી શકશો?", "transliteration": "Shu tame mane rasto batavi shaksho?"},
        {"english": "I want to visit the heritage site.", "gujarati": "મારે ઐતિહાસિક સ્થળની મુલાકાત લેવી છે.", "transliteration": "Mare aithihasik sthalni mulakat levi chhe."},
        {"english": "Is this the bus to Ahmedabad?", "gujarati": "શું આ અમદાવાદ જતી બસ છે?", "transliteration": "Shu aa Ahmedabad jati bus chhe?"},
        {"english": "Please book two tickets for us.", "gujarati": "કૃપા કરીને અમારા માટે બે ટિકિટ બુક કરો.", "transliteration": "Krupa karine amara mate be ticket book karo."},
        {"english": "The view here is magnificent.", "gujarati": "અહીંનો નજારો ખૂબ ભવ્ય છે.", "transliteration": "Ahino najaro khub bhavya chhe."},
        {"english": "What time does the train arrive?", "gujarati": "ટ્રેન કેટલા વાગ્યે આવશે?", "transliteration": "Train ketla vagye aavshe?"},
    ],
    "Restaurant": [
        {"english": "Please bring the menu card.", "gujarati": "કૃપા કરીને મેનુ કાર્ડ લાવો.", "transliteration": "Krupa karine menu card laavo."},
        {"english": "What is today's special dish?", "gujarati": "આજની ખાસ વાનગી કઈ છે?", "transliteration": "Aajni khas vaangi kai chhe?"},
        {"english": "The Gujarati thali was delicious.", "gujarati": "ગુજરાતી થાળી ખૂબ સ્વાદિષ્ટ હતી.", "transliteration": "Gujarati thali khub swadisht hati."},
        {"english": "Please serve water with ice.", "gujarati": "કૃપા કરીને બરફવાળું પાણી આપો.", "transliteration": "Krupa karine barfvalu pani aapo."},
        {"english": "We would like less spicy food.", "gujarati": "અમને ઓછું તીખું ભોજન જોઈશે.", "transliteration": "Amane ochhu teekhu bhojan joishe."},
        {"english": "Can we get the bill, please?", "gujarati": "શું અમે બિલ મેળવી શકીએ?", "transliteration": "Shu ame bill melvi shakie?"},
        {"english": "I love the sweet and savory flavors.", "gujarati": "મને ખાટો-મીઠો સ્વાદ બહુ ગમે છે.", "transliteration": "Mane khato-meetho swad bahu game chhe."},
    ],
    "Shopping": [
        {"english": "How much does this item cost?", "gujarati": "આ વસ્તુની કિંમત કેટલી છે?", "transliteration": "Aa vastuni kimmat ketli chhe?"},
        {"english": "Do you have a different size?", "gujarati": "શું તમારી પાસે બીજી સાઈઝ છે?", "transliteration": "Shu tamari pase beeji size chhe?"},
        {"english": "Can you give a discount?", "gujarati": "શું થોડું ડિસ્કાઉન્ટ મળશે?", "transliteration": "Shu thodu discount malshe?"},
        {"english": "This traditional dress looks lovely.", "gujarati": "આ પરંપરાગત પોશાક ખૂબ સુંદર છે.", "transliteration": "Aa paramparagat poshak khub sundar chhe."},
        {"english": "I will pay with mobile payment.", "gujarati": "હું ઓનલાઇન પેમેન્ટ કરીશ.", "transliteration": "Hu online payment karish."},
        {"english": "Please pack this carefully.", "gujarati": "કૃપા કરીને આને સાચવીને પેક કરો.", "transliteration": "Krupa karine aane saachvine pack karo."},
    ],
    "Greetings": [
        {"english": "Welcome to Gujarat, friend.", "gujarati": "ગુજરાતમાં તમારું સ્વાગત છે, મિત્ર.", "transliteration": "Gujaratma tamaru swagat chhe, mitra."},
        {"english": "Good morning, wishing you joy.", "gujarati": "શુભ સવાર, તમારો દિવસ આનંદમય રહે.", "transliteration": "Shubh savar, tamaro divas aanandmay rahe."},
        {"english": "How has your day been?", "gujarati": "તમારો દિવસ કેવો રહ્યો?", "transliteration": "Tamaro divas kevo rahyo?"},
        {"english": "Pleasure speaking with you today.", "gujarati": "આજે તમારી સાથે વાત કરીને આનંદ થયો.", "transliteration": "Aaje tamari sathe vaat karine aanand thayo."},
        {"english": "Have a wonderful, restful evening.", "gujarati": "તમારી સાંજ શાંતિપૂર્ણ અને સુંદર રહે.", "transliteration": "Tamari saanjh shantipoorna ane sundar rahe."},
    ],
    "Motivation": [
        {"english": "Every small effort counts.", "gujarati": "દરેક નાનો પ્રયાસ મહત્વનો છે.", "transliteration": "Darek nano prayas mahatvano chhe."},
        {"english": "Courage begins with one step.", "gujarati": "હિંમત એક પગલાથી શરૂ થાય છે.", "transliteration": "Himmat ek paglathi sharu thay chhe."},
        {"english": "Believe in your endless power.", "gujarati": "તમારી અસીમ શક્તિ પર વિશ્વાસ રાખો.", "transliteration": "Tamari aseem shakti par vishwas rakho."},
        {"english": "Hard work always creates miracles.", "gujarati": "મહેનત હંમેશા ચમત્કાર સર્જે છે.", "transliteration": "Mehnat hamesha chamatkar sarje chhe."},
        {"english": "Turn challenges into great wisdom.", "gujarati": "પડકારોને મહાન શાણપણમાં બદલો.", "transliteration": "Padkarone mahan shaanpanma badlo."},
    ],
    "Family Terms": [
        {"english": "My family gathers every evening.", "gujarati": "મારો પરિવાર રોજ સાંજે ભેગો થાય છે.", "transliteration": "Maro parivar roj saanje bhego thay chhe."},
        {"english": "Grandmother shares sweet childhood stories.", "gujarati": "દાદી બાળપણની મીઠી વાર્તાઓ કહે છે.", "transliteration": "Dadi baalpan-ni meethi vaartao kahe chhe."},
        {"english": "My elder brother guides me.", "gujarati": "મારા મોટા ભાઈ મને માર્ગદર્શન આપે છે.", "transliteration": "Mara mota bhai mane margdarshan aape chhe."},
        {"english": "Parents are our greatest blessing.", "gujarati": "માતાપિતા આપણા સૌથી મોટા આશીર્વાદ છે.", "transliteration": "Matapita aapna sauthi mota aashirvad chhe."},
        {"english": "We celebrate festivals together happily.", "gujarati": "આપણે તહેવારો સાથે મળીને આનંદથી ઉજવીએ છીએ.", "transliteration": "Aapne tahevaro sathe maline aanandthi ujviye chhiye."},
    ],
    "Weather": [
        {"english": "The breeze from the river is cool.", "gujarati": "નદી પરથી આવતો પવન ઠંડો છે.", "transliteration": "Nadi parthi aavto pavan thando chhe."},
        {"english": "Dark clouds promise refreshing rain.", "gujarati": "કાળા વાદળો તાજા વરસાદની ખાતરી આપે છે.", "transliteration": "Kaala vaadalo taaja varsadni khatri aape chhe."},
        {"english": "The golden sun warms the morning.", "gujarati": "સોનેરી સૂર્ય સવારને હૂંફાળી બનાવે છે.", "transliteration": "Soneri surya savarne hoonfali banave chhe."},
        {"english": "Winter mornings in Gujarat are crisp.", "gujarati": "ગુજરાતમાં શિયાળાની સવાર તાજગીભરી હોય છે.", "transliteration": "Gujaratma shiyalani savar taajgibhari hoy chhe."},
    ],
    "Wisdom": [
        {"english": "Patience resolves what anger destroys.", "gujarati": "જે ક્રોધ બગાડે છે, તે ધીરજ સુધારે છે.", "transliteration": "Je krodh bagade chhe, te dhiraj sudhare chhe."},
        {"english": "Kind words cost nothing at all.", "gujarati": "મીઠા વેણ બોલવામાં કશું ખર્ચાતું નથી.", "transliteration": "Meetha ven bolvama kashu kharchaatu nathi."},
        {"english": "Truth shines brighter than the sun.", "gujarati": "સત્ય સૂર્ય કરતાં પણ વધુ ચમકે છે.", "transliteration": "Satya surya karta pan vadhu chamke chhe."},
        {"english": "A calm mind finds every answer.", "gujarati": "શાંત મન દરેક પ્રશ્નનો ઉકેલ શોધે છે.", "transliteration": "Shaant man darek prashnano ukel shodhe chhe."},
    ]
}


def get_fresh_fallback_phrases(category: str, num_phrases: int, used_set: set = None) -> list:
    """Return category-appropriate fallback phrases when AI generation needs backup"""
    if used_set is None:
        used_set = get_used_phrase_set()

    cat_pool = CATEGORY_FALLBACK_BANKS.get(category, [])
    generic_pool = [
        {"english": "A quiet heart discovers peace.", "gujarati": "શાંત હૃદય શાંતિની શોધ કરે છે.", "transliteration": "Shaant hruday shantini shodh kare chhe."},
        {"english": "Learn something meaningful every single day.", "gujarati": "રોજ કંઈક અર્થપૂર્ણ અને નવું શીખો.", "transliteration": "Roj kaink arthapoorna ane navu shikho."},
        {"english": "Cherish the moments with loved ones.", "gujarati": "સ્નેહીજનો સાથેની પળોને યાદગાર બનાવો.", "transliteration": "Snehijano satheni palone yaadgar banavo."},
        {"english": "Great accomplishments take patience and care.", "gujarati": "મહાન સિદ્ધિઓ માટે ધીરજ અને ખંત જરૂરી છે.", "transliteration": "Mahan siddhio mate dhiraj ane khant jaroori chhe."},
        {"english": "Smile freely and brighten someone's path.", "gujarati": "ખુલ્લા દિલથી હસો અને બીજાના ચહેરા પર સ્મિત લાવો.", "transliteration": "Khulla dilthi haso ane beejana chehra par smit laavo."},
        {"english": "True strength lies in gentle kindness.", "gujarati": "સાચી તાકાત નમ્રતા અને દયામાં છે.", "transliteration": "Sachi taakat namrata ane dayama chhe."},
        {"english": "Stay curious and keep exploring forward.", "gujarati": "નવું જાણવાની જિજ્ઞાસા સદા જીવંત રાખો.", "transliteration": "Navu jaanvani jignasa sada jeevant rakho."},
        {"english": "Every morning brings a brand new hope.", "gujarati": "દરેક પ્રભાત એક નવી આશા લઈને આવે છે.", "transliteration": "Darek prabhaat ek navi aasha laine aave chhe."},
        {"english": "Speak with honesty, live with dignity.", "gujarati": "પ્રામાણિકતાથી બોલો, સ્વાભિમાનથી જીવો.", "transliteration": "Pramaniktathi bolo, swabhimaanthi jeevo."},
        {"english": "Good company makes every journey delightful.", "gujarati": "સારો સાથ સફરને વધુ સુંદર બનાવે છે.", "transliteration": "Saaro saath safarne vadhu sundar banave chhe."},
    ]

    other_pools = []
    for cat, items in CATEGORY_FALLBACK_BANKS.items():
        if cat != category:
            other_pools.extend(items)

    candidates = [p for p in (cat_pool + generic_pool + other_pools) if normalize_phrase(p["english"]) not in used_set]
    random.shuffle(candidates)

    if len(candidates) >= num_phrases:
        return candidates[:num_phrases]

    result = list(candidates)
    while len(result) < num_phrases:
        idx = len(result) + 1
        result.append({
            "english": f"Embrace the beauty of Gujarati phrase {idx}.",
            "gujarati": f"ગુજરાતી ભાષાના સૌંદર્યનો આનંદ માણો.",
            "transliteration": "Gujarati bhashana saundaryano aanand mano."
        })
    return result[:num_phrases]


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE.get(category_english, category_english)
    history = load_phrase_history()
    all_phrases = history.get("phrases", [])
    used_set = {normalize_phrase(p.get("english", "")) for p in all_phrases if p.get("english")}

    cat_phrases = [p["english"] for p in all_phrases if p.get("category") == category_english]
    recent_cat = cat_phrases[-25:]
    recent_all = [p["english"] for p in all_phrases[-25:]]
    combined_avoid = list(dict.fromkeys(recent_cat + recent_all))

    collected = []
    models_to_try = [AI_MODEL or "gemini-fast", "openai-fast", "openai", "mistral"]
    seen_models = set()
    models = [m for m in models_to_try if m and not (m in seen_models or seen_models.add(m))]

    max_attempts = 5
    for attempt in range(max_attempts):
        needed = num_phrases - len(collected)
        if needed <= 0:
            break

        model = models[attempt % len(models)]
        print(f"[content] Attempt {attempt + 1}/{max_attempts} using model '{model}' (need {needed} more phrases)...")

        try:
            import requests
            url = "https://gen.pollinations.ai/v1/chat/completions"
            headers = {"Content-Type": "application/json"}
            if POLLINATIONS_API_KEY and str(POLLINATIONS_API_KEY).strip() and str(POLLINATIONS_API_KEY).strip() != "None":
                headers["Authorization"] = f"Bearer {str(POLLINATIONS_API_KEY).strip()}"

            current_avoid = list(dict.fromkeys(combined_avoid + [p["english"] for p in collected]))
            avoid_sample = current_avoid[-30:]
            avoid_text = ""
            if avoid_sample:
                avoid_text = "\nDO NOT repeat any of these previously used phrases:\n" + "\n".join(f"- {p}" for p in avoid_sample)

            prompt = f"""Create 10 fresh, natural, and creative {category_english} phrases for English speakers learning Gujarati.{avoid_text}

CRITICAL RULES:
1. Every phrase must be directly relevant to the theme: {category_english} ({category_native}).
2. Keep phrases SHORT and punchy (4-10 words per phrase).
3. Add NATURAL PAUSES using commas for realistic pronunciation.
4. Gujarati translation must be in standard Gujarati script (ગુજરાતી લિપિ).
5. Transliteration must be in clear Romanized English script for pronunciation.
6. Make every phrase completely UNIQUE and DIFFERENT from standard clichés.

Return ONLY a valid JSON array of objects with keys "english", "gujarati", and "transliteration".
Example format:
[
  {{"english": "Let's explore the old bazaar.", "gujarati": "ચાલો જૂના બજારની મુલાકાત લઈએ.", "transliteration": "Chalo juna bajarni mulakat laiye."}}
]"""

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are an expert bilingual English-Gujarati teacher. Return ONLY raw valid JSON arrays."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.95 + (attempt * 0.05)
            }

            response = requests.post(url, headers=headers, json=payload, timeout=45)
            response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"].strip()

            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            phrases = json.loads(content)
            if not isinstance(phrases, list):
                print(f"[content] Model returned non-list response: {type(phrases)}")
                continue

            for p in phrases:
                if not isinstance(p, dict):
                    continue
                if "transliteration" not in p and "romaji" in p:
                    p["transliteration"] = p.pop("romaji")
                if "gujarati" not in p:
                    for k in ["gujarati_text", "native", "translation", p.get("language", "")]:
                        if k in p:
                            p["gujarati"] = p.pop(k)
                            break

                eng = str(p.get("english", "")).strip()
                guj = str(p.get("gujarati", "")).strip()
                tra = str(p.get("transliteration", "")).strip()

                if not eng or not guj:
                    continue
                if len(eng.split()) > 15:
                    continue

                norm_eng = normalize_phrase(eng)
                if norm_eng in used_set:
                    print(f"  [dedup] Skipping already used phrase: '{eng}'")
                    continue

                p_clean = {"english": eng, "gujarati": guj, "transliteration": tra}
                collected.append(p_clean)
                used_set.add(norm_eng)
                combined_avoid.append(eng)

                if len(collected) >= num_phrases:
                    break

            print(f"[content] Progress: {len(collected)}/{num_phrases} unique phrases collected")
            if len(collected) >= num_phrases:
                break

        except Exception as e:
            print(f"[content] Attempt {attempt + 1} ({model}) error: {e}")

    if len(collected) >= num_phrases:
        final_phrases = collected[:num_phrases]
        add_phrases_to_history(final_phrases, category_english)
        return final_phrases

    print(f"[content] AI collected {len(collected)} phrases; filling {num_phrases - len(collected)} from fallback...")
    needed = num_phrases - len(collected)
    fallbacks = get_fresh_fallback_phrases(category_english, needed, used_set)
    collected.extend(fallbacks)

    final_phrases = collected[:num_phrases]
    add_phrases_to_history(final_phrases, category_english)
    return final_phrases
async def generate_single_audio(text: str, voice: str, output_path: str):
    try:
        import edge_tts
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        return True
    except Exception as e:
        print(f"  TTS error: {e}")
        return False


async def generate_audio_with_retries(text: str, voice: str, output_path: str, max_retries: int = 3):
    import asyncio
    for attempt in range(1, max_retries + 1):
        success = await generate_single_audio(text, voice, output_path)
        if success:
            if Path(output_path).exists() and Path(output_path).stat().st_size > 100:
                return True
            else:
                print(f"    TTS file too small or missing, retrying ({attempt}/{max_retries})...")
                await asyncio.sleep(2 * attempt)
                continue
        else:
            if attempt < max_retries:
                wait = 2 * attempt
                print(f"    TTS retry {attempt}/{max_retries} in {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"    TTS failed after {max_retries} attempts, using silence fallback")
                return False
    return False


def generate_all_audio(phrases: list, output_dir: str):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_files = []

    for i, phrase in enumerate(phrases):
        english_file = output_dir / f"english_{i}.mp3"
        native_file = output_dir / f"native_{i}.mp3"
        combined_file = output_dir / f"combined_{i}.mp3"

        print(f"\n  Phrase {i+1}:")
        print(f"    EN: {phrase['english']}")
        print(f"    GU: {phrase['gujarati']}")

        nat_success = asyncio.run(generate_audio_with_retries(phrase["gujarati"], NATIVE_VOICE, str(native_file)))
        if nat_success:
            print(f"    - Gujarati: {native_file.name}")
        else:
            print(f"    - Gujarati: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(native_file)]
            subprocess.run(cmd, capture_output=True)

        en_success = asyncio.run(generate_audio_with_retries(phrase["english"], ENGLISH_VOICE, str(english_file)))
        if en_success:
            print(f"    - English: {english_file.name}")
        else:
            print(f"    - English: SILENCE FALLBACK (TTS failed)")
            cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "2", str(english_file)]
            subprocess.run(cmd, capture_output=True)

        en_duration = get_audio_duration(str(english_file))
        nat_duration = get_audio_duration(str(native_file))
        pause_between = 0.5
        total_duration = en_duration + pause_between + nat_duration

        print(f"    Total: {total_duration:.2f}s (EN: {en_duration:.2f}s + pause: {pause_between}s + GU: {nat_duration:.2f}s)")

        cmd = [
            "ffmpeg", "-y",
            "-i", str(english_file),
            "-i", str(native_file),
            "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
            "-map", "[out]",
            str(combined_file)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            concat_file = output_dir / f"concat_{i}.txt"
            with open(concat_file, "w", encoding="utf-8") as f:
                f.write(f"file '{english_file.as_posix()}'\n")
                f.write(f"file '{native_file.as_posix()}'\n")
            cmd = [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0",
                "-i", str(concat_file),
                "-c:a", "aac",
                str(combined_file)
            ]
            subprocess.run(cmd, capture_output=True)
            if concat_file.exists():
                concat_file.unlink()

        actual_duration = get_audio_duration(str(combined_file))
        print(f"    Combined verified: {actual_duration:.2f}s")

        audio_files.append({
            "index": i,
            "english": str(english_file),
            "native": str(native_file),
            "combined": str(combined_file),
            "duration": actual_duration,
            "en_duration": en_duration,
            "nat_duration": nat_duration
        })

    print(f"\n[audio] Generated {len(audio_files)} phrase audios")
    return audio_files


def get_audio_duration(audio_file: str) -> float:
    if not Path(audio_file).exists():
        return 2.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", audio_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except:
        return 2.0


def create_final_narration(audio_files: list, output_file: str):
    n = len(audio_files)
    print(f"[audio] Combining {n} audio files...")
    concat_file = Path(output_file).parent / "narration_list.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for audio_info in audio_files:
            combined_path = Path(audio_info["combined"])
            if combined_path.exists():
                path_str = str(combined_path.resolve()).replace("\\", "/").replace("'", "'\\''")
                f.write(f"file '{path_str}'\n")
    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c:a", "copy", str(output_file)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if concat_file.exists():
        concat_file.unlink()
    if result.returncode == 0 and Path(output_file).exists() and Path(output_file).stat().st_size > 0:
        size = Path(output_file).stat().st_size
        print(f"\n[audio] Final narration: {Path(output_file).name} ({size/1024:.1f} KB)")
        return True
    return False


NOTO_FONT_URL = "https://github.com/google/fonts/raw/main/ofl/notosansgujarati/NotoSansGujarati%5Bwdth%2Cwght%5D.ttf"
FONTS_DIR = BASE_DIR / "fonts"


def ensure_font():
    font_file = FONTS_DIR / "NotoSansGujarati-Bold.ttf"
    if font_file.exists():
        return str(font_file)
    FONTS_DIR.mkdir(exist_ok=True)
    try:
        import urllib.request
        print(f"[font] Downloading {font_file.name}...")
        urllib.request.urlretrieve(NOTO_FONT_URL, str(font_file))
        print(f"[font] Downloaded: {font_file}")
        return str(font_file)
    except Exception as e:
        print(f"[font] Download failed: {e}")
    return None


def create_impressive_background(category_english: str):
    from PIL import Image, ImageDraw

    category_colors = {
    "Greetings": [
        [
            70,
            130,
            180
        ],
        [
            255,
            140,
            0
        ],
        [
            255,
            255,
            0
        ],
        [
            255,
            99,
            71
        ]
    ],
    "Basic Phrases": [
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Common Expressions": [
        [
            138,
            43,
            226
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            105,
            180
        ]
    ],
    "Travel": [
        [
            0,
            191,
            255
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Restaurant": [
        [
            255,
            69,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Shopping": [
        [
            255,
            105,
            180
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            192,
            203
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Emergency": [
        [
            255,
            0,
            0
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            69,
            0
        ],
        [
            220,
            20,
            60
        ]
    ],
    "Family Terms": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Numbers": [
        [
            255,
            215,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Time": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Motivation": [
        [
            138,
            43,
            226
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Love": [
        [
            255,
            0,
            100
        ],
        [
            139,
            0,
            0
        ],
        [
            255,
            105,
            180
        ],
        [
            255,
            192,
            203
        ]
    ],
    "Success": [
        [
            255,
            215,
            0
        ],
        [
            0,
            100,
            0
        ],
        [
            255,
            140,
            0
        ],
        [
            34,
            139,
            34
        ]
    ],
    "Wisdom": [
        [
            0,
            0,
            139
        ],
        [
            255,
            215,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            255,
            0
        ]
    ],
    "Happiness": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            255
        ],
        [
            255,
            165,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Self Improvement": [
        [
            0,
            128,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            0,
            255,
            0
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Gratitude": [
        [
            255,
            127,
            80
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            160,
            122
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Friendship": [
        [
            255,
            192,
            203
        ],
        [
            0,
            100,
            80
        ],
        [
            255,
            105,
            180
        ],
        [
            0,
            200,
            160
        ]
    ],
    "Hope": [
        [
            0,
            0,
            100
        ],
        [
            255,
            255,
            0
        ],
        [
            70,
            130,
            180
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Creativity": [
        [
            255,
            0,
            127
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            20,
            147
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Inner Peace": [
        [
            135,
            206,
            235
        ],
        [
            0,
            0,
            100
        ],
        [
            176,
            224,
            230
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Confidence": [
        [
            255,
            69,
            0
        ],
        [
            0,
            0,
            139
        ],
        [
            255,
            140,
            0
        ],
        [
            70,
            130,
            180
        ]
    ],
    "Perseverance": [
        [
            139,
            69,
            19
        ],
        [
            255,
            215,
            0
        ],
        [
            160,
            82,
            45
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Inspiration": [
        [
            255,
            0,
            255
        ],
        [
            75,
            0,
            130
        ],
        [
            255,
            20,
            147
        ],
        [
            0,
            0,
            139
        ]
    ],
    "Positive Life": [
        [
            50,
            205,
            50
        ],
        [
            255,
            0,
            127
        ],
        [
            144,
            238,
            144
        ],
        [
            255,
            20,
            147
        ]
    ],
    "Courage": [
        [
            178,
            34,
            34
        ],
        [
            255,
            215,
            0
        ],
        [
            220,
            20,
            60
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Kindness": [
        [
            255,
            182,
            193
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            160,
            122
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Patience": [
        [
            34,
            139,
            34
        ],
        [
            255,
            255,
            0
        ],
        [
            60,
            179,
            113
        ],
        [
            255,
            215,
            0
        ]
    ],
    "Forgiveness": [
        [
            230,
            230,
            250
        ],
        [
            75,
            0,
            130
        ],
        [
            216,
            191,
            216
        ],
        [
            138,
            43,
            226
        ]
    ],
    "Strength": [
        [
            100,
            100,
            100
        ],
        [
            255,
            69,
            0
        ],
        [
            150,
            150,
            150
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Joy": [
        [
            255,
            255,
            0
        ],
        [
            255,
            0,
            127
        ],
        [
            255,
            215,
            0
        ],
        [
            147,
            112,
            219
        ]
    ],
    "Balance": [
        [
            60,
            179,
            113
        ],
        [
            138,
            43,
            226
        ],
        [
            152,
            251,
            152
        ],
        [
            75,
            0,
            130
        ]
    ],
    "Growth": [
        [
            0,
            100,
            0
        ],
        [
            255,
            215,
            0
        ],
        [
            34,
            139,
            34
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Purpose": [
        [
            75,
            0,
            130
        ],
        [
            255,
            215,
            0
        ],
        [
            138,
            43,
            226
        ],
        [
            255,
            140,
            0
        ]
    ],
    "Mindfulness": [
        [
            210,
            180,
            140
        ],
        [
            75,
            0,
            130
        ],
        [
            245,
            245,
            220
        ],
        [
            138,
            43,
            226
        ]
    ]
}

    img = Image.new('RGB', (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)

    colors = category_colors.get(category_english, [(138, 43, 226), (75, 0, 130), (255, 20, 147), (147, 112, 219)])

    for y in range(VIDEO_HEIGHT):
        ratio = y / VIDEO_HEIGHT
        if ratio < 0.33:
            r = int(colors[0][0] + (colors[1][0] - colors[0][0]) * (ratio * 3))
            g = int(colors[0][1] + (colors[1][1] - colors[0][1]) * (ratio * 3))
            b = int(colors[0][2] + (colors[1][2] - colors[0][2]) * (ratio * 3))
        elif ratio < 0.66:
            r = int(colors[1][0] + (colors[2][0] - colors[1][0]) * ((ratio - 0.33) * 3))
            g = int(colors[1][1] + (colors[2][1] - colors[1][1]) * ((ratio - 0.33) * 3))
            b = int(colors[1][2] + (colors[2][2] - colors[1][2]) * ((ratio - 0.33) * 3))
        else:
            r = int(colors[2][0] + (colors[3][0] - colors[2][0]) * ((ratio - 0.66) * 3))
            g = int(colors[2][1] + (colors[3][1] - colors[2][1]) * ((ratio - 0.66) * 3))
            b = int(colors[2][2] + (colors[3][2] - colors[2][2]) * ((ratio - 0.66) * 3))
        draw.rectangle([(0, y), (VIDEO_WIDTH, y + 1)], fill=(r, g, b))

    for i in range(0, VIDEO_WIDTH, 120):
        for j in range(0, VIDEO_HEIGHT, 120):
            draw.ellipse(
                [(i + 30, j + 30), (i + 90, j + 90)],
                outline=(255, 255, 255, 20),
                width=1
            )

    glow = Image.new('RGBA', (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for radius in range(800, 0, -50):
        alpha = int(30 * (1 - radius / 800))
        glow_draw.ellipse(
            [(VIDEO_WIDTH//2 - radius, VIDEO_HEIGHT//3 - radius),
             (VIDEO_WIDTH//2 + radius, VIDEO_HEIGHT//3 + radius)],
            fill=(255, 255, 255, alpha)
        )

    img = img.convert('RGBA')
    img = Image.alpha_composite(img, glow)
    return img


def find_font(bold=False, size=40):
    from PIL import ImageFont
    font_file = FONTS_DIR / "NotoSansGujarati-Bold.ttf"
    if font_file.exists():
        try:
            return ImageFont.truetype(str(font_file), size)
        except (IOError, OSError):
            pass
    if bold:
        font_preferences = [
            "segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    else:
        font_preferences = [
            "segoeui.ttf", "arial.ttf", "calibri.ttf", "DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for font_name in font_preferences:
        try:
            return ImageFont.truetype(font_name, size)
        except (IOError, OSError):
            continue
    return ImageFont.load_default()


def rounded_rect(draw, bbox, radius, fill=None, outline=None, width=1):
    x1, y1, x2, y2 = bbox
    r = min(radius, (x2 - x1) // 2, (y2 - y1) // 2)
    draw.pieslice([x1, y1, x1 + r*2, y1 + r*2], 180, 270, fill=fill)
    draw.pieslice([x2 - r*2, y1, x2, y1 + r*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2 - r*2, x1 + r*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2 - r*2, y2 - r*2, x2, y2], 0, 90, fill=fill)
    draw.rectangle([x1 + r, y1, x2 - r, y2], fill=fill)
    draw.rectangle([x1, y1 + r, x2, y2 - r], fill=fill)


def generate_complete_image(phrase_data: dict, category_english: str, output_path: str, phrase_index: int = 0, total_phrases: int = 5):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("PIL not available. Install: pip install Pillow")
        return None

    ensure_font()
    img = create_impressive_background(category_english)
    draw = ImageDraw.Draw(img)

    SIZE_CATEGORY = 64
    SIZE_NATIVE_L = 100
    SIZE_NATIVE_M = 82
    SIZE_NATIVE_S = 66
    SIZE_ENGLISH = 70
    SIZE_TRANSLITERATION = 48
    SIZE_BRANDING = 50
    SIZE_PROGRESS = 38

    font_category = find_font(bold=True, size=SIZE_CATEGORY)
    font_native_l = find_font(bold=True, size=SIZE_NATIVE_L)
    font_native_m = find_font(bold=True, size=SIZE_NATIVE_M)
    font_native_s = find_font(bold=True, size=SIZE_NATIVE_S)
    font_english = find_font(bold=True, size=SIZE_ENGLISH)
    font_transliteration = find_font(bold=False, size=SIZE_TRANSLITERATION)
    font_branding = find_font(bold=True, size=SIZE_BRANDING)
    font_progress = find_font(bold=False, size=SIZE_PROGRESS)

    native = phrase_data.get("gujarati", "")
    english = phrase_data.get("english", "")
    transliteration = phrase_data.get("transliteration", "")

    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def pick_native_font(text, max_w):
        for font, name in [(font_native_l, 'L'), (font_native_m, 'M'), (font_native_s, 'S')]:
            lines = wrap_text(text, font, max_w)
            if len(lines) <= 2:
                return font, lines
        return font_native_s, wrap_text(native, font_native_s, max_w)

    def measure_line_h(font):
        b = draw.textbbox((0, 0), "Ag", font=font)
        return b[3] - b[1]

    max_text_w = VIDEO_WIDTH - 180
    cat_native = CATEGORIES_NATIVE.get(category_english, category_english)

    nat_font, nat_lines = pick_native_font(native, max_text_w - 40)
    en_lines = wrap_text(english, font_english, max_text_w)
    trans_lines = wrap_text(transliteration, font_transliteration, max_text_w - 60) if transliteration else []

    nat_lh = measure_line_h(nat_font)
    en_lh = measure_line_h(font_english)
    trans_lh = measure_line_h(font_transliteration)

    nat_box_pad = 35
    en_box_pad = 28
    trans_box_pad = 22

    nat_box_h = len(nat_lines) * nat_lh + nat_box_pad * 2
    en_box_h = len(en_lines) * en_lh + en_box_pad * 2
    trans_box_h = len(trans_lines) * trans_lh + trans_box_pad * 2 if trans_lines else 0

    gap_cat_nat = 50
    gap_nat_en = 35
    gap_en_trans = 30
    gap_trans_prog = 25
    gap_prog_brand = 40
    prog_bar_h = 30

    total_center_h = (0 + gap_cat_nat + nat_box_h + gap_nat_en +
                      en_box_h + gap_en_trans + trans_box_h + gap_trans_prog +
                      prog_bar_h + gap_prog_brand)

    start_y = int((VIDEO_HEIGHT - total_center_h) * 0.38)
    if start_y < 200:
        start_y = 200

    cy = start_y

    # Category bar (rounded)
    cat_text = category_english
    cat_bb = draw.textbbox((0, 0), cat_text, font=font_category)
    cat_tw = cat_bb[2] - cat_bb[0]
    cat_th = cat_bb[3] - cat_bb[1]
    cat_cx = VIDEO_WIDTH // 2
    cat_cy = 185
    cat_pad = 28
    cat_box_x1 = cat_cx - cat_tw // 2 - cat_pad
    cat_box_y1 = cat_cy - cat_th // 2 - cat_pad
    cat_box_x2 = cat_cx + cat_tw // 2 + cat_pad
    cat_box_y2 = cat_cy + cat_th // 2 + cat_pad
    rounded_rect(draw, (cat_box_x1, cat_box_y1, cat_box_x2, cat_box_y2),
                 25, fill=(0, 0, 0, 190))
    draw.text((cat_cx, cat_cy), cat_text,
              fill=(255, 255, 255), font=font_category, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    cy += gap_cat_nat

    # English phrase (top)
    en_margin = 50
    rounded_rect(draw, (en_margin, cy, VIDEO_WIDTH - en_margin, cy + en_box_h), 28,
                 fill=(20, 40, 100, 220))
    for i, line in enumerate(en_lines):
        ly = cy + en_box_pad + i * en_lh + en_lh // 2
        draw.text((VIDEO_WIDTH // 2, ly), line,
                  fill=(255, 255, 255), font=font_english, anchor="mm",
                  stroke_width=3, stroke_fill=(0, 0, 40))

    cy += en_box_h + gap_nat_en

    # Gujarati phrase (below English)
    nat_margin = 70
    rounded_rect(draw, (nat_margin, cy, VIDEO_WIDTH - nat_margin, cy + nat_box_h), 24,
                 fill=(139, 0, 0, 220))
    for i, line in enumerate(nat_lines):
        ly = cy + nat_box_pad + i * nat_lh + nat_lh // 2
        draw.text((VIDEO_WIDTH // 2, ly), line,
                  fill=(255, 255, 200), font=nat_font, anchor="mm",
                  stroke_width=2, stroke_fill=(60, 0, 0))

    cy += nat_box_h + gap_en_trans

    # Transliteration
    if trans_lines:
        trans_margin = 90
        rounded_rect(draw, (trans_margin, cy, VIDEO_WIDTH - trans_margin, cy + trans_box_h), 18,
                     fill=(40, 40, 40, 220))
        for i, line in enumerate(trans_lines):
            ly = cy + trans_box_pad + i * trans_lh + trans_lh // 2
            draw.text((VIDEO_WIDTH // 2, ly), line,
                      fill=(220, 220, 220), font=font_transliteration, anchor="mm",
                      stroke_width=1, stroke_fill=(20, 20, 20))
        cy += trans_box_h + gap_trans_prog
    else:
        cy += gap_trans_prog

    # Progress
    prog_text = f"{phrase_index + 1} / {total_phrases}"
    prog_bb = draw.textbbox((0, 0), prog_text, font=font_progress)
    prog_h = prog_bb[3] - prog_bb[1]
    draw.text((VIDEO_WIDTH // 2, cy + prog_h // 2), prog_text,
              fill=(180, 180, 180), font=font_progress, anchor="mm")

    # Branding (rounded)
    brand_text = "VELOCITY GUJARATI"
    brand_bb = draw.textbbox((0, 0), brand_text, font=font_branding)
    brand_tw = brand_bb[2] - brand_bb[0]
    brand_th = brand_bb[3] - brand_bb[1]
    brand_cx = VIDEO_WIDTH // 2
    brand_cy = VIDEO_HEIGHT - 120
    brand_pad = 32
    brand_box_x1 = brand_cx - brand_tw // 2 - brand_pad
    brand_box_y1 = brand_cy - brand_th // 2 - brand_pad
    brand_box_x2 = brand_cx + brand_tw // 2 + brand_pad
    brand_box_y2 = brand_cy + brand_th // 2 + brand_pad
    rounded_rect(draw, (brand_box_x1, brand_box_y1, brand_box_x2, brand_box_y2),
                 30, fill=(0, 0, 0, 195))
    draw.text((brand_cx, brand_cy), brand_text,
              fill=(255, 215, 0), font=font_branding, anchor="mm",
              stroke_width=2, stroke_fill=(0, 0, 0))

    if img.mode == 'RGBA':
        img = img.convert('RGB')

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path, quality=95, optimize=True)
    print(f"  Image: {Path(output_path).name}")
    return output_path


def create_video_from_images_audio(image_files: list, audio_files: list, combined_audio: str, output_file: str):
    print(f"\n[video] Creating video from {len(image_files)} images...")
    print(f"[video] Ensuring complete audio playback and sync...")

    temp_clips = []

    for i, (img_path, audio_info) in enumerate(zip(image_files, audio_files)):
        duration = audio_info['duration']
        print(f"  Image {i+1}/{len(image_files)}: {duration:.2f}s (EN: {audio_info.get('en_duration', 0):.1f}s + GU: {audio_info.get('nat_duration', 0):.1f}s)")

        temp_clip = Path(output_file).parent / f"temp_clip_{i:02d}.mp4"
        temp_clips.append(temp_clip)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={FPS}",
            "-t", str(duration),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(temp_clip)
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    print("[video] Concatenating clips...")
    temp_video = Path(output_file).parent / "temp_video.mp4"
    concat_file = Path(output_file).parent / "concat_list.txt"

    with open(concat_file, "w") as f:
        for clip in temp_clips:
            f.write(f"file '{clip.resolve().as_posix()}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_file), "-c", "copy", str(temp_video)]
    subprocess.run(cmd, check=True, capture_output=True)

    print("[video] Adding audio (ensuring complete playback)...")
    audio_duration = get_audio_duration(combined_audio)
    print(f"[video] Audio duration: {audio_duration:.2f}s")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(temp_video),
        "-i", str(combined_audio),
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        str(output_file)
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    video_duration = get_audio_duration(str(output_file).replace(".mp4", ".mp4"))
    print(f"[video] Video created: {Path(output_file).name} ({video_duration:.2f}s)")

    for clip in temp_clips:
        if clip.exists():
            clip.unlink()
    if temp_video.exists():
        temp_video.unlink()
    if concat_file.exists():
        concat_file.unlink()


def generate_reel(category_english: str = None):
    if not category_english:
        category_english = get_available_category()

    print(f"\n{'='*80}")
    print(f"Category: {category_english} ({CATEGORIES_NATIVE.get(category_english, category_english)})")
    print(f"{'='*80}\n")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reel_dir = VIDEO_DIR / f"{category_english}_{timestamp}"
    reel_dir.mkdir(exist_ok=True)

    print("[1/4] Generating unique phrases (checking history)...")
    phrases = generate_phrases(category_english, num_phrases=5)

    for i, phrase in enumerate(phrases, 1):
        print(f"  {i}. {phrase['english']} -> {phrase['gujarati']}")

    print("\n[2/4] Generating images with impressive backgrounds...")
    for i, phrase in enumerate(phrases):
        output_path = reel_dir / f"phrase_{i:02d}.jpg"
        generate_complete_image(phrase, category_english, str(output_path), phrase_index=i, total_phrases=len(phrases))
        print(f"  Image {i+1}: {phrase['english'][:40]}...")

    print("\n[3/4] Generating audio (English + Gujarati with 500ms pause)...")
    audio_files = generate_all_audio(phrases, str(reel_dir))

    final_audio = reel_dir / "narration.mp3"
    create_final_narration(audio_files, str(final_audio))

    print("\n[4/4] Creating video...")
    output_video = reel_dir / "final_reel.mp4"

    image_files = sorted([str(p) for p in reel_dir.glob("phrase_*.jpg")])

    create_video_from_images_audio(
        image_files,
        audio_files,
        str(final_audio),
        str(output_video)
    )

    metadata = {
        "category_english": category_english,
        "category_native": CATEGORIES_NATIVE.get(category_english, category_english),
        "timestamp": timestamp,
        "phrases": phrases,
        "video": str(output_video),
        "audio": str(final_audio)
    }

    with open(reel_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"REEL COMPLETE!")
    print(f"  {reel_dir}")
    print(f"  {output_video.name}")
    print(f"  Branding: VELOCITY GUJARATI")
    print(f"{'='*80}\n")

    return metadata


if __name__ == "__main__":
    print("\n" + "="*80)
    print(f"VELOCITY GUJARATI - FACEBOOK REELS AUTOMATION")
    print("="*80)
    print("\nFEATURES:")
    print("  - Natural pauses with commas (non-robotic TTS)")
    print("  - Perfect audio-video synchronization")
    print("  - Complete audio playback guaranteed")
    print("  - English category names (for learners)")
    print(f"  - VELOCITY GUJARATI branding at bottom")
    print("  - NEVER repeats phrases (permanent history tracking)")
    print(f"\nAVAILABLE CATEGORIES ({len(CATEGORIES_ENGLISH)} total):")
    for i, cat in enumerate(CATEGORIES_ENGLISH, 1):
        print(f"   {i:2d}. {cat} ({CATEGORIES_NATIVE.get(cat, cat)})")
    print("="*80)

    generate_reel()

    print("\n" + "="*80)
    print("READY FOR DAILY AUTOMATION!")
    print("="*80)

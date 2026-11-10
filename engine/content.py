"""AI phrase generation with permanent no-repeat history."""

from __future__ import annotations

import json
import random
import time
from datetime import datetime

import requests

import config
from config import CATEGORIES, CATEGORIES_NATIVE, HISTORY_DIR, MAX_RECENT_CATEGORIES

PHRASE_HISTORY_FILE = HISTORY_DIR / "all_generated_phrases.json"
RECENT_CATEGORIES_FILE = HISTORY_DIR / "recent_categories.json"

PHRASE_KEY = config.LANGUAGE["history_key"]
LANGUAGE_NAME = config.LANGUAGE["name"]
NATIVE_NAME = config.LANGUAGE["native_name"]

# ==== FALLBACK PHRASES START ====
FALLBACK_PHRASES = [
    {"english": "Where can I find a taxi?", "native": "મને ટેક્સી ક્યાંથી મળશે?", "transliteration": "Mane taxi kyanthi malshe?"},
    {"english": "How far is the railway station?", "native": "રેલવે સ્ટેશન કેટલું દૂર છે?", "transliteration": "Railway station ketlu door chhe?"},
    {"english": "Can you show me the way?", "native": "શું તમે મને રસ્તો બતાવી શકશો?", "transliteration": "Shu tame mane rasto batavi shaksho?"},
    {"english": "I want to visit the heritage site.", "native": "મારે ઐતિહાસિક સ્થળની મુલાકાત લેવી છે.", "transliteration": "Mare aithihasik sthalni mulakat levi chhe."},
    {"english": "Is this the bus to Ahmedabad?", "native": "શું આ અમદાવાદ જતી બસ છે?", "transliteration": "Shu aa Ahmedabad jati bus chhe?"},
    {"english": "Please book two tickets for us.", "native": "કૃપા કરીને અમારા માટે બે ટિકિટ બુક કરો.", "transliteration": "Krupa karine amara mate be ticket book karo."},
    {"english": "The view here is magnificent.", "native": "અહીંનો નજારો ખૂબ ભવ્ય છે.", "transliteration": "Ahino najaro khub bhavya chhe."},
    {"english": "What time does the train arrive?", "native": "ટ્રેન કેટલા વાગ્યે આવશે?", "transliteration": "Train ketla vagye aavshe?"},
    {"english": "Please bring the menu card.", "native": "કૃપા કરીને મેનુ કાર્ડ લાવો.", "transliteration": "Krupa karine menu card laavo."},
    {"english": "What is today's special dish?", "native": "આજની ખાસ વાનગી કઈ છે?", "transliteration": "Aajni khas vaangi kai chhe?"},
    {"english": "The Gujarati thali was delicious.", "native": "ગુજરાતી થાળી ખૂબ સ્વાદિષ્ટ હતી.", "transliteration": "Gujarati thali khub swadisht hati."},
    {"english": "Please serve water with ice.", "native": "કૃપા કરીને બરફવાળું પાણી આપો.", "transliteration": "Krupa karine barfvalu pani aapo."},
    {"english": "We would like less spicy food.", "native": "અમને ઓછું તીખું ભોજન જોઈશે.", "transliteration": "Amane ochhu teekhu bhojan joishe."},
    {"english": "Can we get the bill, please?", "native": "શું અમે બિલ મેળવી શકીએ?", "transliteration": "Shu ame bill melvi shakie?"},
    {"english": "I love the sweet and savory flavors.", "native": "મને ખાટો-મીઠો સ્વાદ બહુ ગમે છે.", "transliteration": "Mane khato-meetho swad bahu game chhe."},
    {"english": "How much does this item cost?", "native": "આ વસ્તુની કિંમત કેટલી છે?", "transliteration": "Aa vastuni kimmat ketli chhe?"},
    {"english": "Do you have a different size?", "native": "શું તમારી પાસે બીજી સાઈઝ છે?", "transliteration": "Shu tamari pase beeji size chhe?"},
    {"english": "Can you give a discount?", "native": "શું થોડું ડિસ્કાઉન્ટ મળશે?", "transliteration": "Shu thodu discount malshe?"},
    {"english": "This traditional dress looks lovely.", "native": "આ પરંપરાગત પોશાક ખૂબ સુંદર છે.", "transliteration": "Aa paramparagat poshak khub sundar chhe."},
    {"english": "I will pay with mobile payment.", "native": "હું ઓનલાઇન પેમેન્ટ કરીશ.", "transliteration": "Hu online payment karish."},
    {"english": "Please pack this carefully.", "native": "કૃપા કરીને આને સાચવીને પેક કરો.", "transliteration": "Krupa karine aane saachvine pack karo."},
    {"english": "Welcome to Gujarat, friend.", "native": "ગુજરાતમાં તમારું સ્વાગત છે, મિત્ર.", "transliteration": "Gujaratma tamaru swagat chhe, mitra."},
    {"english": "Good morning, wishing you joy.", "native": "શુભ સવાર, તમારો દિવસ આનંદમય રહે.", "transliteration": "Shubh savar, tamaro divas aanandmay rahe."},
    {"english": "How has your day been?", "native": "તમારો દિવસ કેવો રહ્યો?", "transliteration": "Tamaro divas kevo rahyo?"},
    {"english": "Pleasure speaking with you today.", "native": "આજે તમારી સાથે વાત કરીને આનંદ થયો.", "transliteration": "Aaje tamari sathe vaat karine aanand thayo."},
    {"english": "Have a wonderful, restful evening.", "native": "તમારી સાંજ શાંતિપૂર્ણ અને સુંદર રહે.", "transliteration": "Tamari saanjh shantipoorna ane sundar rahe."},
    {"english": "Every small effort counts.", "native": "દરેક નાનો પ્રયાસ મહત્વનો છે.", "transliteration": "Darek nano prayas mahatvano chhe."},
    {"english": "Courage begins with one step.", "native": "હિંમત એક પગલાથી શરૂ થાય છે.", "transliteration": "Himmat ek paglathi sharu thay chhe."},
    {"english": "Believe in your endless power.", "native": "તમારી અસીમ શક્તિ પર વિશ્વાસ રાખો.", "transliteration": "Tamari aseem shakti par vishwas rakho."},
    {"english": "Hard work always creates miracles.", "native": "મહેનત હંમેશા ચમત્કાર સર્જે છે.", "transliteration": "Mehnat hamesha chamatkar sarje chhe."},
    {"english": "Turn challenges into great wisdom.", "native": "પડકારોને મહાન શાણપણમાં બદલો.", "transliteration": "Padkarone mahan shaanpanma badlo."},
    {"english": "My family gathers every evening.", "native": "મારો પરિવાર રોજ સાંજે ભેગો થાય છે.", "transliteration": "Maro parivar roj saanje bhego thay chhe."},
    {"english": "Grandmother shares sweet childhood stories.", "native": "દાદી બાળપણની મીઠી વાર્તાઓ કહે છે.", "transliteration": "Dadi baalpan-ni meethi vaartao kahe chhe."},
    {"english": "My elder brother guides me.", "native": "મારા મોટા ભાઈ મને માર્ગદર્શન આપે છે.", "transliteration": "Mara mota bhai mane margdarshan aape chhe."},
    {"english": "Parents are our greatest blessing.", "native": "માતાપિતા આપણા સૌથી મોટા આશીર્વાદ છે.", "transliteration": "Matapita aapna sauthi mota aashirvad chhe."},
    {"english": "We celebrate festivals together happily.", "native": "આપણે તહેવારો સાથે મળીને આનંદથી ઉજવીએ છીએ.", "transliteration": "Aapne tahevaro sathe maline aanandthi ujviye chhiye."},
    {"english": "The breeze from the river is cool.", "native": "નદી પરથી આવતો પવન ઠંડો છે.", "transliteration": "Nadi parthi aavto pavan thando chhe."},
    {"english": "Dark clouds promise refreshing rain.", "native": "કાળા વાદળો તાજા વરસાદની ખાતરી આપે છે.", "transliteration": "Kaala vaadalo taaja varsadni khatri aape chhe."},
    {"english": "The golden sun warms the morning.", "native": "સોનેરી સૂર્ય સવારને હૂંફાળી બનાવે છે.", "transliteration": "Soneri surya savarne hoonfali banave chhe."},
    {"english": "Winter mornings in Gujarat are crisp.", "native": "ગુજરાતમાં શિયાળાની સવાર તાજગીભરી હોય છે.", "transliteration": "Gujaratma shiyalani savar taajgibhari hoy chhe."},
    {"english": "Patience resolves what anger destroys.", "native": "જે ક્રોધ બગાડે છે, તે ધીરજ સુધારે છે.", "transliteration": "Je krodh bagade chhe, te dhiraj sudhare chhe."},
    {"english": "Kind words cost nothing at all.", "native": "મીઠા વેણ બોલવામાં કશું ખર્ચાતું નથી.", "transliteration": "Meetha ven bolvama kashu kharchaatu nathi."},
    {"english": "Truth shines brighter than the sun.", "native": "સત્ય સૂર્ય કરતાં પણ વધુ ચમકે છે.", "transliteration": "Satya surya karta pan vadhu chamke chhe."},
    {"english": "A calm mind finds every answer.", "native": "શાંત મન દરેક પ્રશ્નનો ઉકેલ શોધે છે.", "transliteration": "Shaant man darek prashnano ukel shodhe chhe."},
]
# ==== FALLBACK PHRASES END ====


def _load_json(path, default):
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_phrase_history():
    data = _load_json(PHRASE_HISTORY_FILE, {"phrases": [], "last_updated": None})
    data.setdefault("phrases", [])
    return data


def save_phrase_history(data):
    data["last_updated"] = datetime.now().isoformat()
    _save_json(PHRASE_HISTORY_FILE, data)


def is_phrase_used(english):
    english_lower = english.lower().strip()
    for p in load_phrase_history()["phrases"]:
        if p.get("english", "").lower().strip() == english_lower:
            return True
    return False


def _history_native(p):
    for key in (PHRASE_KEY, "vietnamese", "native", "translation", "target"):
        value = p.get(key)
        if value:
            return str(value)
    return ""


def add_phrases_to_history(phrases, category):
    history = load_phrase_history()
    for phrase in phrases:
        history["phrases"].append({
            "english": phrase["english"],
            PHRASE_KEY: phrase["native"],
            "transliteration": phrase.get("transliteration", ""),
            "category": category,
            "generated_at": datetime.now().isoformat(),
        })
    save_phrase_history(history)
    print(f"[content] Saved {len(phrases)} phrases (history total: {len(history['phrases'])})")


def get_available_category():
    data = _load_json(RECENT_CATEGORIES_FILE, {"recent_categories": [], "last_updated": None})
    recent = data.get("recent_categories", [])
    available = [c for c in CATEGORIES if c not in recent]
    if not available:
        recent = recent[-5:]
        available = [c for c in CATEGORIES if c not in recent]
        print("[rotation] Reset recent categories")
    selected = random.choice(available)
    recent.append(selected)
    data["recent_categories"] = recent[-MAX_RECENT_CATEGORIES:]
    data["last_updated"] = datetime.now().isoformat()
    _save_json(RECENT_CATEGORIES_FILE, data)
    print(f"[rotation] Category: {selected} ({len(available)} available)")
    return selected


def _normalize_phrase(item):
    if not isinstance(item, dict):
        return None
    english = str(item.get("english", "")).strip()
    native = str(
        item.get(PHRASE_KEY)
        or item.get("native")
        or item.get("vietnamese")
        or item.get("translation")
        or ""
    ).strip()
    translit = str(item.get("transliteration") or item.get("romanization") or item.get("romaji") or "").strip()
    if not english or not native:
        return None
    if len(english.split()) > 16:
        return None
    if "/" in native or "|" in native:
        native = native.split("/")[0].split("|")[0].strip()
    return {
        "english": english.replace("  ", " ").strip(),
        "native": native.strip(),
        "transliteration": translit.strip().strip("[]"),
    }


def _history_keys(history):
    used_en = set()
    used_nat = set()
    for p in history.get("phrases", []):
        en = str(p.get("english", "")).lower().strip()
        nat = _history_native(p).lower().strip()
        if en:
            used_en.add(en)
        if nat:
            used_nat.add(nat)
    return used_en, used_nat


def generate_phrases(category_english: str, num_phrases: int = 5) -> list:
    category_native = CATEGORIES_NATIVE[category_english]
    history = load_phrase_history()
    used_en, used_nat = _history_keys(history)
    recent_english = [
        p["english"] for p in history["phrases"] if p.get("category") == category_english
    ][-30:]

    models = [config.AI_MODEL]
    if "gemini-fast" not in models:
        models.append("gemini-fast")

    if config.POLLINATIONS_API_KEY:
        for attempt in range(5):
            model = models[0] if attempt < 3 else models[-1]
            try:
                phrases = _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model)
                unique = []
                for item in phrases:
                    p = _normalize_phrase(item)
                    if not p:
                        continue
                    key_en = p["english"].lower().strip()
                    key_nat = p["native"].lower().strip()
                    if key_en in used_en or key_nat in used_nat:
                        continue
                    if any(key_en == u["english"].lower().strip() for u in unique):
                        continue
                    used_en.add(key_en)
                    used_nat.add(key_nat)
                    unique.append(p)
                    if len(unique) >= num_phrases:
                        break
                if len(unique) >= num_phrases:
                    add_phrases_to_history(unique[:num_phrases], category_english)
                    return unique[:num_phrases]
                print(f"[content] Attempt {attempt + 1}: only {len(unique)} fresh phrases (need {num_phrases})")
            except Exception as exc:  # noqa: BLE001 - network boundary
                print(f"[content] Attempt {attempt + 1} failed ({model}): {exc}")
            time.sleep(1.5 * (attempt + 1))
    else:
        print("[content] No POLLINATIONS_API_KEY, using fallback phrases")

    fresh_fallback = []
    for p in FALLBACK_PHRASES:
        if p["english"].lower().strip() in used_en or p["native"].lower().strip() in used_nat:
            continue
        fresh_fallback.append(p)
    if not fresh_fallback:
        raise RuntimeError("Phrase API unavailable and no unused fallback phrases left; refusing to reuse phrases")
    chosen = fresh_fallback[:num_phrases]
    if len(chosen) < num_phrases:
        print(f"[content] Only {len(chosen)} fresh fallback phrases; building a shorter lesson")
    add_phrases_to_history(chosen, category_english)
    return chosen


def _request_phrases(category_english, category_native, recent_english, num_phrases, attempt, model=None):
    avoid = ""
    if recent_english:
        avoid = "\nDo NOT reuse any of these phrases:\n" + "\n".join(f"- {p}" for p in recent_english)

    prompt = f"""Create {num_phrases * 6} unique {category_english} phrases for English speakers learning {LANGUAGE_NAME}.
{avoid}

Rules:
1. Keep every phrase short and natural (4-11 words in English).
2. Use natural commas for TTS breathing pauses.
3. Each phrase must be speakable in 2-4 seconds.
4. Write clean {LANGUAGE_NAME} in {NATIVE_NAME} with correct accents and orthography. One translation only, no slashes.
5. Transliteration is a friendly Roman-script pronunciation guide for English speakers (not IPA).
6. Vary the sentence patterns and emotions. No duplicates.
7. Phrases must feel like real everyday language, not textbook filler.

Return ONLY a JSON array:
[{{"english": "...", "native": "...", "transliteration": "..."}}]"""

    response = requests.post(
        "https://gen.pollinations.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {config.POLLINATIONS_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": model or config.AI_MODEL,
            "messages": [
                {"role": "system", "content": f"You are a {LANGUAGE_NAME} teacher creating short, natural, varied bilingual phrases. Reply with JSON only."},
                {"role": "user", "content": prompt},
            ],
            "temperature": min(0.95 + attempt * 0.02, 1.0),
        },
        timeout=90,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    if "```json" in content:
        content = content.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in content:
        content = content.split("```", 1)[1].split("```", 1)[0].strip()

    start = content.find("[")
    end = content.rfind("]")
    if start >= 0 and end > start:
        content = content[start:end + 1]

    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("AI did not return a JSON array")
    return data

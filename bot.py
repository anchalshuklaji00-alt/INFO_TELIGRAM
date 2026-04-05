import telebot
import requests
import os
import json
import time
from datetime import datetime

# 🔥 BOT TOKEN
BOT_TOKEN = '8679319585:AAEN_PkS2IB8DvY1a2EM6VCqND2yXlXqSyc'
bot = telebot.TeleBot(BOT_TOKEN)

API_URL = "https://info-43yp.vercel.app/player-info"

# ==========================================
# ⚙️ CHANNELS, GROUPS SETUP
# ==========================================
GROUP_USERNAME = "@LikeBotFreeFireMax"
CHANNEL_1 = "@ROLEX857J"
CHANNEL_2 = "@rolexlike"
BOT_2_LINK = "https://t.me/RolexLike_bot"

# ==========================================
# 🗃️ ITEM NAME DATABASE (Load once at startup)
# ==========================================
ITEM_DB = {}

def _load_item_db():
    global ITEM_DB
    # Older files: itemID + description field
    for fname in ["ItemData.json", "ItemDataOB46.json", "ItemDataOB47.json"]:
        if os.path.exists(fname):
            try:
                with open(fname, encoding="utf-8") as f:
                    for entry in json.load(f):
                        iid  = str(entry.get("itemID", "")).strip()
                        name = (entry.get("description") or "").strip()
                        if iid and name and name.lower() not in ("unread", ""):
                            ITEM_DB.setdefault(iid, name)
            except Exception:
                pass
    # OB50 newest names — override older entries
    if os.path.exists("items-OB50-live.json"):
        try:
            with open("items-OB50-live.json", encoding="utf-8") as f:
                for entry in json.load(f):
                    iid  = str(entry.get("Id", "")).strip()
                    name = (entry.get("name") or "").strip()
                    if iid and name and name.lower() not in ("unread", ""):
                        ITEM_DB[iid] = name
        except Exception:
            pass
    print(f"✅ Item DB loaded: {len(ITEM_DB)} items")

_load_item_db()

def get_item_name(item_id):
    """Return item name from DB. Falls back to raw ID string if not found."""
    if not item_id:
        return "Not Available"
    name = ITEM_DB.get(str(item_id))
    return name if name else str(item_id)


# ==========================================
# ⚙️ USER DATABASE SYSTEM
# ==========================================
USER_FILE      = "verified_users.txt"
ALL_USERS_FILE = "all_users_bot.txt"

for file in [USER_FILE, ALL_USERS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass

user_cooldowns = {}

def is_user_verified(user_id):
    with open(USER_FILE, "r") as f:
        users = f.read().splitlines()
    return str(user_id) in users

def add_verified_user(user_id):
    if not is_user_verified(user_id):
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

def remove_verified_user(user_id):
    if is_user_verified(user_id):
        with open(USER_FILE, "r") as f:
            users = f.read().splitlines()
        users.remove(str(user_id))
        with open(USER_FILE, "w") as f:
            f.write("\n".join(users) + "\n")

def log_active_user(user_id):
    with open(ALL_USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(ALL_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")


# ==========================================
# 🚨 LEAVE & BLOCK TRACKER (AUTO-REMOVE)
# ==========================================
@bot.message_handler(content_types=['left_chat_member'])
def handle_left_member(message):
    remove_verified_user(message.left_chat_member.id)

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for member in message.new_chat_members:
        log_active_user(member.id)

@bot.my_chat_member_handler()
def handle_bot_block(message: telebot.types.ChatMemberUpdated):
    if message.new_chat_member.status in ['kicked', 'left']:
        remove_verified_user(message.from_user.id)


# ==========================================
# 🔥 FF RANK & STARS LOGIC  ← ORIGINAL, UNTOUCHED
# ==========================================
def get_br_rank(rank_id, points):
    pts = int(points)
    r = str(rank_id)
    if pts >= 6000: return "Master"
    if pts >= 3200: return "Heroic"
    ranks = {
        "11": "Bronze I",    "12": "Bronze II",    "13": "Bronze III",
        "21": "Silver I",    "22": "Silver II",    "23": "Silver III",
        "31": "Gold I",      "32": "Gold II",      "33": "Gold III",   "34": "Gold IV",
        "41": "Platinum I",  "42": "Platinum II",  "43": "Platinum III","44": "Platinum IV","45": "Platinum V",
        "51": "Diamond I",   "52": "Diamond II",   "53": "Diamond III","54": "Diamond IV", "55": "Diamond V",
        "61": "Heroic",      "62": "Elite Heroic",
        "71": "Master",      "72": "Elite Master",
        "81": "Grandmaster I","82": "Grandmaster II","83": "Grandmaster III","84": "Grandmaster IV","85": "Grandmaster V",
        "321": "Diamond V",  "322": "Diamond IV",  "323": "Diamond III","324": "Diamond II","325": "Diamond I",
        "401": "Heroic",     "402": "Elite Heroic",
        "501": "Master",     "502": "Elite Master",
    }
    return ranks.get(r, f"Rank {r}")

def get_cs_rank(rank_id):
    r = str(rank_id)
    ranks = {
        "11": "Bronze I",    "12": "Bronze II",    "13": "Bronze III",
        "21": "Silver I",    "22": "Silver II",    "23": "Silver III",
        "31": "Gold I",      "32": "Gold II",      "33": "Gold III",   "34": "Gold IV",
        "41": "Platinum I",  "42": "Platinum II",  "43": "Platinum III","44": "Platinum IV","45": "Platinum V",
        "51": "Diamond I",   "52": "Diamond II",   "53": "Diamond III","54": "Diamond IV", "55": "Diamond V",
        "61": "Heroic",      "62": "Elite Heroic",
        "71": "Master",      "72": "Elite Master",
        "81": "Grandmaster I","82": "Grandmaster II","83": "Grandmaster III","84": "Grandmaster IV","85": "Grandmaster V",
        "91": "Grandmaster",
        "211": "Diamond I",  "212": "Diamond II",  "213": "Diamond III","214": "Diamond IV",
        "311": "Heroic",     "312": "Elite Heroic","320": "Elite Heroic",
        "321": "Master",     "324": "Elite Master",
    }
    return ranks.get(r, f"Rank {r}")

def get_cs_stars(rank_id, points):
    pts = int(points)
    r_id = int(rank_id)
    if r_id >= 311:
        return max(0, pts - 87)
    return pts

def fmt_t(ts):
    if ts and str(ts).isdigit():
        return datetime.fromtimestamp(int(ts)).strftime('%d %B %Y at %I:%M:%S %p')
    return "Not Available"


# ==========================================
# 🛑 FORCE JOIN MESSAGE HELPER
# ==========================================
def send_force_join_msg(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        telebot.types.InlineKeyboardButton("🔥 Join VIP Group",  url=f"https://t.me/{GROUP_USERNAME.replace('@','')}"),
        telebot.types.InlineKeyboardButton("📢 Join Channel 1",  url=f"https://t.me/{CHANNEL_1.replace('@','')}"),
        telebot.types.InlineKeyboardButton("📢 Join Channel 2",  url=f"https://t.me/{CHANNEL_2.replace('@','')}"),
        telebot.types.InlineKeyboardButton("🤖 Start 2nd Bot",   url=BOT_2_LINK),
        telebot.types.InlineKeyboardButton("✅ Verify",           callback_data=f"verify_{user_id}"),
    )
    premium_msg = """🔥 **ROLEX VIP BOT ACTIVE**
Bhai! Is VIP bot se tum kisi bhi Free Fire ID ki kundali nikal sakte ho. ind type command use kijiye for India server data. Scan data nikalne ke liye niche ind type command follow karein. scan details fast mil jayegi. 🎮

🚫 **ACCESS RESTRICTED** 🚫
Is Premium VIP Bot ko use karne ke liye hamara official group aur dono channels join karna compulsory hai.

👇 **HOW TO UNLOCK:**
1️⃣ Niche diye gaye sabhi buttons par click karke Join karo.
2️⃣ Wapas aakar '✅ Verify' dabao.

⚡ Powered by @RolexBoss62"""
    try:
        with open('1.png', 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=premium_msg, reply_markup=markup, parse_mode="Markdown")
    except FileNotFoundError:
        bot.reply_to(message, premium_msg, reply_markup=markup, parse_mode="Markdown")


# ==========================================
# 🎮 /start
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    log_active_user(user_id)

    is_joined_all = False
    try:
        valid_statuses = ['member', 'administrator', 'creator']
        if (bot.get_chat_member(GROUP_USERNAME, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_1, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2, user_id).status in valid_statuses):
            is_joined_all = True
    except Exception:
        is_joined_all = False

    if not is_joined_all:
        remove_verified_user(user_id)
        send_force_join_msg(message)
    else:
        success_msg = """🔥 **ROLEX VIP BOT ACTIVE**
Bhai, tum pehle se verified ho! 🎉

👇 **NOW YOU CAN USE:**
Type: `/info ind Tumhari_UID` (scan UID details nikalne ke liye)
👉 *Example:* `/info ind 2652073509`

⚡ Powered by @RolexBoss62"""
        try:
            with open('1.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=success_msg, parse_mode="Markdown")
        except FileNotFoundError:
            bot.reply_to(message, success_msg, parse_mode="Markdown")


# ==========================================
# 📡 /info COMMAND
# ==========================================
@bot.message_handler(commands=['info'])
def get_player_info(message):
    user_id = message.from_user.id
    log_active_user(user_id)

    # 1. Live join check
    is_joined_all = False
    try:
        valid_statuses = ['member', 'administrator', 'creator']
        if (bot.get_chat_member(GROUP_USERNAME, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_1, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2, user_id).status in valid_statuses):
            is_joined_all = True
    except Exception:
        is_joined_all = False

    if not is_joined_all:
        remove_verified_user(user_id)
        send_force_join_msg(message)
        return

    # 2. Anti-spam (8 seconds)
    current_time = time.time()
    if user_id in user_cooldowns:
        elapsed = current_time - user_cooldowns[user_id]
        if elapsed < 8:
            bot.reply_to(message, f"⏳ Bhai, spam mat karo! Agli command {int(8 - elapsed)} second baad dena.")
            return
    user_cooldowns[user_id] = current_time

    # 3. Command check
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message,
            "⚠️ **Bhai, command adhoori ya galat hai!**\nSahi tarika ye hai:\n👉 `/info ind 123456789`",
            parse_mode="Markdown")
        return

    region   = args[1].upper()
    uid      = args[2]
    wait_msg = bot.reply_to(message, "⚡ **EXTRACTING VIP DETAILS...**", parse_mode="Markdown")

    # 4. API + Build reply
    try:
        response = requests.get(API_URL, params={'region': region, 'uid': uid}, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                data = data[0]

            # ── Parse all sections (same as original) ───────────────────
            basic   = data.get("basicInfo",      {}) or {}
            profile = data.get("profileInfo",    {}) or {}
            clan    = data.get("clanBasicInfo",  {}) or {}
            captain = data.get("captainBasicInfo",{}) or {}
            pet     = data.get("petInfo",        {}) or {}
            social  = data.get("socialInfo",     {}) or {}
            credit  = data.get("creditScoreInfo",{}) or {}

            # ── Derived values (same logic as original) ──────────────────
            gender      = str(social.get('gender', 'Male')).replace('Gender_', '').title()
            bp_pass     = "Premium" if basic.get('hasElitePass') else "Free"
            mode_prefer = str(social.get('modePrefer', 'CsRanked')).replace('ModePrefer_', '')
            language    = str(social.get('language', 'English')).replace('Language_', '')

            cs_stars_player = get_cs_stars(basic.get('csRank', 0),   basic.get('csRankingPoints', 0))
            cs_stars_leader = get_cs_stars(captain.get('csRank', 0), captain.get('csRankingPoints', 0))

            br_rank_str   = f"{get_br_rank(basic.get('rank',0), basic.get('rankingPoints',0))} ({basic.get('rankingPoints',0)})"
            cs_rank_str   = f"{get_cs_rank(basic.get('csRank',0))} ({cs_stars_player} Star)"
            leader_br_str = f"{get_br_rank(captain.get('rank',0), captain.get('rankingPoints',0))} ({captain.get('rankingPoints',0)})"
            leader_cs_str = f"{get_cs_rank(captain.get('csRank',0))} ({cs_stars_leader} Star)"

            # ── FIX: Prime Level from API (was hardcoded 7 before) ───────
            prime_level = (basic.get('primeLevel')
                        or basic.get('primeMaxLevel')
                        or "Not Available")

            # ── Item name lookups ────────────────────────────────────────
            # Avatar & banner
            avatar_name = get_item_name(profile.get('avatarId'))
            banner_name = get_item_name(basic.get('bannerId'))

            # Title
            title_name = get_item_name(basic.get('title'))

            # Weapon skin shows: [weaponSkin, groupAnim, transformAnim]
            weapon_shows   = basic.get('weaponSkinShows') or []
            equipped_gun   = get_item_name(weapon_shows[0]) if len(weapon_shows) > 0 else "Not Available"
            equipped_anim  = get_item_name(weapon_shows[1]) if len(weapon_shows) > 1 else "Not Available"
            equipped_trans = get_item_name(weapon_shows[2]) if len(weapon_shows) > 2 else "Not Available"

            # Equipped skills — format is groups of 4: [slotType, skillId, ?, slotIndex]
            skills_raw = profile.get('equipedSkills') or []
            if skills_raw:
                skill_ids  = [skills_raw[i] for i in range(1, len(skills_raw), 4) if i < len(skills_raw)]
                skills_str = ", ".join(get_item_name(s) for s in skill_ids) if skill_ids else "Not Available"
            else:
                skills_str = "Not Available"

            # Clothes / outfits
            clothes_raw = profile.get('clothes') or []
            if clothes_raw:
                clothes_lines = "\n".join(
                    f"    {'└' if i == len(clothes_raw)-1 else '├'}─ {get_item_name(c)}"
                    for i, c in enumerate(clothes_raw)
                )
            else:
                clothes_lines = "    └─ Not Available"

            # Pet
            pet_name      = pet.get('name') or "Not Available"
            pet_type_name = get_item_name(pet.get('id')) if pet.get('id') else pet_name
            pet_skin_name = get_item_name(pet.get('skinId'))
            pet_skill_name= get_item_name(pet.get('selectedSkillId'))

            # Guild / clan
            in_guild     = bool(clan.get('clanId'))
            credit_score = credit.get('creditScore', 'Not Available')
            signature    = social.get('signature') or "Not Available"
            leader_bp    = "Premium" if captain.get('hasElitePass') else "Free"

            # ── Premium reply ────────────────────────────────────────────
            reply = f"""╔══════════════════════════════════╗
      🎮 *FREE FIRE VIP INTEL* 🎮
╚══════════════════════════════════╝

*ACCOUNT BASIC INFORMATION* 🔍
┌─────────────────────────────
├─ 👤 Name         : `{basic.get('nickname', 'Unknown')}`
├─ 🆔 UID          : `{uid}`
├─ 🌐 Region       : `{region}`
├─ 🎯 Level        : `{basic.get('level', 0)}` *(EXP: {basic.get('exp', 0)})*
├─ 💎 Prime Level  : `{prime_level}`
├─ ❤️ Likes        : `{basic.get('liked', 0)}`
├─ ⭐ Honor Score  : `{credit_score}`
├─ 🎖️ Title        : `{title_name}`
├─ 🔥 Fire Pass    : `{bp_pass}`
└─ 📝 Signature    : `{signature}`

*ACCOUNT ACTIVITY* 📅
┌─────────────────────────────
├─ 📦 Latest OB    : `{basic.get('releaseVersion', 'N/A')}`
├─ 🏅 BP Badges    : `{basic.get('badgeCnt', 0)}`
├─ 🎯 BR Rank      : `{br_rank_str}`
├─ 🎯 CS Rank      : `{cs_rank_str}`
├─ 👤 Gender       : `{gender}`
├─ 📊 Show Rank    : `{mode_prefer}`
├─ 👁️ Show BR Rank : `{basic.get('showBrRank', True)}`
├─ 👁️ Show CS Rank : `{basic.get('showCsRank', True)}`
├─ 📅 Created At   : `{fmt_t(basic.get('createAt'))}`
└─ 🕐 Last Login   : `{fmt_t(basic.get('lastLoginAt'))}`

*ACCOUNT OVERVIEW* 🧥
┌─────────────────────────────
├─ 🖼️ Avatar ID    : `{avatar_name}`
├─ 🖼️ Banner ID    : `{banner_name}`
├─ 📌 Pin ID       : `Default`
├─ 🌀 Language     : `{language}`
├─ 🔫 Weapon Skin  : `{equipped_gun}`
├─ 💫 Anim ID      : `{equipped_anim}`
├─ 🔄 Transform ID : `{equipped_trans}`
└─ ⚡ Skills       : `{skills_str}`

*OUTFITS* 👕
┌─────────────────────────────
{clothes_lines}

*PET DETAILS* 🐾
┌─────────────────────────────
├─ 🐾 Equipped     : `{'Yes' if pet.get('isSelected') else 'No'}`
├─ 🐶 Pet Name     : `{pet_name}`
├─ 🐾 Pet Type     : `{pet_type_name}`
├─ 🎨 Pet Skin     : `{pet_skin_name}`
├─ ⚡ Pet Skill    : `{pet_skill_name}`
├─ 📊 Pet EXP      : `{pet.get('exp', 0)}`
└─ 🔢 Pet Level    : `{pet.get('level', 'Not Available')}`"""

            # Guild section
            if in_guild:
                reply += f"""

*GUILD INFORMATION* 🛡️
┌─────────────────────────────
├─ 🏰 Guild Name   : `{clan.get('clanName', 'Not Available')}`
├─ 🆔 Guild ID     : `{clan.get('clanId', 'Not Available')}`
├─ 📊 Guild Level  : `{clan.get('clanLevel', 'Not Available')}`
└─ 👥 Members      : `{clan.get('memberNum', 0)}/{clan.get('capacity', 0)}`

*GUILD LEADER INFO* 👑
┌─────────────────────────────
├─ 👤 Name         : `{captain.get('nickname', 'Not Available')}`
├─ 🆔 Leader UID   : `{captain.get('accountId', 'Not Available')}`
├─ 🎮 Level        : `{captain.get('level', 'Not Available')}`
├─ 🌐 Region       : `{region}`
├─ 🔥 Fire Pass    : `{leader_bp}`
├─ 📅 Created At   : `{fmt_t(captain.get('createAt'))}`
├─ 🕐 Last Login   : `{fmt_t(captain.get('lastLoginAt'))}`
├─ 📦 Latest OB    : `{captain.get('releaseVersion', 'N/A')}`
├─ 🏅 BP Badges    : `{captain.get('badgeCnt', 0)}`
├─ 🎯 BR Rank      : `{leader_br_str}`
└─ 🎯 CS Rank      : `{leader_cs_str}`"""
            else:
                reply += """

*GUILD INFORMATION* 🛡️
┌─────────────────────────────
└─ 🚫 *Player is not in any Guild*"""

            reply += """

*PUBLIC CRAFTLAND MAPS* 🗺️
┌─────────────────────────────
└─ 📭 Not Found

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *Bot By ROLEX* | @LikeBotFreeFireMax
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

            bot.delete_message(message.chat.id, wait_msg.message_id)
            bot.send_message(message.chat.id, reply, parse_mode="Markdown")

        else:
            bot.reply_to(message, "❌ **Error:** API ne reply nahi diya.")

    except requests.exceptions.Timeout:
        bot.reply_to(message, "❌ **API Error:** Server abhi slow hai. Kripya thodi der baad try karein!")
    except Exception:
        bot.reply_to(message, "❌ OPERATION FAILED ❌\n━━━━━━━━━━━━━━━━━━\n⚠️ API Error: Token expire ho gaya hai ya invalid hai.\n━━━━━━━━━━━━━━━━━━\n💡 Tip: Message karo owner ko @RolexBoss62")


# ==========================================
# ✅ VERIFY BUTTON LOGIC
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_callback(call):
    user_id = int(call.data.split('_')[1])

    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Ye button tumhare liye nahi hai!", show_alert=True)
        return

    try:
        valid_statuses = ['member', 'administrator', 'creator']
        if (bot.get_chat_member(GROUP_USERNAME, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_1, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2, user_id).status in valid_statuses):

            add_verified_user(user_id)
            log_active_user(user_id)

            success_msg = """✅ **Verification Successful!**

Group aur channels join karne ke liye shukriya! Ab tum apni scan detail nikal sakte ho. 🔥

👇 **NOW YOU CAN USE:**
Type: `/info ind Tumhari_UID` (scan UID details nikalne ke liye)
👉 *Example:* `/info ind 2652073509`"""

            bot.edit_message_caption(
                caption=success_msg,
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.answer_callback_query(
                call.id,
                "❌ Tumne abhi tak saare group aur channels join nahi kiye hain! Pehle sab join karo.",
                show_alert=True
            )
    except Exception as e:
        bot.answer_callback_query(
            call.id,
            "❌ Koi error aayi. Ek baar check karo bot group/channels me admin hai ya nahi.",
            show_alert=True
        )


print("🔥 ROLEX VIP Superfast Bot is starting on Pella...")
bot.infinity_polling(allowed_updates=telebot.util.update_types)


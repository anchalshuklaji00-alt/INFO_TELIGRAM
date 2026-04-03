import telebot
import requests
import os
import json
import time
from datetime import datetime

# 🔥 YAHAN TUMHARA NAYA TOKEN HAI 🔥
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
# 🗃️ ITEM DATABASE (Load at startup)
# ==========================================
ITEM_DB = {}

def _load_item_databases():
    """Load all JSON item files into a combined lookup dict at startup."""
    global ITEM_DB

    # --- 1. ItemData.json (main, oldest) ---
    for fname in ["ItemData.json", "ItemDataOB46.json", "ItemDataOB47.json"]:
        if os.path.exists(fname):
            try:
                with open(fname, encoding="utf-8") as f:
                    for entry in json.load(f):
                        iid  = str(entry.get("itemID", "")).strip()
                        name = (entry.get("description") or "").strip()
                        if iid and name and name.lower() not in ("unread", ""):
                            ITEM_DB.setdefault(iid, name)   # don't overwrite already-loaded
            except Exception:
                pass

    # --- 2. OB50 live (has proper English names, override older) ---
    if os.path.exists("items-OB50-live.json"):
        try:
            with open("items-OB50-live.json", encoding="utf-8") as f:
                for entry in json.load(f):
                    iid  = str(entry.get("Id", "")).strip()
                    name = (entry.get("name") or "").strip()
                    if iid and name and name.lower() not in ("unread", ""):
                        ITEM_DB[iid] = name     # OB50 always wins
        except Exception:
            pass

    # --- 3. OB51 (no names, skip for now) ---

    print(f"✅ Item DB loaded: {len(ITEM_DB)} items")

_load_item_databases()


def get_item_name(item_id, fallback=None):
    """Return human-readable name for an item ID.
    Falls back to the raw ID if not found, or fallback if provided."""
    if not item_id:
        return fallback or "Not Available"
    name = ITEM_DB.get(str(item_id))
    if name:
        return name
    return str(item_id) if item_id else (fallback or "Not Available")


def resolve_skills(skill_list):
    """Convert a list of skill IDs to names."""
    if not skill_list:
        return "Not Available"
    names = [get_item_name(s) for s in skill_list]
    return ", ".join(names[:6])   # limit to 6 to avoid overflow


# ==========================================
# ⚙️ SUPERFAST LIVE TEXT DATABASE SYSTEM
# ==========================================
USER_FILE = "verified_users.txt"
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
    user_id = message.left_chat_member.id
    remove_verified_user(user_id)

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    for member in message.new_chat_members:
        log_active_user(member.id)

@bot.my_chat_member_handler()
def handle_bot_block(message: telebot.types.ChatMemberUpdated):
    if message.new_chat_member.status in ['kicked', 'left']:
        remove_verified_user(message.from_user.id)


# ==========================================
# 🔥 FF RANK & STARS LOGIC
# ==========================================
def get_br_rank(rank_id, points):
    pts = int(points)
    r = str(rank_id)
    if pts >= 6000: return "Master"
    if pts >= 3200: return "Heroic"
    ranks = {
        "11": "Bronze I",    "12": "Bronze II",    "13": "Bronze III",
        "21": "Silver I",    "22": "Silver II",     "23": "Silver III",
        "31": "Gold I",      "32": "Gold II",       "33": "Gold III",    "34": "Gold IV",
        "41": "Platinum I",  "42": "Platinum II",   "43": "Platinum III","44": "Platinum IV","45": "Platinum V",
        "51": "Diamond I",   "52": "Diamond II",    "53": "Diamond III", "54": "Diamond IV","55": "Diamond V",
        "61": "Heroic",      "62": "Elite Heroic",
        "71": "Master",      "72": "Elite Master",
        "81": "Grandmaster I","82": "Grandmaster II","83": "Grandmaster III","84": "Grandmaster IV","85": "Grandmaster V",
        "321": "Diamond V",  "322": "Diamond IV",   "323": "Diamond III","324": "Diamond II","325": "Diamond I",
        "401": "Heroic",     "402": "Elite Heroic",
        "501": "Master",     "502": "Elite Master",
    }
    return ranks.get(r, f"Rank {r}")

def get_cs_rank(rank_id):
    r = str(rank_id)
    ranks = {
        "11": "Bronze I",   "12": "Bronze II",   "13": "Bronze III",
        "21": "Silver I",   "22": "Silver II",    "23": "Silver III",
        "31": "Gold I",     "32": "Gold II",      "33": "Gold III",   "34": "Gold IV",
        "41": "Platinum I", "42": "Platinum II",  "43": "Platinum III","44": "Platinum IV","45": "Platinum V",
        "51": "Diamond I",  "52": "Diamond II",   "53": "Diamond III","54": "Diamond IV","55": "Diamond V",
        "61": "Heroic",     "62": "Elite Heroic",
        "71": "Master",     "72": "Elite Master",
        "81": "Grandmaster I","82": "Grandmaster II","83": "Grandmaster III","84": "Grandmaster IV","85": "Grandmaster V",
        "91": "Grandmaster",
        "324": "Elite Master","321": "Master","311": "Heroic",
        "211": "Diamond I", "212": "Diamond II",  "213": "Diamond III","214": "Diamond IV",
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
        return datetime.fromtimestamp(int(ts)).strftime('%d %B %Y • %I:%M %p')
    return "Not Available"

def val(v, fallback="Not Available"):
    """Return v if truthy and not blank/None, else fallback."""
    if v is None or str(v).strip() in ("", "0", "None", "N/A", "no", "No", "false", "False"):
        return fallback
    return v


# ==========================================
# 🛑 FORCE JOIN MESSAGE HELPER
# ==========================================
def send_force_join_msg(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)

    btn1      = telebot.types.InlineKeyboardButton("🔥 Join VIP Group",   url=f"https://t.me/{GROUP_USERNAME.replace('@','')}")
    btn2      = telebot.types.InlineKeyboardButton("📢 Join Channel 1",   url=f"https://t.me/{CHANNEL_1.replace('@','')}")
    btn3      = telebot.types.InlineKeyboardButton("📢 Join Channel 2",   url=f"https://t.me/{CHANNEL_2.replace('@','')}")
    btn4      = telebot.types.InlineKeyboardButton("🤖 Start 2nd Bot",    url=BOT_2_LINK)
    btn_verify= telebot.types.InlineKeyboardButton("✅ Verify",           callback_data=f"verify_{user_id}")

    markup.add(btn1, btn2, btn3, btn4, btn_verify)

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
# 🎮 MAIN COMMANDS
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    log_active_user(user_id)

    is_joined_all = False
    try:
        valid_statuses = ['member', 'administrator', 'creator']
        if (bot.get_chat_member(GROUP_USERNAME, user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_1,      user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2,      user_id).status in valid_statuses):
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
# 📡 /INFO COMMAND — PREMIUM OUTPUT
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
            bot.get_chat_member(CHANNEL_1,      user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2,      user_id).status in valid_statuses):
            is_joined_all = True
    except Exception:
        is_joined_all = False

    if not is_joined_all:
        remove_verified_user(user_id)
        send_force_join_msg(message)
        return

    # 2. Anti-spam
    current_time = time.time()
    if user_id in user_cooldowns:
        elapsed = current_time - user_cooldowns[user_id]
        if elapsed < 8:
            bot.reply_to(message, f"⏳ Bhai, spam mat karo! Agli command {int(8 - elapsed)} second baad dena.")
            return
    user_cooldowns[user_id] = current_time

    # 3. Command validation
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message,
            "⚠️ *Bhai, command adhoori ya galat hai!*\nSahi tarika ye hai:\n👉 `/info ind 123456789`",
            parse_mode="Markdown")
        return

    region = args[1].upper()
    uid    = args[2]
    wait_msg = bot.reply_to(message, "⚡ *Scanning player data... Please wait!*", parse_mode="Markdown")

    # 4. API call + premium response
    try:
        response = requests.get(API_URL, params={'region': region, 'uid': uid}, timeout=15)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                data = data[0]

            basic   = data.get("basicInfo",    {}) or {}
            profile = data.get("profileInfo",  {}) or {}
            clan    = data.get("clanBasicInfo",{}) or {}
            captain = data.get("captainBasicInfo", {}) or {}
            pet     = data.get("petInfo",      {}) or {}
            social  = data.get("socialInfo",   {}) or {}
            credit  = data.get("creditScoreInfo", {}) or {}

            # ── Derived fields ──────────────────────────────────────────
            gender      = str(social.get('gender', 'Male')).replace('Gender_', '').title()
            bp_pass     = "🔥 Elite Pass" if basic.get('hasElitePass') else "🆓 Free Pass"
            mode_prefer = str(social.get('modePrefer', 'N/A')).replace('ModePrefer_', '')
            language    = str(social.get('language', 'N/A')).replace('Language_', '')
            signature   = social.get('signature') or "—"

            prime_level = basic.get('primeLevel') or basic.get('primeMaxLevel') or "Not Available"

            cs_stars_p  = get_cs_stars(basic.get('csRank', 0),   basic.get('csRankingPoints', 0))
            cs_stars_l  = get_cs_stars(captain.get('csRank', 0), captain.get('csRankingPoints', 0))

            br_rank_str     = f"{get_br_rank(basic.get('rank',0), basic.get('rankingPoints',0))}  ({basic.get('rankingPoints',0)} pts)"
            cs_rank_str     = f"{get_cs_rank(basic.get('csRank',0))}  ({cs_stars_p} ⭐)"
            leader_br_str   = f"{get_br_rank(captain.get('rank',0), captain.get('rankingPoints',0))}  ({captain.get('rankingPoints',0)} pts)"
            leader_cs_str   = f"{get_cs_rank(captain.get('csRank',0))}  ({cs_stars_l} ⭐)"

            # ── Item name lookups ───────────────────────────────────────
            avatar_id   = profile.get('avatarId')
            avatar_name = get_item_name(avatar_id)

            banner_id   = basic.get('bannerId')
            banner_name = get_item_name(banner_id)

            # Weapon skin — weaponSkinShows is a list
            weapon_shows = basic.get('weaponSkinShows') or []
            if weapon_shows:
                weapon_name = get_item_name(weapon_shows[0])
            else:
                weapon_name = "Not Available"

            # Equipped skills
            skills_raw  = profile.get('equipedSkills') or []
            skills_str  = resolve_skills(skills_raw) if skills_raw else "Not Available"

            # Pin
            pin_id   = profile.get('pinId') or basic.get('pinId')
            pin_name = get_item_name(pin_id, fallback="Default")

            # Animation
            anim_id      = profile.get('animationId')    or basic.get('animationId')
            anim_name    = get_item_name(anim_id, fallback="Default")

            transform_id   = profile.get('transformAnimId') or basic.get('transformAnimId')
            transform_name = get_item_name(transform_id, fallback="Default")

            # Pet
            pet_equipped = bool(pet.get('petType') or pet.get('name'))
            pet_name     = pet.get('name') or get_item_name(pet.get('petType'), fallback="Not Available")
            pet_type_name= get_item_name(pet.get('petType'), fallback=pet_name)
            pet_exp      = pet.get('exp', 0)
            pet_level    = pet.get('level') or "Not Available"

            # Guild / clan
            in_guild     = bool(clan.get('clanId'))
            guild_name   = clan.get('clanName')  or "Not in Guild"
            guild_id     = clan.get('clanId')    or "—"
            guild_level  = clan.get('clanLevel') or "—"
            guild_members= f"{clan.get('memberNum',0)}/{clan.get('capacity',0)}" if in_guild else "—"

            # Credit score
            credit_score = credit.get('creditScore') or "Not Available"

            # Leader fire pass
            leader_bp = "🔥 Elite Pass" if captain.get('hasElitePass') else ("🆓 Free Pass" if captain else "Not Available")

            # Outfits list
            outfits_raw = profile.get('outfits') or basic.get('outfits') or []
            if outfits_raw:
                outfits_str = "\n".join(
                    f"  {'└' if i == len(outfits_raw)-1 else '├'}─ {get_item_name(o)}"
                    for i, o in enumerate(outfits_raw)
                )
            else:
                outfits_str = "  └─ Not Available"

            # ── Build premium reply ─────────────────────────────────────
            reply = f"""
╔══════════════════════════════════╗
      🎯 *FREE FIRE PLAYER INTEL*
╚══════════════════════════════════╝

👤 *ACCOUNT PROFILE*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔸 Name         : `{basic.get('nickname','Unknown')}`
🔸 UID          : `{uid}`
🔸 Region       : `{region}`
🔸 Level        : `{basic.get('level', 0)}`  *(EXP: {basic.get('exp', 0)})*
🔸 Prime Level  : `{prime_level}`
🔸 Likes        : `{basic.get('liked', 0)}`
🔸 Honor Score  : `{credit_score}`
🔸 Gender       : `{gender}`
🔸 Language     : `{language}`
🔸 Fire Pass    : {bp_pass}
🔸 Signature    : _{signature}_

📅 *ACTIVITY LOG*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Last OB      : `{basic.get('releaseVersion','N/A')}`
📌 Joined       : `{fmt_t(basic.get('createAt'))}`
📌 Last Login   : `{fmt_t(basic.get('lastLoginAt'))}`
📌 Show BR Rank : `{basic.get('showBrRank', 'N/A')}`
📌 Show CS Rank : `{basic.get('showCsRank', 'N/A')}`
📌 Preferred Mode : `{mode_prefer}`

🏆 *RANK INFO*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 BR Rank      : `{br_rank_str}`
🎯 CS Rank      : `{cs_rank_str}`
🎯 BP Badges    : `{basic.get('badgeCnt', 0)}`

🧥 *COSMETICS & GEAR*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🖼 Avatar       : `{avatar_name}`
🖼 Banner       : `{banner_name}`
📌 Pin          : `{pin_name}`
🔫 Weapon Skin  : `{weapon_name}`
💫 Animation    : `{anim_name}`
🔄 Transform    : `{transform_name}`
⚡ Skills       : `{skills_str}`

👕 *OUTFITS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{outfits_str}

🐾 *PET DETAILS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐶 Equipped     : `{'Yes' if pet_equipped else 'No'}`
🐶 Pet Name     : `{pet_name}`
🐶 Pet Type     : `{pet_type_name}`
🐶 Pet EXP      : `{pet_exp}`
🐶 Pet Level    : `{pet_level}`"""

            # ── Guild section ───────────────────────────────────────────
            if in_guild:
                reply += f"""

🛡️ *GUILD INFORMATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏰 Guild Name   : `{guild_name}`
🆔 Guild ID     : `{guild_id}`
📊 Guild Level  : `{guild_level}`
👥 Members      : `{guild_members}`

👑 *GUILD LEADER*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 Name         : `{captain.get('nickname','Not Available')}`
🆔 UID          : `{captain.get('accountId','Not Available')}`
🎮 Level        : `{captain.get('level','Not Available')}`
🌐 Region       : `{region}`
🔥 Fire Pass    : {leader_bp}
🏆 BR Rank      : `{leader_br_str}`
🏆 CS Rank      : `{leader_cs_str}`
🎖️ BP Badges   : `{captain.get('badgeCnt', 0)}`
📌 Last OB      : `{captain.get('releaseVersion','N/A')}`
📅 Joined       : `{fmt_t(captain.get('createAt'))}`
📅 Last Login   : `{fmt_t(captain.get('lastLoginAt'))}`"""
            else:
                reply += f"""

🛡️ *GUILD INFORMATION*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚫 *This player is not in any Guild*"""

            reply += f"""

🗺️ *CRAFTLAND MAPS*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📭 No public Craftland maps found.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ *Scanned by ROLEX VIP Bot*
🔗 Group: @LikeBotFreeFireMax
━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

            bot.delete_message(message.chat.id, wait_msg.message_id)
            bot.send_message(message.chat.id, reply, parse_mode="Markdown")

        else:
            bot.edit_message_text(
                "❌ *API Error:* Player data nahi mila. UID ya Region check karo.",
                chat_id=message.chat.id,
                message_id=wait_msg.message_id,
                parse_mode="Markdown"
            )

    except requests.exceptions.Timeout:
        bot.edit_message_text(
            "❌ *Timeout:* Server abhi slow hai. Thodi der baad try karo!",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.edit_message_text(
            f"❌ *OPERATION FAILED*\n━━━━━━━━━━━━━━━━\n⚠️ Token expire ho gaya ya API down hai.\n💡 Owner ko message karo: @RolexBoss62",
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            parse_mode="Markdown"
        )


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
            bot.get_chat_member(CHANNEL_1,      user_id).status in valid_statuses and
            bot.get_chat_member(CHANNEL_2,      user_id).status in valid_statuses):

            add_verified_user(user_id)
            log_active_user(user_id)

            success_msg = """✅ *Verification Successful!*

Group aur channels join karne ke liye shukriya! Ab tum apni scan detail nikal sakte ho. 🔥

👇 *NOW YOU CAN USE:*
Type: `/info ind Tumhari_UID`
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
                "❌ Tumne abhi tak saare group aur channels join nahi kiye! Pehle sab join karo.",
                show_alert=True
            )
    except Exception:
        bot.answer_callback_query(
            call.id,
            "❌ Koi error aayi. Check karo bot group/channels me admin hai ya nahi.",
            show_alert=True
        )


print("🔥 ROLEX VIP Bot is starting...")
bot.infinity_polling(allowed_updates=telebot.util.update_types)


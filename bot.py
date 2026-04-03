import telebot
import requests
import os
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
# ⚙️ SUPERFAST LIVE TEXT DATABASE SYSTEM
# ==========================================
USER_FILE = "verified_users.txt"
ALL_USERS_FILE = "all_users_bot.txt"

# Agar files nahi hain toh automatic bana dega
for file in [USER_FILE, ALL_USERS_FILE]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            pass

# Anti-Spam Timer (8 Seconds)
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
        "11": "Bronze I", "12": "Bronze II", "13": "Bronze III",
        "21": "Silver I", "22": "Silver II", "23": "Silver III",
        "31": "Gold I", "32": "Gold II", "33": "Gold III", "34": "Gold IV",
        "41": "Platinum I", "42": "Platinum II", "43": "Platinum III", "44": "Platinum IV", "45": "Platinum V",
        "51": "Diamond I", "52": "Diamond II", "53": "Diamond III", "54": "Diamond IV", "55": "Diamond V",
        "61": "Heroic", "62": "Elite Heroic",
        "71": "Master", "72": "Elite Master",
        "81": "Grandmaster I", "82": "Grandmaster II", "83": "Grandmaster III", "84": "Grandmaster IV", "85": "Grandmaster V",
        "321": "Diamond V", "322": "Diamond IV", "323": "Diamond III", "324": "Diamond II", "325": "Diamond I",
        "401": "Heroic", "402": "Elite Heroic", "501": "Master", "502": "Elite Master"
    }
    return ranks.get(r, f"Rank {r}")

def get_cs_rank(rank_id):
    r = str(rank_id)
    ranks = {
        "11": "Bronze I", "12": "Bronze II", "13": "Bronze III",
        "21": "Silver I", "22": "Silver II", "23": "Silver III",
        "31": "Gold I", "32": "Gold II", "33": "Gold III", "34": "Gold IV",
        "41": "Platinum I", "42": "Platinum II", "43": "Platinum III", "44": "Platinum IV", "45": "Platinum V",
        "51": "Diamond I", "52": "Diamond II", "53": "Diamond III", "54": "Diamond IV", "55": "Diamond V",
        "61": "Heroic", "62": "Elite Heroic",
        "71": "Master", "72": "Elite Master",
        "81": "Grandmaster I", "82": "Grandmaster II", "83": "Grandmaster III", "84": "Grandmaster IV", "85": "Grandmaster V",
        "91": "Grandmaster",
        "324": "Elite Master", "321": "Master", "311": "Heroic",
        "211": "Diamond I", "212": "Diamond II", "213": "Diamond III", "214": "Diamond IV"
    }
    return ranks.get(r, f"Rank {r}")

def get_cs_stars(rank_id, points):
    pts = int(points)
    r_id = int(rank_id)
    if r_id >= 311: return max(0, pts - 87)
    return pts

def fmt_t(ts):
    if ts and str(ts).isdigit():
        return datetime.fromtimestamp(int(ts)).strftime('%d %B %Y at %I:%M:%S %p')
    return "N/A"

# ==========================================
# 🛑 COMMON FORCE JOIN MESSAGE HELPER
# ==========================================
def send_force_join_msg(message):
    user_id = message.from_user.id
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    
    btn1 = telebot.types.InlineKeyboardButton("🔥 Join VIP Group", url=f"https://t.me/{GROUP_USERNAME.replace('@', '')}")
    btn2 = telebot.types.InlineKeyboardButton("📢 Join Channel 1", url=f"https://t.me/{CHANNEL_1.replace('@', '')}")
    btn3 = telebot.types.InlineKeyboardButton("📢 Join Channel 2", url=f"https://t.me/{CHANNEL_2.replace('@', '')}")
    btn4 = telebot.types.InlineKeyboardButton("🤖 Start 2nd Bot", url=BOT_2_LINK)
    btn_verify = telebot.types.InlineKeyboardButton("✅ Verify", callback_data=f"verify_{user_id}")
    
    markup.add(btn1, btn2, btn3, btn4, btn_verify)
    
    premium_msg = """🔥 **ROLEX VIP BOT ACTIVE**
Bhai! Is VIP bot se tum kisi bhi Free Fire ID ki kundali nikal sakte ho. ind type command use kijiye for India server data. Scan data nikalne ke liye niche ind typecommand follow karein. scan details fast mil jayegi. 🎮

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
    
    # ⚡ LIVE API CHECK ON /START ⚡
    is_joined_all = False
    try:
        valid_statuses = ['member', 'administrator', 'creator']
        status_grp = bot.get_chat_member(GROUP_USERNAME, user_id).status
        status_ch1 = bot.get_chat_member(CHANNEL_1, user_id).status
        status_ch2 = bot.get_chat_member(CHANNEL_2, user_id).status

        if status_grp in valid_statuses and status_ch1 in valid_statuses and status_ch2 in valid_statuses:
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


@bot.message_handler(commands=['info'])
def get_player_info(message):
    user_id = message.from_user.id
    log_active_user(user_id)

    # ⚡ 1. LIVE PREMIUM FORCE JOIN CHECKER ⚡
    is_joined_all = False
    try:
        valid_statuses = ['member', 'administrator', 'creator']
        status_grp = bot.get_chat_member(GROUP_USERNAME, user_id).status
        status_ch1 = bot.get_chat_member(CHANNEL_1, user_id).status
        status_ch2 = bot.get_chat_member(CHANNEL_2, user_id).status

        if status_grp in valid_statuses and status_ch1 in valid_statuses and status_ch2 in valid_statuses:
            is_joined_all = True
    except Exception:
        is_joined_all = False 

    if not is_joined_all:
        remove_verified_user(user_id) 
        send_force_join_msg(message)
        return

    # ⚡ 2. 8-SECOND ANTI-SPAM TIMER ⚡
    current_time = time.time()
    if user_id in user_cooldowns:
        elapsed = current_time - user_cooldowns[user_id]
        if elapsed < 8:
            bot.reply_to(message, f"⏳ Bhai, spam mat karo! Agli command {int(8 - elapsed)} second baad dena.")
            return
    user_cooldowns[user_id] = current_time

    # ⚡ 3. COMMAND CHECKER ⚡
    args = message.text.split()
    if len(args) != 3:
        error_msg = "⚠️ **Bhai, command adhoori ya galat hai!**\nSahi tarika ye hai:\n👉 `/info ind 123456789`"
        bot.reply_to(message, error_msg, parse_mode="Markdown")
        return

    region = args[1].upper() 
    uid = args[2]
    wait_msg = bot.reply_to(message, "⚡ **EXTRACTING VIP DETAILS...**", parse_mode="Markdown")

    # ⚡ 4. API REQUEST & DATA PARSING ⚡
    try:
        response = requests.get(API_URL, params={'region': region, 'uid': uid}, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list): data = data[0]
            
            basic = data.get("basicInfo", {})
            profile = data.get("profileInfo", {})
            clan = data.get("clanBasicInfo", {})
            captain = data.get("captainBasicInfo", {})
            pet = data.get("petInfo", {})
            social = data.get("socialInfo", {})
            credit = data.get("creditScoreInfo", {})

            gender = str(social.get('gender', 'Male')).replace('Gender_', '').title()
            bp_pass = "Premium" if basic.get('hasElitePass') else "Free"
            mode_prefer = str(social.get('modePrefer', 'CsRanked')).replace('ModePrefer_', '')
            language = str(social.get('language', 'English')).replace('Language_', '')
            
            cs_stars_player = get_cs_stars(basic.get('csRank', 0), basic.get('csRankingPoints', 0))
            cs_stars_leader = get_cs_stars(captain.get('csRank', 0), captain.get('csRankingPoints', 0))

            br_rank_str = f"{get_br_rank(basic.get('rank', 0), basic.get('rankingPoints', 0))} ({basic.get('rankingPoints', 0)})"
            cs_rank_str = f"{get_cs_rank(basic.get('csRank', 0))} ({cs_stars_player} Star)"
            
            leader_br_str = f"{get_br_rank(captain.get('rank', 0), captain.get('rankingPoints', 0))} ({captain.get('rankingPoints', 0)})"
            leader_cs_str = f"{get_cs_rank(captain.get('csRank', 0))} ({cs_stars_leader} Star)"

            prime_level = social.get('primeLevel', basic.get('primeLevel', '0'))
            is_celebrity = basic.get('isCelebrity', 'False')
            title_name = basic.get('title', 'Headshot Artist')
            
            # 🔥 CRAFTLAND MAPS DYNAMIC LOGIC 🔥
            craftland_data = data.get('craftlandInfo', data.get('craftland', None))
            if craftland_data:
                craftland_text = f"┗ ✅ Maps Available: {craftland_data}" 
            else:
                craftland_text = "┗ ❌ Not Found"
            
            # 🔥 NEW PREMIUM VIP LOOK UI 🔥
            reply = f"""👑 **𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡** 👑

👤 **𝗕𝗔𝗦𝗜𝗖 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
┣ 🌟 **Prime Level:** {prime_level}
┣ 📛 **Name:** {basic.get('nickname', 'Unknown')}
┣ 🆔 **UID:** {uid}
┣ 📊 **Level:** {basic.get('level', 0)} (Exp: {basic.get('exp', 0)})
┣ 🌍 **Region:** {region}
┣ ❤️ **Likes:** {basic.get('liked', 0)}
┣ 🛡️ **Honor Score:** {credit.get('creditScore', 'N/A')}
┣ 💫 **Celebrity Status:** {is_celebrity}
┣ 🏆 **Title Name:** {title_name}
┗ ✍️ **Signature:** {social.get('signature', 'No Signature')}

📊 **𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗔𝗖𝗧𝗜𝗩𝗜𝗧Ｙ**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
┣ 🔄 **Most Recent OB:** {basic.get('releaseVersion', 'OB52')}
┣ 🎫 **Fire Pass:** {bp_pass}
┣ 🎖️ **Current Bp Badges:** {basic.get('badgeCnt', 0)}
┣ ⚔️ **Br Rank:** {br_rank_str}
┣ 🔫 **Cs Rank:** {cs_rank_str}
┣ 🚻 **Gender:** {gender}
┣ 🎯 **Show Rank:** {mode_prefer}
┣ 👁️ **Show Br Rank:** {basic.get('showBrRank', True)}
┣ 👁️ **Show Cs Rank:** {basic.get('showCsRank', True)}
┣ 📅 **Created At:** {fmt_t(basic.get('createAt'))}
┗ 🕒 **Last Login:** {fmt_t(basic.get('lastLoginAt'))}

🔎 **𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗢𝗩𝗘𝗥𝗩𝗜𝗘𝗪**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
┣ 🖼️ **Avatar ID:** {profile.get('avatarId', 'N/A')}
┣ 🏙️ **Banner ID:** {basic.get('bannerId', 'N/A')}
┣ 📍 **Pin ID:** Default
┣ ⏱️ **Active Time:** Flexible
┣ 📆 **Active Days:** Flexible
┣ 🎮 **Mode Prefer:** {mode_prefer}
┣ 🔮 **Equipped Skills:** {", ".join(map(str, profile.get('equipedSkills', [])))[:40]}
┣ 🗣️ **Language:** {language}
┣ 🃏 **Equipped Battle Card ID:** Not Equipped
┣ 🔫 **Equipped Gun ID:** {basic.get('weaponSkinShows', ['None'])[0]}
┣ 🏃 **Equipped Animation ID:** 912050001
┣ ⚡ **Transform Animation ID:** 914050001
┗ 👕 **Outfits:** Graphically Presented Below

🐾 **𝗣𝗘𝗧 𝗗𝗘𝗧𝗔𝗜𝗟𝗦**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
┣ 🎒 **Equipped?:** {'Yes' if pet.get('name') else 'No'}
┣ 🐕 **Pet Name:** {pet.get('name', 'N/A')}
┣ 🏷️ **Pet Type:** {pet.get('name', 'N/A')}
┣ 📈 **Pet Exp:** {pet.get('exp', 0)}
┗ 🎖️ **Pet Level:** {pet.get('level', 'N/A')}

🛡️ **𝗚𝗨𝗜𝗟𝗗 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
┣ 🔰 **Guild Name:** {clan.get('clanName', 'No Guild')}
┣ 🆔 **Guild ID:** {clan.get('clanId', 'N/A')}
┣ 📊 **Guild Level:** {clan.get('clanLevel', 'N/A')}
┣ 👥 **Live Members:** {clan.get('memberNum', 0)}/{clan.get('capacity', 0)}
┗ 👑 **Leader Information:**
    ┣ 👤 **Leader Name:** {captain.get('nickname', 'N/A')}
    ┣ 🆔 **Leader UID:** {captain.get('accountId', 'N/A')}
    ┣ 📊 **Leader Level:** {captain.get('level', 'N/A')}
    ┣ 🌍 **Leader Region:** {region}
    ┣ 🎫 **Leader Fire Pass:** Premium
    ┣ 📅 **Leader Created At:** {fmt_t(captain.get('createAt'))}
    ┣ 🕒 **Leader Last Login:** {fmt_t(captain.get('lastLoginAt'))}
    ┣ 🔄 **Leader Most Recent OB:** {captain.get('releaseVersion', 'OB52')}
    ┣ 🏆 **Leader Title Name:** Headshot Artist
    ┣ 🎖️ **Leader Current Bp Badges:** {captain.get('badgeCnt', 0)}
    ┣ ⚔️ **Leader Br Rank:** {leader_br_str}
    ┗ 🔫 **Leader Cs Rank:** {leader_cs_str}

🗺️ **𝗣𝗨𝗕𝗟𝗜𝗖 𝗖𝗥𝗔𝗙𝗧𝗟𝗔𝗡𝗗 𝗠𝗔𝗣𝗦**
┏━━━━━━━━━━━━━━━━━━━━━━━━━━
{craftland_text}

✨ *Bot By ROLEX*"""

            bot.delete_message(message.chat.id, wait_msg.message_id)
            bot.send_message(message.chat.id, reply)

        else:
            bot.reply_to(message, "❌ **Error:** API ne reply nahi diya.")
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "❌ **API Error:** Server abhi slow hai. Kripya thodi der baad try karein!")
    except Exception:
        bot.reply_to(message, "❌ OPERATION FAILED ❌\n━━━━━━━━━━━━━━━━━━\n⚠️ API Error: Token expire ho gaya hai ya invalid hai.\n━━━━━━━━━━━━━━━━━━\n💡 Tip: Message karo owner ko @RolexBoss62")


# ==========================================
# ✅ MULTI-VERIFY BUTTON LOGIC (Group + 2 Channels)
# ==========================================
@bot.callback_query_handler(func=lambda call: call.data.startswith('verify_'))
def verify_callback(call):
    user_id = int(call.data.split('_')[1])
    
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "❌ Ye button tumhare liye nahi hai!", show_alert=True)
        return

    try:
        valid_statuses = ['member', 'administrator', 'creator']
        
        status_grp = bot.get_chat_member(GROUP_USERNAME, user_id).status
        status_ch1 = bot.get_chat_member(CHANNEL_1, user_id).status
        status_ch2 = bot.get_chat_member(CHANNEL_2, user_id).status

        if status_grp in valid_statuses and status_ch1 in valid_statuses and status_ch2 in valid_statuses:
            add_verified_user(user_id)
            log_active_user(user_id)
            
            success_msg = """✅ **Verification Successful!**

Group aur channels join karne ke liye shukriya! Ab tum apni scan detail nikal sakte ho. 🔥

👇 **NOW YOU CAN USE:**
Type: `/info ind Tumhari_UID` (scan UID details nikalne ke liye)
👉 *Example:* `/info ind 2652073509`"""

            bot.edit_message_caption(caption=success_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="Markdown")
        else:
            bot.answer_callback_query(call.id, "❌ Tumne abhi tak saare group aur channels join nahi kiye hain! Pehle sab join karo.", show_alert=True)
    except Exception as e:
        bot.answer_callback_query(call.id, "❌ Koi error aayi. Ek baar check karo bot group/channels me admin hai ya nahi.", show_alert=True)

print("🔥 ROLEX VIP Superfast Bot is starting on Pella...")
bot.infinity_polling(allowed_updates=telebot.util.update_types)


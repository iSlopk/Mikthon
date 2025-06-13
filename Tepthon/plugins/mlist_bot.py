import asyncio
from telethon import events, Button

from . import zedub
from ..core.managers import edit_or_reply

plugin_category = "البوت"

MLIST_DATA = {}  # {(chat_id, reply_to_id): set(user_ids)}
MLIST_MSGS = {}  # {(chat_id, reply_to_id): message_id}
LOG_CHANNEL_ID = None  # مؤقتاً في الرام، وسنحفظه دائمًا بـ gvar

# --- دعم تعيين قناة اللوق ---
from ..sql_helper.globals import addgvar, gvarstatus, delgvar

@zedub.bot_cmd(pattern="^/msetlog$")
async def set_log_channel(event):
    if not event.is_reply:
        return await event.reply("قم بتحويل رسالة من قناة اللوق إلى البوت ثم أرسل الأمر /msetlog بالرد عليها.")
    reply = await event.get_reply_message()
    if not getattr(reply, "peer_id", None):
        return await event.reply("تعذر التعرف على القناة.")
    chat_id = reply.peer_id.channel_id if hasattr(reply.peer_id, 'channel_id') else reply.chat_id
    addgvar("mlist_log_channel", str(chat_id))
    await event.reply(f"✅ تم تعيين قناة اللوق بنجاح: `{chat_id}`")

@zedub.bot_cmd(pattern="^/mdellog$")
async def del_log_channel(event):
    if not gvarstatus("mlist_log_channel"):
        return await event.reply("❗️ لا يوجد قناة لوق معينة مسبقاً.")
    delgvar("mlist_log_channel")
    await event.reply("تم إلغاء تعيين قناة اللوق بنجاح.")

def get_log_channel():
    cid = gvarstatus("mlist_log_channel")
    if cid:
        try:
            return int(cid)
        except Exception:
            return None
    return None

async def send_log(client, text):
    channel_id = get_log_channel()
    if not channel_id:
        return
    try:
        await client.send_message(channel_id, text, parse_mode="html")
    except Exception:
        pass

async def get_names(client, user_ids):
    names = []
    for uid in user_ids:
        try:
            entity = await client.get_entity(uid)
            names.append(f"- [{entity.first_name}](tg://user?id={uid})")
        except Exception:
            continue
    return names

def get_key(event):
    reply_to = event.reply_to_msg_id if getattr(event, "reply_to_msg_id", None) else event.id
    return (event.chat_id, reply_to)

async def update_mlist_message(client, chat_id, reply_to, key):
    user_ids = MLIST_DATA.get(key, set())
    names = await get_names(client, list(user_ids))
    text = "**قـائـمـة الـمـشـرفـيـن الـحـضـور:**\n" + ("\n".join(names) if names else "_لا يوجد أحد بعد_")
    btns = [
        [
            Button.inline("Log In 🟢", data=f"mlogin|{chat_id}|{reply_to}"),
            Button.inline("Log Out 🔴", data=f"mlogout|{chat_id}|{reply_to}")
        ]
    ]
    try:
        msg_id = MLIST_MSGS.get(key)
        if msg_id:
            await client.edit_message(chat_id, msg_id, text, buttons=btns, link_preview=False)
    except Exception:
        pass

@zedub.bot_cmd(pattern="^/mlist$")
async def mlist_handler(event):
    key = get_key(event)
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    chat_id, reply_to = key
    names = await get_names(event.client, list(MLIST_DATA[key]))
    text = "**قـائـمـة الـمـشـرفـيـن الـحـض("Log In 🟢", data=f"mlogin|{chat_id}|{reply_to}"),
            Button.inline("Log Out 🔴", data=f"mlogout|{chat_id}|{reply_to}")
        ]
    ]
    msg = await event.reply(text, buttons=btns, link_preview=False)
    MLIST_MSGS[key] = msg.id

@zedub.bot_cmd(pattern="^/in$")
async def mlist_in(event):
    key = get_key(event)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    MLIST_id    await update_mlist_message(event.client, key[0], key[1], key)
    msg = await event.reply("تم تسجيل حضورك ✅")
    asyncio.create_task(delete_later(msg))
    user = await event.client.get_entity(user_id)
    await send_log(event.client, f"✅ <b>{user.first_name}</b> (<code>{user_id}</code>) قام بتسجيل الحضور.")

@zedub.bot_cmd(pattern="^/out$")
async def mlist_out(event):
    key = get_key(event)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    if user_id in MLIST_DATA[key]:
        MLIST_DATA[key].remove(user_id)
        await update_mlist_message(event.client, key[0], key[1], key)
        msg = await event.reply("تم تسجيل خروجك ❌")
        asyncio.create_task(delete_later(msg))
        user = await event.client.get_entity(user_id)
        await send_log(event.client, f"❌ <b>{user.first_name}</b> (<code>{user_id}</code>) قام بتسجيل الخروج.")
    else:
        msg = await event.reply("أنت لست ضمن القائمة!")
        asyncio.create_task(delete_later(msg))

async def delete_later(msg):
    await asyncio.sleep(4)
    try:
        await msg.delete()
    except Exception:
        pass

@zedub.on(events.CallbackQuery(pattern=r"mlogin\|(-?\d+)\|(\d+)"))
async def mlogin_handler(event):
    chat_id = int(event.pattern_match.group(1))
    reply_to = int(event.pattern_match.group(2))
    key = (chat_id, reply_to)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    MLIST_DATA[key].add(user_id)
    await update_mlist_message(event.client, chat_id, reply_to, key)
    await event.answer("تم تسجيل حضورك ✅", alert=False)
    user = await event.client.get_entity(user_id)
    await send_log(event.client, f"✅ <b>{user.first_name}</b> (<code>{user_id}</code>) قام بتسجيل الحضور.")

@zedub.on(events.CallbackQuery(pattern=r"mlogout\|(-?\d+)\|(\d+)"))
async def mlogout_handler(event):
    chat_id = int(event.pattern_match.group(1))
    reply_to = int(event.pattern_match.group(2))
    key = (chat_id, reply_to)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    if user_id in MLIST_DATA[key]:
        MLIST_DATA[key].remove(user_id)
        await update_mlist_message(event.client, chat_id, reply_to, key)
        await event.answer("تم تسجيل خروجك ❌", alert=False)
        user = await event.client.get_entity(user_id)
        await send_log(event.client, f"❌ <b>{user.first_name}</b> (<code>{user_id}</code>) قام بتسجيل الخروج.")
    else:
        await event.answer("أنت لست ضمن القائمة!", alert=False)
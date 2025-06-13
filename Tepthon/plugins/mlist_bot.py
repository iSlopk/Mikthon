import asyncio
from telethon import events, Button

from . import zedub
from ..core.managers import edit_or_reply

plugin_category = "البوت"

MLIST_DATA = {}  # {(chat_id, reply_to_id): set(user_ids)}
MLIST_MSGS = {}  # {(chat_id, reply_to_id): message_id}

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
    # مفتاح خاص بكل موضوع (أو برسالة الرد)
    reply_to = event.reply_to_msg_id if getattr(event, "reply_to_msg_id", None) else event.id
    return (event.chat_id, reply_to)

async def update_mlist_message(client, chat_id, reply_to, key):
    user_ids = MLIST_DATA.get(key, set())
    names = await get_names(client, list(user_ids))
    text = "**قائمة الحضور:**\n" + ("\n".join(names) if names else "_لا يوجد أحد بعد_")
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
    text = "**قائمة الحضور:**\n" + ("\n".join(names) if names else "_لا يوجد أحد بعد_")
    btns = [
        [
            Button.inline("Log In 🟢", data=f"mlogin|{chat_id}|{reply_to}"),
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
    MLIST_DATA[key].add(user_id)
    await update_mlist_message(event.client, key[0], key[1], key)
    await event.reply("تم تسجيل حضورك ✅")

@zedub.bot_cmd(pattern="^/out$")
async def mlist_out(event):
    key = get_key(event)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    if user_id in MLIST_DATA[key]:
        MLIST_DATA[key].remove(user_id)
        await update_mlist_message(event.client, key[0], key[1], key)
        await event.reply("تم تسجيل خروجك ❌")
    else:
        await event.reply("أنت لست ضمن القائمة!")

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
    else:
        await event.answer("أنت لست ضمن القائمة!", alert=False)
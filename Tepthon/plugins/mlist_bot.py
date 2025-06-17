import asyncio
from telethon import events, Button, functions
from telethon.events import CallbackQuery, InlineQuery

from . import zedub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from pySmartDL import SmartDL


MLIST_DATA = {}  
MLIST_MSGS = {}  

plugin_category = "البوت"
botusername = Config.TG_BOT_USERNAME
cmhd = Config.COMMAND_HAND_LER


async def get_topic_id_by_name(client, chat_id, topic_name):
    try:
        topics = await client(functions.messages.GetForumTopicsRequest(peer=chat_id, q=topic_name, offset_date=0, offset_id=0, offset_topic=0, limit=100))
        for topic in topics.topics:
            if topic.title == topic_name:
                return topic.id
    except Exception:
        pass
    return None
    
    
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
    text = "**قـائـمـة الـمـشـرفـيـن الـحـضـور:**\n\n" + ("\n".join(names) if names else "لا مشرف متواجد حالياً 👀")
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
    text = "**قـائـمـة الـمـشـرفـيـن الـحـضـور:**\n" + ("\n".join(names) if names else "لا مشرف متواجد حالياً 👀")
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
    msg = await event.reply("تم تسجيل حضورك ✅")
    asyncio.create_task(delete_later(msg))
    user = await event.client.get_entity(user_id)
    topic_id = await get_topic_id_by_name(event.client, event.chat_id, "Mlist Log")
    if topic_id:
        await event.client.send_message(
            entity=event.chat_id,
            message=f"👤 **المستخدم** : [{user.first_name}](tg://user?id={user.id})\n 🟢 سجل حضوره الآن.",
            reply_to=None,
            thread_id=topic_id
        )

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

    else:
        msg = await event.reply("أنت لست ضمن القائمة!")
    topic_id = await get_topic_id_by_name(event.client, event.chat_id, "Mlist Log")
    if topic_id:
        await event.client.send_message(
            entity=event.chat_id,
            message=f"👤 **المستخدم** : [{user.first_name}](tg://user?id={user.id})\n 🔴 سجل خروجه الآن.",
            reply_to=None,
            thread_id=topic_id
        )


        asyncio.create_task(delete_later(msg))

async def delete_later(msg):
    await asyncio.sleep(4)
    try:
        await msg.delete()
    except Exception:
        pass

@zedub.tgbot.on(events.CallbackQuery(pattern=r"mlogin\|(-?\d+)\|(\d+)"))
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
    topic_id = await get_topic_id_by_name(event.client, event.chat_id, "Mlist Log")
    if topic_id:
        await event.client.send_message(
            entity=event.chat_id,
            message=f"👤 **المستخدم** : [{user.first_name}](tg://user?id={user.id})\n 🟢 سجل حضوره الآن.",
            reply_to=None,
            thread_id=topic_id
        )

@zedub.tgbot.on(events.CallbackQuery(pattern=r"mlogout\|(-?\d+)\|(\d+)"))
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
    else:
        await event.answer("أنت لست ضمن القائمة!", alert=False)
        
    
    topic_id = await get_topic_id_by_name(event.client, event.chat_id, "Mlist Log")
    if topic_id:
        await event.client.send_message(
            entity=event.chat_id,
            message=f"👤 **المستخدم** : [{user.first_name}](tg://user?id={user.id})\n 🔴 سجل خروجه الآن.",
            reply_to=None,
            thread_id=topic_id
        )
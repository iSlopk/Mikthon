# -*- coding: utf-8 -*-
# Plugin: mlist attendance for ZThon

import asyncio
from telethon import events, Button
from telethon.tl.types import PeerChannel

from Tepthon import zedub
from Tepthon.core.logger import logging
from Tepthon.core.managers import edit_or_reply

plugin_category = "الخدمات"

# تخزين القائمة والرسالة لكل موضوع
MLIST_DATA = {}  # { (chat_id, topic_id): set(user_ids) }
MLIST_MSGS = {}  # { (chat_id, topic_id): message_id }

async def get_names(client, user_ids):
    names = []
    for uid in user_ids:
        try:
            entity = await client.get_entity(uid)
            names.append(f"- [{entity.first_name}](tg://user?id={uid})")
        except Exception:
            continue
    return names

def get_topic_id(event):
    """
    استخراج رقم الموضوع (thread_id) من الرسالة أو الرد.
    """
    if getattr(event, "reply_to_msg_id", None):
        return getattr(event, "reply_to_msg_id", event.id)
    if hasattr(event, "forum_topic_id") and event.forum_topic_id:
        return event.forum_topic_id
    if hasattr(event, "message") and hasattr(event.message, "reply_to_msg_id") and event.message.reply_to_msg_id:
        return event.message.reply_to_msg_id
    return event.id

async def update_mlist_message(client, chat_id, topic_id):
    key = (chat_id, topic_id)
    user_ids = MLIST_DATA.get(key, set())
    names = await get_names(client, list(user_ids))
    text = "**قائمة الحضور:**\n"
    text += "\n".join(names) if names else "_لا يوجد أحد بعد_"
    btns = [
        [Button.inline("Log In 🟢", data=f"mlogin|{chat_id}|{topic_id}"),
         Button.inline("Log Out 🔴", data=f"mlogout|{chat_id}|{topic_id}")]
    ]
    try:
        msg_id = MLIST_MSGS.get(key)
        if msg_id:
            await client.edit_message(chat_id, msg_id, text, buttons=btns, link_preview=False)
    except Exception as e:
        logging.getLogger(__name__).error(f"MLIST: تحديث الرسالة فشل: {e}")

@zedub.zed_cmd(
    pattern="mlist$",
    command=("mlist", plugin_category),
    info={
        "header": "قائمة حضور تفاعلية مع أزرار تسجيل الدخول والخروج.",
        "usage": "/mlist",
    },
)
async def mlist_handler(event):
    chat_id = event.chat_id
    topic_id = get_topic_id(event)
    key = (chat_id, topic_id)
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    names = await get_names(event.client, list(MLIST_DATA[key]))
    text = "**قائمة الحضور:**\n"
    text += "\n".join(names) if names else "_لا يوجد أحد بعد_"
    btns = [
        [Button.inline("Log In 🟢", data=f"mlogin|{chat_id}|{topic_id}"),
         Button.inline("Log Out 🔴", data=f"mlogout|{chat_id}|{topic_id}")]
    ]
    msg = await event.respond(text, buttons=btns, reply_to=topic_id, link_preview=False)
    MLIST_MSGS[key] = msg.id

@zedub.zed_cmd(pattern="in$", command=("in", plugin_category))
async def mlist_in(event):
    chat_id = event.chat_id
    topic_id = get_topic_id(event)
    key = (chat_id, topic_id)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    MLIST_DATA[key].add(user_id)
    await update_mlist_message(event.client, chat_id, topic_id)
    await edit_or_reply(event, "تم تسجيل حضورك ✅", 5)

@zedub.zed_cmd(pattern="out$", command=("out", plugin_category))
async def mlist_out(event):
    chat_id = event.chat_id
    topic_id = get_topic_id(event)
    key = (chat_id, topic_id)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    if user_id in MLIST_DATA[key]:
        MLIST_DATA[key].remove(user_id)
        await update_mlist_message(event.client, chat_id, topic_id)
        await edit_or_reply(event, "تم تسجيل خروجك ❌", 5)
    else:
        await edit_or_reply(event, "أنت لست ضمن القائمة!", 5)

@zedub.zedub_bot.on(events.CallbackQuery(pattern=r"mlogin\|(-?\d+)\|(\d+)"))
async def mlogin_handler(event):
    chat_id = int(event.pattern_match.group(1))
    topic_id = int(event.pattern_match.group(2))
    key = (chat_id, topic_id)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    MLIST_DATA[key].add(user_id)
    await update_mlist_message(event.client, chat_id, topic_id)
    await event.answer("تم تسجيل حضورك ✅", alert=False)

@zedub.zedub_bot.on(events.CallbackQuery(pattern=r"mlogout\|(-?\d+)\|(\d+)"))
async def mlogout_handler(event):
    chat_id = int(event.pattern_match.group(1))
    topic_id = int(event.pattern_match.group(2))
    key = (chat_id, topic_id)
    user_id = event.sender_id
    if key not in MLIST_DATA:
        MLIST_DATA[key] = set()
    if user_id in MLIST_DATA[key]:
        MLIST_DATA[key].remove(user_id)
        await update_mlist_message(event.client, chat_id, topic_id)
        await event.answer("تم تسجيل خروجك ❌", alert=False)
    else:
        await event.answer("أنت لست ضمن القائمة!", alert=False)
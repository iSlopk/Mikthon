import re
import datetime
from asyncio import sleep

from telethon import events
from telethon.utils import get_display_name

from . import zedub
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..sql_helper import pmpermit_sql as pmpermit_sql
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..sql_helper.pasmat_sql import (
    add_pasmat,
    get_pasmats,
    remove_all_pasmats,
    remove_pasmat,
)
from ..sql_helper.pmrad_sql import (
    add_pmrad,
    get_pmrads,
    remove_all_pmrads,
    remove_pmrad,
)
from . import BOTLOG, BOTLOG_CHATID

plugin_category = "الخدمات"
LOGS = logging.getLogger(__name__)


ZelzalMeMe_cmd = (
    "𓆩 [𝗦𝗼𝘂𝗿𝗰𝗲 𝗠𝗶𝗸𝘁𝗵𝗼𝗻 ⌁ - اوامـر البصمـات 🎙](t.me/slopk) 𓆪\n\n"
    "**✾╎قائـمه اوامـر ردود البصمات والميديا العامـه🎙:**\n\n"
    "**⎞𝟏⎝** `.بصمه`\n"
    "**•• ⦇الامـر + كلمـة الـرد بالـرد ع بصمـه او ميديـا⦈ لـ اضـافة رد بصمـه عـام**\n\n"
    "**⎞𝟐⎝** `.حذف بصمه`\n"
    "**•• ⦇الامـر + كلمـة البصمـه⦈ لـ حـذف رد بصمـه محـدد**\n\n"
    "**⎞𝟑⎝** `.بصماتي`\n"
    "**•• لـ عـرض قائمـة بـ جميـع بصمـاتك المضـافـة**\n\n"
    "**⎞𝟒⎝** `.حذف بصماتي`\n"
    "**•• لـ حـذف جميـع بصمـاتك المضافـة**\n\n"
    "\n 𓆩 [𝙎𝙊𝙐𝙍𝘾𝞝 𝗠𝗶𝗸𝘁𝗵𝗼𝗻 ⌁](t.me/slopk) 𓆪"
)


# Copyright (C) 2022 Zed-Thon . All Rights Reserved
@zedub.zed_cmd(pattern="البصمات")
async def cmd(zelzallll):
    await edit_or_reply(zelzallll, ZelzalMeMe_cmd)

async def reply_id(event):
    reply_to_id = None
    if event.reply_to_msg_id:
        reply_to_id = event.reply_to_msg_id
    return reply_to_id

@zedub.on(admin_cmd(incoming=True))
async def filter_incoming_handler(event):
    name = event.raw_text
    repl = await reply_id(event)
    filters = get_pasmats(zedub.uid)
    if not filters:
        return
    for trigger in filters:
        if name == trigger.keyword:
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            try:
                await event.client.send_file(
                    event.chat_id,
                    file=file_media,
                    link_preview=link_preview,
                    reply_to=repl,
                )
                await event.delete()
            except BaseException:
                return

@zedub.zed_cmd(pattern="بصمه (.*)")
async def add_new_meme(event):
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ البصمـات 🔊 :**\
                \n**⪼ تم حفـظ البصمـه بـ اسم {keyword}**\n**⪼ لـ قائمـه بصماتك .. بنجـاح ✅**\n**⪼ لـ تصفـح قائمـة بصماتك ارسـل (.بصماتي) 📑**",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "**❈╎يتطلب اضافة البصمات تعيين كـروب السجـل اولاً ..**\n**❈╎لإضافـة كـروب السجـل**\n**❈╎اتبـع الشـرح ⇚** قـم باستعمـال أمر .اضف فار كروب السجل + أيدي المجموعـة يمكنك استخراجـه عبر بوت وعـد.",
            )
            return
    elif msg and msg.text and not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**")
    elif not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**")
    else:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**")
    success = "**⪼تم {} البصمـه بـ اسم {} .. بنجـاح ✅**"
    if add_pasmat(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("اضافة", keyword))
    remove_pasmat(str(zedub.uid), keyword)
    if add_pasmat(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تحديث", keyword))
    await edit_or_reply(event, "**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**")


@zedub.zed_cmd(pattern="بصماتي$")
async def on_meme_list(event):
    OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**"
    filters = get_pasmats(zedub.uid)
    for filt in filters:
        if OUT_STR == "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**":
            OUT_STR = "𓆩 𝗠𝗶𝗸𝘁𝗵𝗼𝗻 ⌁ - قائمـة بصمـاتك المضـافـة 🔊𓆪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
        OUT_STR += "🎙 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="**⧗╎قائمـة بصمـاتك المضـافـة🔊**",
        file_name="filters.text",
    )


@zedub.zed_cmd(pattern="حذف بصمه(?: |$)(.*)")
async def remove_a_meme(event):
    filt = event.pattern_match.group(1)
    if not remove_pasmat(zedub.uid, filt):
        await event.edit("**- ❝ البصمـه ↫** {} **غيـر موجـوده ⁉️**".format(filt))
    else:
        await event.edit("**- ❝ البصمـه ↫** {} **تم حذفهـا بنجاح ☑️**".format(filt))


@zedub.zed_cmd(pattern="حذف بصماتي$")
async def on_all_meme_delete(event):
    filters = get_pasmats(zedub.uid)
    if filters:
        remove_all_pasmats(zedub.uid)
        await edit_or_reply(event, "**⪼ تم حـذف جميـع بصمـاتك .. بنجـاح ✅**")
    else:
        OUT_STR = "**⪼ لا يوجـد لديك بصمـات محفوظـه ❌**\n\n**⪼ ارسـل (** `.بصمه` **) + اسم البصمـه**\n**⪼بالـرد ع بصمـه او مقطـع صـوتـي 🔊**\n**⪼ لإضافتهـا لـ قائمـة بصماتك 🧾**"
        await edit_or_reply(event, OUT_STR)

# ================================================================================================ #
# =========================================ردود الخاص================================================= #
# ================================================================================================ #

@zedub.on(admin_cmd(incoming=True))
async def filter_incoming_handler(event):
    if not event.is_private:
        return
    if event.sender_id == event.client.uid:
        return
    name = event.raw_text
    filters = get_pmrads(zedub.uid)
    if not filters:
        return
    a_user = await event.get_sender()
    chat = await event.get_chat()
    me = await event.client.get_me()
    title = None
    #participants = await event.client.get_participants(chat)
    count = None
    mention = f"[{a_user.first_name}](tg://user?id={a_user.id})"
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    first = a_user.first_name
    last = a_user.last_name
    fullname = f"{first} {last}" if last else first
    username = f"@{a_user.username}" if a_user.username else mention
    userid = a_user.id
    my_first = me.first_name
    my_last = me.last_name
    my_fullname = f"{my_first} {my_last}" if my_last else my_first
    my_username = f"@{me.username}" if me.username else my_mention
    for trigger in filters:
        pattern = f"( |^|[^\\w]){re.escape(trigger.keyword)}( |$|[^\\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            file_media = None
            filter_msg = None
            if trigger.f_mesg_id:
                msg_o = await event.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id)
                )
                file_media = msg_o.media
                filter_msg = msg_o.message
                link_preview = True
            elif trigger.reply:
                filter_msg = trigger.reply
                link_preview = False
            await event.reply(
                filter_msg.format(
                    mention=mention,
                    first=first,
                    last=last,
                    fullname=fullname,
                    username=username,
                    userid=userid,
                    my_first=my_first,
                    my_last=my_last,
                    my_fullname=my_fullname,
                    my_username=my_username,
                    my_mention=my_mention,
                ),
                file=file_media,
                link_preview=link_preview,
            )

@zedub.zed_cmd(pattern="اضف تلقائي (.*)")
async def add_new_meme(event):
    keyword = event.pattern_match.group(1)
    string = event.text.partition(keyword)[2]
    msg = await event.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                f"**⪼ ردودك التلقائيـة خـاص 🗣 :**\
                \n**⪼ تم حفـظ الـرد التلقـائـي بـ اسم {keyword}**\n**⪼ لـ قائمـه ردودك التلقائيـة .. بنجـاح ✅**\n**⪼ لـ تصفـح قائمـة ردودك التلقائيـة ارسـل (.ردود الخاص) 📑**",
            )
            msg_o = await event.client.forward_messages(
                entity=BOTLOG_CHATID,
                messages=msg,
                from_peer=event.chat_id,
                silent=True,
            )
            msg_id = msg_o.id
        else:
            await edit_or_reply(
                event,
                "**❈╎يتطلب اضافة الـردود التلقـائـيـة تعيين كـروب السجـل اولاً ..**\n**❈╎لإضافـة كـروب السجـل**\n**❈╎اتبـع الشـرح ⇚** قـم باستعمـال أمر .اضف فار كروب السجل + أيدي المجموعـة يمكنك استخراجـه عبر بوت وعـد.",
            )
            return
    elif msg and msg.text and not string:
        string = msg.text
    elif not string:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**")
    else:
        return await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**")
    success = "**⪼تم {} الـرد التلقـائـي بـ اسم {} .. بنجـاح ✅**"
    if add_pmrad(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("اضافة", keyword))
    remove_pmrad(str(zedub.uid), keyword)
    if add_pmrad(str(zedub.uid), keyword, string, msg_id) is True:
        return await edit_or_reply(event, success.format("تحديث", keyword))
    await edit_or_reply(event, "**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**")


@zedub.zed_cmd(pattern="ردود الخاص$")
async def on_meme_list(event):
    OUT_STR = "**⪼ لا يوجـد لديك ردود تلقائيـة لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**"
    filters = get_pmrads(zedub.uid)
    for filt in filters:
        if OUT_STR == "**⪼ لا يوجـد لديك ردود تلقائيـة لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**":
            OUT_STR = "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗠𝗶𝗸𝘁𝗵𝗼𝗻 ⌁ - ردودك التلقـائيـة خـاص 🗣𓆪\n⋆┄─┄─┄─┄┄─┄─┄─┄─┄┄⋆\n"
        OUT_STR += "🎙 `{}`\n".format(filt.keyword)
    await edit_or_reply(
        event,
        OUT_STR,
        caption="**⧗╎قائمـة ردودك التلقـائـيـة خـاص المضـافـة🗣**",
        file_name="filters.text",
    )


@zedub.zed_cmd(pattern="حذف تلقائي(?: |$)(.*)")
async def remove_a_meme(event):
    filt = event.pattern_match.group(1)
    if not remove_pmrad(zedub.uid, filt):
        await event.edit("**- ❝ الـرد التلقـائـي ↫** {} **غيـر موجـود ⁉️**".format(filt))
    else:
        await event.edit("**- ❝ الـرد التلقـائـي ↫** {} **تم حذفه .. بنجاح ☑️**".format(filt))


@zedub.zed_cmd(pattern="حذف ردود الخاص$")
async def on_all_meme_delete(event):
    filters = get_pmrads(zedub.uid)
    if filters:
        remove_all_pmrads(zedub.uid)
        await edit_or_reply(event, "**⪼ تم حـذف جميـع ردودك التلقـائـيـة خـاص .. بنجـاح ✅**")
    else:
        OUT_STR = "**⪼ لا يوجـد لديك ردود تلقائيـة لـ الخـاص ❌**\n\n**⪼ ارسـل (** `.اضف تلقائي` **) + كلمـة الـرد**\n**⪼بالـرد ع جملـة او ميديـا 🗣**\n**⪼ لإضافتهـا لـ قائمـة ردودك التلقائيـة 🧾**"
        await edit_or_reply(event, OUT_STR)
        

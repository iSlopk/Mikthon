import asyncio 
import random
import re
import requests
import time
import psutil
from datetime import datetime
from platform import python_version
#BiLaL
from telethon import version, events
from telethon.tl import types, functions
from telethon.tl.types import UserStatusOnline as onn
from telethon.utils import get_display_name
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)

from . import StartTime, zedub, zedversion
from ..Config import Config
from ..helpers.functions import zedalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..core.logger import logging
from ..helpers.utils import _format
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..core.managers import edit_delete, edit_or_reply
from ..core.logger import logging
from . import BOTLOG, BOTLOG_CHATID, mention



@zedub.zed_cmd(pattern="(تفعيل البصمه الذاتيه|تفعيل البصمه الذاتية|تفعيل البصمة الذاتيه|تفعيل البصمة الذاتية)")
async def start_datea(event):
    global vocself

    if vocself:
        return await edit_or_reply(event, "**⎉╎حفظ البصمة الذاتية التلقائي 🎙**\n**⎉╎مفعلـه .. مسبقًـا ✅**")
    vocself = True
    await edit_or_reply(event, "**⎉╎تم تفعيل حفظ البصمة الذاتية 🎙**\n**⎉╎تلقائيًّـا .. بنجاح ✅**")

@zedub.zed_cmd(pattern="(ايقاف البصمه الذاتيه|ايقاف البصمه الذاتية|ايقاف البصمة الذاتيه|ايقاف البصمة الذاتية)")
async def stop_datea(event):
    global vocself
    
    if vocself:
        vocself = False
        return await edit_or_reply(event, "**⎉╎تم تعطيل حفظ البصمة الذاتية 🎙**\n**⎉╎الان صارت مو شغالة .. ✅**")
    await edit_or_reply(event, "**⎉╎حفظ البصمة الذاتية التلقائي 🎙**\n**⎉╎معطلـه .. مسبقـاً ✅**")

@zedub.on(events.NewMessage(func=lambda e: e.is_private and (e.audio or e.voice) and e.media_unread))
async def sddm(event):
    global vocself
  
    if vocself:
        sender = await event.get_sender()
        username = f"@{sender.username}" if sender.username else "لا يوجد"
        chat = await event.get_chat()
        voc = await event.download_media()
       
        await zedub.send_file("me", voc, caption=f"[ᯓ 𝙏𝙀𝙋𝙏𝙃𝙊𝙉 ⌁ - حفـظ البصمـة الذاتيــة 🎙\n⋆─┄─┄─┄─┄─┄─┄─⋆\n⌔ مࢪحبـًا .. عـزيـزي 🫂\n⌔ تـم حفظ البصمة الذاتية .. تلقائيًّـا ☑️ ❝\n⌔ معلومـات المـرسـل :-\n• الاسم : {_format.mentionuser(sender.first_name , sender.id)}\n• اليوزر : {username}\n• الايدي : {sender.id}")

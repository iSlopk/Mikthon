# telegraph utils for ZThon
import os
import random
import string
from datetime import datetime

from PIL import Image
from telegraph import Telegraph, exceptions, upload_file
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.utils import get_display_name
from urlextract import URLExtract

from ..Config import Config
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import delete_conv
from . import BOTLOG, BOTLOG_CHATID, zedub, reply_id

LOGS = logging.getLogger(__name__)

plugin_category = "الخدمات"

extractor = URLExtract()
telegraph = Telegraph()
r = telegraph.create_account(short_name=Config.TELEGRAPH_SHORT_NAME)
auth_url = r["auth_url"]


@zedub.zed_cmd(
    pattern="ctg(?: |$)([\s\S]*)",
    command=("ctg", plugin_category),
    info={
        "header": "Reply to link To get link preview using telegrah.s.",
        "usage": "{tr}ctg <reply/text>",
    },
)
async def ctg(event):
    "To get link preview"
    input_str = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    reply_to_id = await reply_id(event)
    if not input_str and reply:
        input_str = reply.text
    if not input_str:
        return await edit_delete(event, "**ಠ∀ಠ Give me link to search..**", 20)
    urls = extractor.find_urls(input_str)
    if not urls:
        return await edit_delete(event, "**There no link to search in the text..**", 20)
    chat = "@chotamreaderbot"
    zedevent = await edit_or_reply(event, "```Processing...```")
    async with event.client.conversation(chat) as conv:
        try:
            msg_flag = await conv.send_message(urls[0])
        except YouBlockedUserError:
            await edit_or_reply(
                zedevent, "**Error:** Trying to unblock & retry, wait a sec..."
            )
            await zedub(unblock("chotamreaderbot"))
            msg_flag = await conv.send_message(urls[0])
        response = await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        if response.text.startswith(""):
            await edit_or_reply(zedevent, "Am I Dumb Or Am I Dumb?")
        else:
            await zedevent.delete()
            await event.client.send_message(
                event.chat_id, response, reply_to=reply_to_id, link_preview=True
            )
        await delete_conv(event, chat, msg_flag)

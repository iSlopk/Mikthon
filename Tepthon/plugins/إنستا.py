#الجوكر
from datetime import datetime
from telethon.errors.rpcerrorlist import YouBlockedUserError
from Tepthon import zedub

# تعريف فئة أو اسم للبلاجن
plugin_category = "Instagram"

@zedub.zed_cmd(
    pattern="انستا (.*)",
    command=("انستا", plugin_category),
    info={
        "header": "To download instagram video/photo",
        "description": "Note downloads only public profile photos/videos.",
        "examples": [
            "{tr}insta <link>",
        ],
    },
)
async def kakashi(event):
    "For downloading instagram media"
    chat = "@SaveOFFbot"
    link = event.pattern_match.group(1)

    # تحقق مما إذا كان الرابط صحيحًا
    if "www.instagram.com" not in link:
        return await edit_or_reply(event, "**⎉╎ ضـع رابط الانستجرام بعــد الأمر أولًا**")

    start = datetime.now()
    catevent = await edit_or_reply(event, "**⎉╎ جـــاري التحميــــل انتظـــر لُطفًــــا 🔍..**")

    async with event.client.conversation(chat) as conv:
        try:
            msg_start = await conv.send_message("/start")
            response = await conv.get_response()
            msg = await conv.send_message(link)
            video = await conv.get_response()
            details = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
        except YouBlockedUserError:
            await catevent.edit("**⎉╎ ألـــغِ حظـر البوت ثم أعــد المـحاولة @SaveOFFbot**")
            return
        except Exception as e:
            await catevent.edit(f"**⎉╎ خطــــــــأ ❌: {str(e)}**")
            return

    await catevent.delete()
    
    # إرسال الملف
    cat = await event.client.send_file(event.chat_id, video)

    end = datetime.now()
    ms = (end - start).seconds

    await cat.edit(f"**⎉╎ تم التنزيــل ♥️ : @Tepthon**", parse_mode="html")

    # حذف الرسائل المستخدمة في المحادثة
    await event.client.delete_messages(
        conv.chat_id, 
        [msg_start.id, response.id, msg.id, video.id, details.id]
    )

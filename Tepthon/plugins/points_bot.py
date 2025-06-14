import asyncio
from telethon import events
from telethon.errors.rpcerrorlist import MessageAuthorRequiredError

from . import zedub
from ..Config import Config
from ..core.managers import edit_or_reply

plugin_category = "بوت النقاط"
cmhd = Config.COMMAND_HAND_LER

POINTS_DATA = {}  # {chat_id: {user_id: points}}


async def safe_edit_or_reply(event, text, **kwargs):
    """
    دالة للرد أو التعديل بأمان (تعالج خطأ MessageAuthorRequiredError تلقائياً).
    """
    try:
        await edit_or_reply(event, text, **kwargs)
    except MessageAuthorRequiredError:
        await event.reply(text, **kwargs)


async def get_user_id(event, args):
    """
    جلب ID المستخدم حسب الرد أو المنشن أو الإيدي.
    """
    if event.is_reply:
        reply = await event.get_reply_message()
        return reply.sender_id
    if args:
        if args[0].startswith("@"):
            try:
                entity = await event.client.get_entity(args[0])
                return entity.id
            except Exception:
                pass
        try:
            return int(args[0])
        except Exception:
            pass
    return None


@zedub.bot_cmd(pattern=fr"^(?:{cmhd}addp|{cmhd}disp)(?:\s+(.+))?$")
async def points_manage(event):
    """إضافة أو خصم نقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    perms = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not perms.is_admin:
        return await safe_edit_or_reply(event, "❗️الأمر متاح للمشرفين فقط.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    cmd = points = 1

    # استخراج النقاط إذا وُجدت
    if len(args) > 1:
        try:
            points = abs(int(args[1]))
        except Exception:
            pass

    # جلب user_id
    uid = await get_user_id(event, args)
    if uid is None:
        return await safe_edit_or_reply(event, "يرجى تحديد المستخدم بالرد أو المنشن أو الإيدي.")

    # ضبط الداتا
    chat_points = POINTS_DATA.setdefault(event.chat_id, {})
    old = chat_points.get(uid, 0)
    if cmd == "/addp":
        chat_points[uid] = old + points
        await safe_edit_or_reply(event, f"✅ تم إضافة {points} نقطة.\nرصيد المستخدم الآن: {chat_points[uid]}")
    else:
        chat_points[uid] = max(old - points, 0)
        await safe_edit_or_reply(event, f"❌ تم خصم {points} نقطة.\nرصيد المستخدم الآن: {chat_points[uid]}")


@zedub.bot_cmd(pattern=fr"^(?:{cmhd}ps|{cmhd}points)(?:\s+(.+))?$")
async def show_points(event):
    """عرض النقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    uid = await get_user_id(event, args)
    chat_points = POINTS_DATA.get(event.chat_id, {})
    if uid is None:
        # عرض الجميع بدون حد
        ranking = sorted(chat_points.items(), key=lambda x: x[1], reverse=True)
        if not ranking:
            return await safe_edit_or_reply(event, "لا يوجد نقاط مسجلة في هذه المجموعة.")
        text = "**ترتيب النقاط في المجموعة:**\n"
        for i, (uid, pts) in enumerate(ranking, 1):
            try:
                user = await event.client.get_entity(uid)
                name = user.first_name
            except Exception:
                name = str(uid)
            text += f"{i}. [{name}](tg://user?id={uid}) - {pts}\n"
        await safe_edit_or_reply(event, text)
    else:
        pts = chat_points.get(uid, 0)
        try:
            user = await event.client.get_entity(uid)
            name = user.first_name
        except Exception:
            name = str(uid)
        await safe_edit_or_reply(event, f"رصيد [{name}](tg://user?id={uid}): {pts} نقطة.")


@zedub.bot_cmd(pattern=fr"^{ if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    perms = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not perms.is_admin:
        return await safe_edit_or_reply(event, "❗️الأمر متاح للم in POINTS_DATA and POINTS_DATA[event.chat_id]:
        for uid in POINTS_DATA[event.chat_id]:
            POINTS_DATA[event.chat_id][uid] = 0
        await safe_edit_or_reply(event, "✅ تم إعادة تعيين جميع النقاط إلى الصفر.")
    else:
        await safe_edit_or_reply(event, "لا يوجد نقاط مسجلة حالياً.")
import asyncio
from telethon import events

from . import zedub

plugin_category = "بوت النقاط"

POINTS_DATA = {}  # {chat_id: {user_id: points}}

async def get_user_id(event, args):
    """جلب ID المستخدم حسب الرد أو المنشن أو الإيدي"""
    if event.is_reply:
        reply = await event.get_reply_message()
        return reply.sender_id
    if args:
        if args[0].startswith return int(args[0])
        except Exception:
            pass
    return None

@zedub.bot_cmd(pattern="^(?:/addp|/disp)(?:\s+(.+))?$")
async def points_manage(event):
    """إضافة أو خصم نقاط"""
    if not event.is_group:
        return await event.reply("❗️يعمل فقط في المجموعات.")
    if not await event.client.get_permissions(event.chat_id, event.sender_id).is_admin:
        return await event.reply("❗️الأمر متاح للمشرفين فقط.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    cmd = event.text.split()[0].lower()
    points = 1

    # استخراج النقاط إذا وُجدت
    if len(args) > 1:
        try:
            points = abs(int(args[1]))
        except Exception:
            pass

    # جلب user_id
    uid = await get_user_id(event, args)
    if uid is None:
        return await event.reply("يرجى تحديد المستخدم بالرد أو المنشن أو الإيدي.")

    # ضبط الداتا
    chat_points = POINTS_DATA.setdefault(event.chat_id, {})
    old = chat_points.get(uid, 0)
    if cmd == "/addp":
        chat_points[uid] = old + points
        await event.reply(f"✅ تم إضافة {points} نقطة.\nرصيد المستخدم الآن: {chat_points[uid]}")
    else:
        chat_points[uid] = max(old - points, 0)
        await event.reply(f"❌ تم خصم {points} نقطة.\nرصيد المستخدم الآن: {chat_points[uid]}")

@zedub.bot_cmd(pattern="^(?:/ps|/points)(?:\s+(.+))?$")
async def show_points(event):
    """عرض النقاط"""
    if not event.is_group:
        return await event.reply("❗️يعمل فقط في المجموعات.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    uid = await get_user_id(event, args)
    chat_points = POINTS_DATA.get(event.chat_id, {})
    if uid is None:
        # عرض الجميع بدون حد
        ranking = sorted(chat_points.items(), key=lambda x: x[1], reverse=True)
        if not ranking:
            return await event.reply("لا يوجد نقاط مسجلة في هذه المجموعة.")
        text = "**ترتيب النقاط في المجموعة:**\n"
        for i, (uid, pts) in enumerate(ranking, 1):
            try:
                user = await event.client.get_entity(uid)
                name = user.first_name
            except Exception:
                name = str(uid)
            text += f"{i}. [{name}](tg://user?id={uid}) - {pts}\n"
        await event.reply(text)
    else:
        pts = chat_points.get(uid, 0)
        user = await event.client.get_entity(uid)
        await event.reply(f"رصيد [{user.first_name}](tg://user?id={uid}): {pts} نقطة.")

@zedub.bot_cmd(pattern="^/resetp$")
async def reset_points(event):
    """إعادة جميع النقاط إلى صفر"""
    if not event.is_group:
        return await event.reply("❗️يعمل فقط في المجموعات.")
    if not await event.client.get_permissions(event.chat_id, event.sender_id).is_admin:
        return await event.reply("❗️الأمر متاح للمشرفين فقط.")
    if event.chat_id in POINTS_DATA:
        for uid in POINTS_DATA[event.chat_id]:
            POINTS_DATA[event.chat_id][uid] = 0
        await event.reply("✅ تم إعادة تعيين النقاط.")
    else:
        await event.reply("لا يوجد نقاط مسجلة حالياً.")

# لا ملف ولا داتا دائمة (تخزين مؤقت بالذاكرة فقط)
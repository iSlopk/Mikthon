import asyncio
import sqlite3
from telethon import events
from telethon.errors.rpcerrorlist import MessageAuthorRequiredError

from . import zedub
from ..Config import Config
from ..core.managers import edit_or_reply

plugin_category = "بوت النقاط"
cmhd = Config.COMMAND_HAND_LER

DB_PATH = "points_db.sqlite"

def get_db():
    return sqlite3.connect(DB_PATH)

def create_table():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS points (
            chat_id INTEGER,
            user_id INTEGER,
            points INTEGER,
            PRIMARY KEY (chat_id, user_id)
        )""")
create_table()

def get_points(chat_id, user_id):
    with get_db() as db:
        cur = db.execute(
            "SELECT points FROM points WHERE chat_id=? AND user_id=?",
            (chat_id, user_id)
        )
        row = cur.fetchone()
        return row[0] if row else 0

def set_points(chat_id, user_id, points):
    with get_db() as db:
        db.execute(
            "INSERT OR REPLACE INTO points (chat_id, user_id, points) VALUES (?, ?, ?)",
            (chat_id, user_id, points)
        )

def get_all_points(chat_id):
    with get_db() as db:
        cur = db.execute(
            "SELECT user_id, points FROM points WHERE chat_id=? ORDER BY points DESC",
            (chat_id,)
        )
        return cur.fetchall()

def reset_all_points(chat_id):
    with get_db() as db:
        db.execute(
            "UPDATE points SET points=0 WHERE chat_id=?",
            (chat_id,)
        )

async def safe_edit_or_reply(event, text, **kwargs):
    """دالة للرد أو التعديل بأمان (تعالج خطأ MessageAuthorRequiredError تلقائياً)."""
    try:
        await edit_or_reply(event, text, **kwargs)
    except MessageAuthorRequiredError:
        await event.reply(text, **kwargs)

async def get_user_id(event, args):
    """جلب ID المستخدم حسب الرد أو المنشن أو الإيدي."""
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

@zedub.bot_cmd(pattern=fr"^(?:{cmhd}اضف|{cmhd}خصم)(?:\s+(.+))?$")
async def points_manage(event):
    """إضافة أو خصم نقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    perms = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not perms.is_admin:
        return await safe_edit_or_reply(event, "❗️الأمر متاح للمشرفين فقط.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    cmd = event.text.split()[0].lower().replace(cmhd, "#")
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
        return await safe_edit_or_reply(event, "يرجى تحديد المستخدم بالرد أو المنشن أو الإيدي.")

    # عمليات النقاط عبر قاعدة البيانات
    old = get_points(event.chat_id, uid)
    if cmd == "#اضف":
        new_points = old + points
        set_points(event.chat_id, uid, new_points)
        await safe_edit_or_reply(event, f"✅ تم إضافة {points} نقطة.\nنقاط [{name}](tg://user?id={user_id}) الآن: {new_points}")
    else:
        new_points = max(old - points, 0)
        set_points(event.chat_id, uid, new_points)
        await safe_edit_or_reply(event, f"❌ تم خصم {points} نقطة.\nنقاط [{name}](tg://user?id={user_id}) الآن: {new_points}")

@zedub.bot_cmd(pattern=fr"^(?:{cmhd}ps|{cmhd}points|{cmhd}النقاط)(?:\s+(.+))?$")
async def show_points(event):
    """عرض النقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    uid = await get_user_id(event, args)
    ranking = get_all_points(event.chat_id)
    if uid is None:
        # عرض الجميع بدون حد
        if not ranking:
            return await safe_edit_or_reply(event, "لا يوجد نقاط مسجلة في هذه المجموعة.")
        text = "**ترتيب النقاط في المجموعة:**\n"
        for i, (user_id, pts) in enumerate(ranking, 1):
            try:
                user = await event.client.get_entity(user_id)
                name = user.first_name
            except Exception:
                name = str(user_id)
            text += f"{i}. [{name}](tg://user?id={user_id}) » {pts}\n"
        await safe_edit_or_reply(event, text)
    else:
        pts = get_points(event.chat_id, uid)
        try:
            user = await event.client.get_entity(uid)
            name = user.first_name
        except Exception:
            name = str(uid)
        await safe_edit_or_reply(event, f"نقاط [{name}](tg://user?id={uid}): {pts} نقطة.")

@zedub.bot_cmd(pattern=fr"^{cmhd}تصفير$")
async def reset_points(event):
    """إعادة جميع النقاط إلى صفر"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    perms = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not perms.is_admin:
        return await safe_edit_or_reply(event, "❗️الأمر متاح للمشرفين فقط.")
    ranking = get_all_points(event.chat_id)
    if ranking:
        reset_all_points(event.chat_id)
        await safe_edit_or_reply(event, "✅ تم تصفير جميع النقاط.")
    else:
        await safe_edit_or_reply(event, "لا يوجد نقاط مسجلة حالياً.")
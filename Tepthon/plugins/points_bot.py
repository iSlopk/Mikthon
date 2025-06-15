import asyncio
import sqlite3
from telethon import events
from telethon.errors.rpcerrorlist import MessageAuthorRequiredError

from . import zedub
from ..Config import Config
from ..core.managers import edit_or_reply

plugin_category = "بوت النقاط"
TEAM_MODE_STATUS = {}
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
            "SELECT user_id, points FROM points WHERE chat_id=? AND points > 0 ORDER BY points DESC",
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

@zedub.bot_cmd(pattern=fr"^(?:{cmhd}p|{cmhd}delp)(?:\s+(.+))?$")
async def points_manage(event):
    """إضافة أو خصم نقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    perms = await event.client.get_permissions(event.chat_id, event.sender_id)
    if not perms.is_admin:
        return await safe_edit_or_reply(event, "❗️الأمر متاح للمشرفين فقط.")
    args = event.pattern_match.group(1) 
    args = args.split() if args else []
    cmd = event.text.split()[0].lower().replace(cmhd, "/")
    
    points = 1

    if len(args) > 1:
        try:
            points = abs(int(args[1]))
        except Exception:
            pass
    
    elif event.is_reply and args:
        try:
            points = abs(int(args[0]))
        except Exception:
            pass

    # استدعاء دالة handle_event دائماً
    return await handle_event(event, args, cmd, points)

async def handle_event(event, args, cmd, points):
    """تنفيذ إضافة أو خصم النقاط"""
    # الحصول على ID المستخدم المستهدف
    uid = await get_user_id(event, args)
    if uid is None:
        return await safe_edit_or_reply(event, "❗️يرجى تحديد المستخدم بالرد أو المنشن أو الإيدي.")

    # محاولة الحصول على معلومات المستخدم
    try:
        user = await event.client.get_entity(uid)
        name = user.first_name + (" " + user.last_name if user.last_name else "")
    except Exception:
        name = str(uid)
    user_id = uid

    # الحصول على عدد النقاط الحالي
    old = get_points(event.chat_id, uid)

    # إذا كان الأمر هو /p يتم إضافة النقاط
    if cmd == "/p":
        new_points = old + points
        set_points(event.chat_id, uid, new_points)
        return await safe_edit_or_reply(
            event,
            f"➕ تم إضافة {points} نقطة.\n👤 المستخدم : [{name}](tg://user?id={user_id})\n🔢 عدد نقاطه : [{new_points}]"
        )
    # إذا كان الأمر هو /delp يتم خصم النقاط
    else:
        new_points = max(old - points, 0)  # التأكد من أن النقاط لا تصبح أقل من صفر
        set_points(event.chat_id, uid, new_points)
        return await safe_edit_or_reply(
            event,
            f"➖ تم خصم {points} نقطة.\n👤 المستخدم : [{name}](tg://user?id={user_id})\n🔢 عدد نقاطه : [{new_points}]")

@zedub.bot_cmd(pattern=fr"^(?:{cmhd}ps|{cmhd}points)(?:\s+(.+))?$")
async def show_points(event):
    """عرض النقاط"""
    if not event.is_group:
        return await safe_edit_or_reply(event, "❗️يعمل فقط في المجموعات.")
    args = event.pattern_match.group(1)
    args = args.split() if args else []
    uid = await get_user_id(event, args)
    ranking = get_all_points(event.chat_id)
    if uid is None:
        
        if not ranking:
            return await safe_edit_or_reply(event, "🍃 لا يوجد نقاط مسجلة في الشات.")
        text = "**📊 | نشرة النقاط في المجموعة **:\n\n"
        for i, (user_id, pts) in enumerate(ranking, 1):
            try:
                user = await event.client.get_entity(user_id)
                
                name = user.first_name + (" " + user.last_name if user.last_name else "")
                
            except Exception:
                name = str(user_id)
            text += f"{i}- [{name}](tg://user?id={user_id}) [{pts}]\n"
        return await safe_edit_or_reply(event, text)
    else:
        pts = get_points(event.chat_id, uid)
        try:
            user = await event.client.get_entity(uid)
            
            name = user.first_name + (" " + user.last_name if user.last_name else "")
            
        except Exception:
            name = str(uid)
        return await safe_edit_or_reply(event, f"👤 المستخدم : [{name}](tg://user?id={uid})\n🔢 عدد النقاط : [{pts}].")

@zedub.bot_cmd(pattern=fr"^{cmhd}rstp$")
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
        return await safe_edit_or_reply(event, "✅ تم ترسيت نقاط الشات.")
    else:
        return await safe_edit_or_reply(event, "🍃 لا يوجد نقاط مسجلة حالياً.")
        
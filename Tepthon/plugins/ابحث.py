import random
import glob
import os
from yt_dlp import YoutubeDL
from telethon import events
from Tepthon import zedub
from ..Config import Config

plugin_category = "البوت"

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file

@zedub.on(events.NewMessage(pattern='.بحث3 (.*)'))
async def get_song(event):
    song_name = event.pattern_match.group(1)
    await event.reply(f"🕵️‍♂️ جارٍ البحث عن الأغنية: **{song_name}**...")

    # إعداد خيارات yt-dlp
    ydl_opts = {
        "format": "bestaudio/best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "%(title)s.%(ext)s",
        "quiet": True,
        "cookiefile": get_cookies_file(),
    }

    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            if not info['entries']:
                await event.reply("❌ لم يتم العثور على أي نتائج.")
                return

            # أرسال قائمة الأغاني المتاحة
            response_message = "🎶 تم العثور على الأغاني التالية:\n"
            for index, entry in enumerate(info['entries'][:5], start=1):  # عرض أول 5 نتائج
                response_message += f"{index}. {entry['title']}\n"

            response_message += "\n📝 اختر رقم الأغنية لتحميلها."

            await event.reply(response_message)

            # انتظار رد المستخدم لاختيار رقم الأغنية
            async def wait_for_reply():
                reply = await zedub.wait_for_new_message(event.chat_id)
                return reply.message

            user_selection = await wait_for_reply()
            selected_index = int(user_selection) - 1

            if 0 <= selected_index < len(info['entries']):
                selected_entry = info['entries'][selected_index]
                title = selected_entry['title']
                await event.reply(f"📥 جاري تحميل: **{title}**...")

                # تحميل الأغنية
                ydl.download([selected_entry['webpage_url']])
                filename = f"{title}.mp3"

                # إرسال الملف إلى تيليجرام
                await zedub.send_file(event.chat_id, filename)

                # حذف الملف بعد الإرسال
                os.remove(filename)
            else:
                await event.reply("⚠️ رقم غير صالح.")
        except Exception as e:
            await event.reply(f"🚫 حدث خطأ أثناء البحث عن الأغنية: {e}")

"""
❃ `{i}تحميل صوتي` <(رابط يوتيوب/او اي رابط)>
   لـ تحميل الملف بشكل ملف صوتي في التليجرام، يمكنك وضع رابط اي منصة


❃ `{i}تحميل فيد` <(رابط يوتيوب/او اي رابط)>
   لـ تحميل الملف بشكل فيديو في التليجرام، يمكنك وضع رابط اي منصة


❃ `{i}صوتي` <(عنوان)>
   لـ تحميل الملف بشكل ملف صوتي في التليجرام من خلال العنوان فقط بدون رابط

"""

import random
import glob
import asyncio
import yt_dlp
import os
from ..core.managers import edit_or_reply
from yt_dlp import YoutubeDL
from Tepthon import zedub
from ..Config import Config

def get_cookies_file():
    folder_path = f"{os.getcwd()}/rcookies"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt_file = random.choice(txt_files)
    return cookie_txt_file
    
ytd = {
    "prefer_ffmpeg": True,
    "addmetadata": True,
    "geo-bypass": True,
    "nocheckcertificate": True,
    "postprocessors": [{"key": "FFmpegMetadata"}],
    "cookiefile": "cozc.txt"  # تأكد من تحديد المسار الصحيح لملف الكوكيز
}

@zedub.zed_cmd(pattern="تحميل صوتي (.*)")
async def down_voic(event):
    zed = await edit_or_reply("⌔ جار التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "bestaudio"
    ytd["outtmpl"] = "%(id)s.m4a"
    ytd["postprocessors"].insert(
        0,
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
    )
    url = event.pattern_match.group(1)
    if not url:
        return await zed.edit_or_reply("⌔ يجب عليك وضع رابط للتحميل الصوتي")
    try:
        await is_url_work(url)
    except BaseException:
        return await zed.edit_or_reply("⌔ يرجى وضع الرابط بشكل صحيح")
    await download_yt(zed, url, ytd)

@zedub.zed_cmd(pattern="تحميل فيد (.*)")
async def vidown(event):
    zed = await edit_or_reply("⌔ جـاري التحميل يرجى الانتظار قليلًا")
    ytd["format"] = "best"
    ytd["outtmpl"] = "%(id)s.mp4"
    ytd["postprocessors"].insert(
        0, {"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}
    )
    url = event.pattern_match.group(1)
    print(url)
    if not url:
        return await zed.edit_or_reply("⌔ يجب عليك وضع رابط لتحميل الفيد")
    try:
        await is_url_work(url)
    except BaseException:
        return await zed.edit_or_reply("⌔ يرجى وضع الرابط بشكل صحيح")
    await download_yt(zed, url, ytd)

@zedub.zed_cmd(pattern="صوتي( (.*)|$)")
async def sotea(event):
    zed = await edit_or_reply("⌔ جار التحميل يرجى الانتظـار قليلًا")
    ytd["format"] = "bestaudio"
    ytd["outtmpl"] = "%(id)s.m4a"
    ytd["postprocessors"].insert(
        0,
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
            "preferredquality": "128",
        },
    )
    query = event.pattern_match.group(2) if event.pattern_match.group(1) else None
    if not query:
        return await zed.edit_or_reply("⌔ يجب عليك تحديد ما تريد تحميله اكتب عنوان مع الأمر")
    url = get_yt_link(query, ytd)
    if not url:
        return await zed.edit("⌔ لم يتم العثور على الفيديو اكتب عنوان مفصل بشكل صحيح")
    await zed.edit_or_reply("⌔ جاري تحميل الملف الصوتي انتظـر قليلًا")
    await download_yt(zed, url, ytd)

import random
from re import compile as c
from neokimberly import kimberly
from pyrogram import filters
import yt_dlp
import os


instagram="(https?:\\/\\/([a-zA-Z0-9-]+\\.)?instagram\\.com\\/[^?]+)"
tiktok="(https?:\\/\\/([a-zA-Z0-9-]+\\.)?tiktok\\.com\\/[^\\/]+)"
twitter="(https?:\\/\\/([a-zA-Z0-9-]+\\.)*(twitter|x)\\.com\\/(.*?)\\/[^\\s]+)" 
regex_urls = [c(instagram), c(tiktok), c(twitter)]

@kimberly.on_message(filters.regex(f"{instagram}|{tiktok}|{twitter}"))
@kimberly.on_edited_message(filters.regex(f"{instagram}|{tiktok}|{twitter}"))
async def fix_embed(_, message):
    for website in regex_urls:
        url = website.search(message.text)
        if url is not None:
            url = url.group(1)
            if "instagram" in url:
                # Cookies path
                dirname = os.path.dirname(__file__)
                cookiefile = os.path.join(dirname, "../config/cookies/ig.txt")

                randname = random.getrandbits(64)
                ydl_opts = {
                    "format": "bestvideo[ext=mp4]+bestaudio/best", # This will select the specific resolution typed here
                    "outtmpl": f"/tmp/{randname}.mp4",
                    "restrictfilenames": True,
                    "nooverwrites": True,
                    "cookiefile": cookiefile
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    try:
                        vid_msg = await message.reply_text("Downloading video...")
                        error_code = ydl.download(url)
                        await vid_msg.edit("Uploading...")
                        await message.reply_video(f"/tmp/{randname}.mp4", quote=True, disable_notification=True, supports_streaming=True)
                        await vid_msg.delete()
                        os.remove(f"/tmp/{randname}.mp4")

                    except Exception as e:
                        await message.reply_text("Unable to download the video.\n```", e, "```")
            else:
                await message.reply_text(url.replace("tiktok", "vxtiktok").replace("twitter.com", "fxtwitter.com").replace("x.com", "fxtwitter.com"))


# TODO)) implement callback button to force download the embed (video) with yt-dlp

from re import compile as c
from neokimberly import kimberly
from pyrogram import filters


instagram="(https?:\\/\\/([a-zA-Z0-9-]+\\.)?instagram\\.com\\/[^?]+)"
tiktok="(https?:\\/\\/([a-zA-Z0-9-]+\\.)?tiktok\\.com\\/[^\\/]+)"
twitter="(https?:\\/\\/([a-zA-Z0-9-]+\\.)*(twitter|x)\\.com\\/(.*?)\\/[^\\s]+)" 
regex_urls = [c(instagram), c(tiktok), c(twitter)]


@kimberly.on_message(filters.regex(f"{instagram}|{tiktok}|{twitter}"))
@kimberly.on_edited_message(filters.regex(f"{instagram}|{tiktok}|{twitter}"))
async def fix_embed(_, message):
    for website in regex_urls:
        url = website.search(message.text.lower())
        if url is not None:
            await message.reply_text(url.group(1).replace("instagram", "ddinstagram").replace("tiktok", "vxtiktok").replace("twitter", "i.fxtwitter"))


# TODO)) implement callback button to force download the embed (video) with yt-dlp

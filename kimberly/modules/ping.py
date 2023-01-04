from datetime import datetime
from pyrogram import filters
from neokimberly import kimberly

@kimberly.on_message(filters.regex("^/ping$"))
async def ping_me(client, message):
    start = datetime.now()
    reply = await message.reply_text("`Pong!`")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await reply.edit_text(f"**Pong!**\n`{ms} ms`")

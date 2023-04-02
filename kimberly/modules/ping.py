from time import perf_counter 
from pyrogram import filters
from neokimberly import kimberly

@kimberly.on_message(filters.command("ping"))
async def ping_me(client, message):
    start = perf_counter()
    reply = await message.reply_text("`Pong!`")
    end = perf_counter()
    ms = (end - start) * 1000
    await reply.edit_text(f"**Pong!**\n`{ms:.3f} ms`")

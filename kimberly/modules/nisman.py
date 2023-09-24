from datetime import datetime
from pyrogram import filters
from config.login import timezone,nisman_time
from db.timezones import *
from neokimberly import kimberly


# Set group's timezone when the bot is added to the group
@kimberly.on_message(filters.group & filters.new_chat_members, group=-1)
async def assign_default_group_timezone(_, message):
    if len(message.new_chat_members) > 1:
        return
    user = message.new_chat_members[0]
    if (user.is_self):
        chat_id = message.chat.id
        if (not await group_has_tz(chat_id)):
            # We already check if the time is correct when starting the bot
            time = datetime.strptime(nisman_time, "%H:%M:%S").time()
            await set_group_timezone(chat_id, timezone)
            await set_group_nisman_time(chat_id, time)
        else:
            print("Group already has timezone")

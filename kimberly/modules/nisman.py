from pyrogram import filters
from db.timezones import set_group_timezone
from neokimberly import kimberly
from config.login import timezone


# Set group's timezone when the bot is added to the group
@kimberly.on_message(filters.group & filters.new_chat_members, group=-1)
async def assign_default_group_timezone(_, message):
    if len(message.new_chat_members) > 1:
        return
    user = message.new_chat_members[0]
    if (user.is_self):
        await set_group_timezone(message.chat.id, timezone)
        pass

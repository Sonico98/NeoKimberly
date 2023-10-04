from neokimberly import kimberly
from pyrogram.enums import ChatMemberStatus

async def is_admin(chat_id, user_id):
    member = await kimberly.get_chat_member(chat_id, user_id)
    status = member.status
    if (status == ChatMemberStatus.OWNER or status == ChatMemberStatus.ADMINISTRATOR):
        return True
    return False

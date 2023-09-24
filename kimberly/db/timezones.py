from db.generic import *
from db.mongodb import db

# Collection
grps = db.groups


async def set_group_timezone(chat_id, timezone: str):
    await store_group_value(grps, chat_id, "timezone", timezone)

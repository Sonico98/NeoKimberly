from db.generic import *
from db.mongodb import db
from datetime import date,time

# Collection
grps = db.groups


async def group_has_tz(chat_id):
    res = await find_docs(grps, { "group": chat_id, \
                                 "timezone": {"$exists":"true"}})
    if (len(res) > 0):
        return True
    return False 


async def set_group_timezone(chat_id, timezone: str):
    await store_group_value(grps, chat_id, "timezone", timezone)


async def set_group_nisman_time(chat_id, time: time):
    await store_group_value(grps, chat_id, "nisman_time", str(time))


async def set_group_nisman_day(chat_id, day: date):
    await store_group_value(grps, chat_id, "nisman_day", str(day))


async def get_all_groups_times():
    res = await find_docs(grps, {}, { "group": 1, "timezone": 1, "nisman_day": 1, "nisman_time": 1 })
    if (len(res) > 0):
        return res
    return []

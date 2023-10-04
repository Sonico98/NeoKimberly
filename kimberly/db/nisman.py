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
    await modify_db_value(grps, chat_id, "timezone", timezone, "$set")


async def set_group_nisman_time(chat_id, time: time):
    await modify_db_value(grps, chat_id, "nisman_time", str(time), "$set")


async def set_group_nisman_day(chat_id, day: date):
    await modify_db_value(grps, chat_id, "nisman_day", str(day), "$set")


async def set_group_special_date(chat_id, special_dates: list):
    await modify_db_value(grps, chat_id, "special_dates", special_dates, "$set")


async def get_all_groups_times():
    res = await find_docs(grps, {}, { "group": 1, "timezone": 1, "nisman_day": 1, "nisman_time": 1 })
    if (len(res) > 0):
        return res
    return []


async def store_nisman(chat_id, user_id, nisman_count):
    await modify_db_value(grps, chat_id, "nismans", nisman_count, "$inc", user_id)

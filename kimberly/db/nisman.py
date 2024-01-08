from datetime import date, timedelta
from config.login import default_nisman_time, default_timezone
from db.generic import *
from db.mongodb import db
from utils.time_parser import get_today

# Collection
grps = db.groups


async def group_has_tz(chat_id):
    res = await find_docs(grps, { "_id": chat_id, \
                                 "timezone": {"$exists":"true"}})
    if (len(res) > 0):
        return True
    return False 


async def set_group_timezone(chat_id, timezone: str):
    await modify_db_value(grps, chat_id, "timezone", timezone, "$set")


async def set_group_nisman_time(chat_id, time):
    await modify_db_value(grps, chat_id, "nisman_time", time, "$set")


async def set_group_nisman_day(chat_id, day: date):
    await modify_db_value(grps, chat_id, "nisman_day", str(day), "$set")


async def add_group_special_date(chat_id, special_dates: list):
    for date in special_dates:
        await modify_db_value(grps, chat_id, "special_dates", date, "$push")


async def rm_group_special_date(chat_id, special_dates: list):
    for date in special_dates:
        await modify_db_value(grps, chat_id, "special_dates", date, "$pull")


async def set_group_nisman_defaults(chat_id):
    await set_group_timezone(chat_id, default_timezone)
    # We already check if the time format is correct when starting the bot
    await set_group_nisman_time(chat_id, default_nisman_time)
    day = await get_today(default_timezone) + timedelta(days=1)
    await set_group_nisman_day(chat_id, day)
    await add_group_special_date(chat_id, ["12-25", "01-01"]) # Christmas + New Year
    return day


async def get_all_groups_times():
    groups_without_tz = await find_docs(grps, { "timezone": { "$exists": False } } )
    if (len(groups_without_tz) > 0):
        for group in groups_without_tz:
            await set_group_nisman_defaults(group.get("_id"))

    res = await find_docs(grps, {}, { "_id": 1, "timezone": 1, "nisman_day": 1, \
                                     "nisman_time": 1, "special_dates": 1 })
    if (len(res) > 0):
        return res
    return []


async def store_nisman(chat_id, user_id, nisman_count):
    await modify_db_value(grps, chat_id, "nismans", nisman_count, "$inc", user_id)

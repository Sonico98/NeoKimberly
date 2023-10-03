from datetime import date, datetime, timedelta
from pyrogram import filters
import pytz
from config.login import nisman_time, timezone
from db.nisman import *
from neokimberly import kimberly

grps_time_data = []

async def build_timezones_list():
    global grps_time_data
    grps_time_data = await get_all_groups_times()


async def assign_time(chat_id, time):
    gtime = datetime.strptime(time, "%H:%M:%S").time()
    await set_group_nisman_time(chat_id, gtime)


async def get_today(timezone):
    return datetime.now(pytz.timezone(timezone)).date()


async def add_to_grps_t_data(chat_id, timezone, nisman_time, nisman_day):
    group_db_id = await get_doc_id({"group": chat_id})
    group = {
        "_id": group_db_id,
        "group": chat_id,
        "timezone": timezone,
        "nisman_time": nisman_time,
        "nisman_day": nisman_day
    }
    grps_time_data.append(group)


# TODO: Implement divide and conquer
async def search_group_in_list(chat_id):
    for group in grps_time_data:
        if (group.get("group") == chat_id):
            return group
    return None


async def update_group_time_data(chat_id, timezone=None, nisman_time=None, nisman_day=None):
    for group in grps_time_data:
        if (group.get("group") == chat_id):
            if (timezone is not None):
                group.update({"timezone": timezone})
            if (nisman_time is not None):
                group.update({"nisman_time": nisman_time})
            if (nisman_day is not None):
                group.update({"nisman_day": nisman_day})


# Set group's timezone when the bot is added to the group
@kimberly.on_message(filters.group & filters.new_chat_members, group=-1)
async def assign_default_group_timezone(_, message):
    if len(message.new_chat_members) > 1:
        return
    user = message.new_chat_members[0]
    if (user.is_self):
        chat_id = message.chat.id
        if (not await group_has_tz(chat_id)):
            await set_group_timezone(chat_id, timezone)
            # We already check if the time format is correct when starting the bot
            await assign_time(chat_id, nisman_time)
            day = await get_today(timezone) + timedelta(days=1)
            await set_group_nisman_day(chat_id, day)
            await add_to_grps_t_data(chat_id, timezone, nisman_time, day)
        else:
            print("Group already has timezone")

# TODO: check for special dates
@kimberly.on_message(filters.group, group=-5)
async def check_nisman(_, message):
    msg_datetime = message.date
    chat_id = message.chat.id
    user = message.from_user
    group = await search_group_in_list(chat_id)
    if (group is not None):
        grp_timezone = pytz.timezone(group.get("timezone"))
        grp_nisman_time = group.get("nisman_time")
        grp_nisman_day = group.get("nisman_day")
        grp_nisman_datetime = datetime.strptime(f"{grp_nisman_day} {grp_nisman_time}", "%Y-%m-%d %H:%M:%S").astimezone()
        msg_datetime_timezone = msg_datetime.astimezone(grp_timezone)
        if (msg_datetime_timezone >= grp_nisman_datetime):
            await message.reply_text(f"{user.first_name} ha hecho la Nisman")
            await store_nisman(chat_id, user.id, 1)
            day = await get_today(timezone) + timedelta(days=1)
            await update_group_time_data(chat_id, nisman_day=day)
            await set_group_nisman_day(chat_id, day)

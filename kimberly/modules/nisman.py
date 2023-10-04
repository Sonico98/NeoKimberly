from datetime import datetime, timedelta
from pyrogram import filters
import pytz
from config.login import nisman_time, timezone
from db.nisman import *
from neokimberly import kimberly
from utils.users import is_admin
from utils.time_parser import time_format_is_correct

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


@kimberly.on_message(filters.group & filters.command("setup_huso_horario"))
async def setup_timezone(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (await is_admin(chat_id, user_id)):
        if (len(message.command) > 1):
            timezone = message.command[1]
            if timezone in pytz.all_timezones:
                day = await get_today(timezone) + timedelta(days=1)
                await set_group_timezone(chat_id, timezone)
                await set_group_nisman_day(chat_id, day)
                await update_group_time_data(chat_id, timezone, nisman_day=day)
                await message.reply_text(f"Se actualizó el huso horario del grupo a {timezone}.")
            else:
                await message.reply_text(f"'{timezone}' no corresponde a un huso horario válido.")
            pass
        else:
            group = await search_group_in_list(chat_id)
            # Because the group will always get added to the list as soon as the bot gets added to it
            assert group is not None
            await message.reply_text("Con este comando podés configurar "
                "el huso horario a considerar para la Nisman del grupo, por ejemplo "
                "<code>America/Argentina/Buenos_Aires</code>. "
                "Podés fijarte tu huso horario en "
                "<a href='https://en.wikipedia.org/wiki/List_of_tz_database_time_zones'>el listado de Wikipedia</a>.\n"
                f"El huso horario establecido para el grupo es: <code>{group.get('timezone')}</code>\n\n"
                "<b>Modo de uso:</b> <pre>/setup_huso_horario «huso_horario»</pre>\n"
                "<b>Ejemplo:</b> <pre>/setup_huso_horario America/Argentina/Buenos_Aires</pre>")
    else:
        message.reply_text("Este comando sólo está disponible para administradores.")


@kimberly.on_message(filters.group & filters.command("setup_hora_nisman"))
async def setup_time(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (await is_admin(chat_id, user_id)):
        if (len(message.command) > 1):
            time = message.command[1]
            if (await time_format_is_correct(time)):
                await assign_time(chat_id, time)
                await update_group_time_data(chat_id, nisman_time=time)
                await message.reply_text(f"Se actualizó el horario de nisman del grupo a {time}.")
            else:
                await message.reply_text(f"'{time}' no corresponde a un horario válido.")
            pass
        else:
            group = await search_group_in_list(chat_id)
            # Because the group will always get added to the list as soon as the bot gets added to it
            assert group is not None
            await message.reply_text("Con este comando podés configurar "
                "a qué hora se hace la Nisman en el grupo. La Nisman es un juego "
                "que consiste en ser el primero en enviar un mensaje a partir del horario establecido.\n"
                f"El horario establecido para el grupo es: <code>{group.get('nisman_time')}</code>\n\n"
                "<b>Modo de uso:</b> <pre>/setup_hora_nisman «H:M:S»</pre>\n"
                "<b>Ejemplo:</b> <pre>/setup_hora_nisman 20:05:00</pre>")
    else:
        message.reply_text("Este comando sólo está disponible para administradores.")

# TODO: check for special dates
# TODO: think of another way of checking for messages to prevent floodwaits
@kimberly.on_message(filters.group & filters.text, group=-5)
async def check_nisman(_, message):
    msg_datetime = message.date
    chat_id = message.chat.id
    user = message.from_user
    group = await search_group_in_list(chat_id)
    # Because the group will always get added to the list as soon as the bot gets added to it
    assert group is not None
    grp_timezone = pytz.timezone(group.get("timezone"))
    grp_n_time = group.get("nisman_time")
    grp_n_day = group.get("nisman_day")
    grp_nisman_datetime = grp_timezone.localize(datetime.strptime(f"{grp_n_day} {grp_n_time}", "%Y-%m-%d %H:%M:%S"))
    msg_datetime_timezone = msg_datetime.astimezone(grp_timezone)
    if (msg_datetime_timezone >= grp_nisman_datetime):
        await message.reply_text(f"{user.first_name} ha hecho la Nisman")
        await store_nisman(chat_id, user.id, 1)
        day = await get_today(timezone) + timedelta(days=1)
        await update_group_time_data(chat_id, nisman_day=day)
        await set_group_nisman_day(chat_id, day)

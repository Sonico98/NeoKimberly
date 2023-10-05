from datetime import datetime, timedelta
from pyrogram import filters
import pytz
from config.login import default_nisman_time, default_timezone
from db.nisman import *
from neokimberly import kimberly
from utils.leaderboard import send_leaderboard
from utils.time_parser import get_today, date_format_is_correct, time_format_is_correct
from utils.users import is_admin

grps_time_data = []


async def build_timezones_list():
    global grps_time_data
    grps_time_data = await get_all_groups_times()


async def add_to_grps_t_data(chat_id, timezone, nisman_time, nisman_day, special_dates: list):
    group_db_id = await get_doc_id({"group": chat_id})
    group = {
        "_id": group_db_id,
        "group": chat_id,
        "timezone": timezone,
        "nisman_time": nisman_time,
        "nisman_day": nisman_day,
        "special_dates": special_dates
    }
    grps_time_data.append(group)


# TODO: Implement divide and conquer
async def search_group_in_list(chat_id):
    for group in grps_time_data:
        if (group.get("group") == chat_id):
            return group
    return None


async def update_group_time_data(chat_id, timezone=None, nisman_time=None, \
                                 nisman_day=None, special_dates=None, rm_date=False):
    for group in grps_time_data:
        if (group.get("group") == chat_id):
            if (timezone is not None):
                group.update({"timezone": timezone})
            if (nisman_time is not None):
                group.update({"nisman_time": nisman_time})
            if (nisman_day is not None):
                group.update({"nisman_day": nisman_day})
            if (special_dates is not None):
                if (rm_date):
                    for date in special_dates:
                        group.get("special_dates").remove(date)
                else:
                    for date in special_dates:
                        group.get("special_dates").append(date)


async def group_date_exists(chat_id, date):
    group = await search_group_in_list(chat_id)
    assert group is not None
    group_dates = group.get("special_dates")
    for gdate in group_dates:
        if (date == gdate):
            return True
    return False

# Set group's timezone when the bot is added to the group
@kimberly.on_message(filters.group & filters.new_chat_members, group=-1)
async def assign_default_group_timezone(_, message):
    if len(message.new_chat_members) > 1:
        return
    user = message.new_chat_members[0]
    if (user.is_self):
        chat_id = message.chat.id
        if (not await group_has_tz(chat_id)):
            day = await set_group_nisman_defaults(chat_id)
            await add_to_grps_t_data(chat_id, default_timezone, default_nisman_time, day, ["12-25", "01-01"])
        else:
            print("Group already has timezone")


@kimberly.on_message(filters.group & filters.command("setup_huso_horario"))
async def setup_timezone(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (not await is_admin(chat_id, user_id)):
        message.reply_text("Este comando sólo está disponible para administradores.")
    else:
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


@kimberly.on_message(filters.group & filters.command("setup_hora_nisman"))
async def setup_time(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (not await is_admin(chat_id, user_id)):
        message.reply_text("Este comando sólo está disponible para administradores.")
    else:
        if (len(message.command) > 1):
            time = message.command[1]
            if (await time_format_is_correct(time)):
                await set_group_nisman_time(chat_id, time)
                await update_group_time_data(chat_id, nisman_time=time)
                await message.reply_text(f"Se actualizó el horario de nisman del grupo a {time}.")
            else:
                await message.reply_text(f"'{time}' no corresponde a un horario válido.")
        else:
            group = await search_group_in_list(chat_id)
            # Because the group will always get added to the list as soon as the bot gets added to it
            assert group is not None
            await message.reply_text("Con este comando podés configurar "
                "a qué hora se hace la Nisman en el grupo.\n"
                f"El horario establecido para el grupo es: <code>{group.get('nisman_time')}</code>\n\n"
                "<b>Modo de uso:</b> <pre>/setup_hora_nisman «H:M:S»</pre>\n"
                "<b>Ejemplo:</b> <pre>/setup_hora_nisman 20:05:00</pre>")

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
    grp_nisman_datetime = grp_timezone.localize(datetime.strptime(
        f"{grp_n_day} {grp_n_time}", "%Y-%m-%d %H:%M:%S")
    )
    msg_datetime_tz_aware = msg_datetime.astimezone(grp_timezone)
    if (msg_datetime_tz_aware >= grp_nisman_datetime):
        christmas = False
        new_year = False
        special_date = False
        nisman_points = 1
        special_date_match = ""
        special_dates = group.get("special_dates")
        for month_and_day in special_dates: 
            print(month_and_day)
            current_year = datetime.now().year
            date = datetime.strptime(f"{current_year}-{month_and_day}", "%Y-%m-%d")
            if (date.astimezone(grp_timezone).date() == msg_datetime_tz_aware.date()):
                if (month_and_day == "12-25"):
                    christmas = True
                    return
                elif (month_and_day == "01-01"):
                    new_year = True
                    return
                else:
                    special_date = True
                    special_date_match = month_and_day
                    return

        if (msg_datetime_tz_aware in group.get("special_dates")):
            pass
        if (christmas):
            await message.reply_text(f"¡<b>{user.first_name}</b> hizo la Nisman navideña!\n"
                                        "Suma <b>5 puntos</b>.")
            nisman_points = 5
        elif (new_year):
            await message.reply_text(f"¡<b>{user.first_name}</b> hizo la primer Nisman del año!\n"
                                        "Suma <b>3 puntos</b>.")
            nisman_points = 3
        elif (special_date):
            await message.reply_text(f"¡<b>{user.first_name}</b> hizo la Nisman especial " \
                                        f"del {special_date_match}!\nSuma <b>2 puntos</b>.")
            nisman_points = 2
        else:
            await message.reply_text(f"{user.first_name} hizo la Nisman")
        await store_nisman(chat_id, user.id, nisman_points)
        day = await get_today(default_timezone) + timedelta(days=1)
        await update_group_time_data(chat_id, nisman_day=day)
        await set_group_nisman_day(chat_id, day)


@kimberly.on_message(filters.group & filters.command("nisman"))
async def nisman_command(_, message):
    header_msg = "**Ranking de Nisman**"
    error_msg = "Todavía nadie hizo la Nisman en este grupo.\n" + \
                "La Nisman es un juego que consiste en ser el primero en enviar " + \
                "un mensaje a partir del horario establecido en /setup_hora_nisman."
    await send_leaderboard(_, message, "nismans", "nisman_list", \
                           header_msg=header_msg, error_msg=error_msg)


@kimberly.on_callback_query(filters.regex("nisman_list"))
async def change_page(_, callback_query):
    next_page = int(callback_query.data.split(":")[1])
    message = callback_query.message
    header_msg = "**Ranking de Nisman**"
    await send_leaderboard(_, message, "nismans", "nisman_list", \
                           callback=True, page_number=next_page, header_msg=header_msg)

@kimberly.on_message(filters.group & filters.command("setup_add_fechas_nisman"))
async def add_special_date(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (not await is_admin(chat_id, user_id)):
        message.reply_text("Este comando sólo está disponible para administradores.")
    else:
        if (len(message.command) > 1):
            fecha = message.command[1]
            if (await date_format_is_correct(fecha)):
                await add_group_special_date(chat_id, [fecha])
                await update_group_time_data(chat_id, special_dates=[fecha])
                await message.reply_text(f"Se añadió la fecha especial {fecha}.")
            else:
                await message.reply_text(f"'{fecha}' no corresponde a una fecha válida.")
        else:
            group = await search_group_in_list(chat_id)
            # Because the group will always get added to the list as soon as the bot gets added to it
            assert group is not None
            await message.reply_text("Con este comando podés añadir "
                "fechas especiales de Nisman al grupo. Cuando alguien "
                "haga la Nisman en una fecha especial, se le sumarán 2 puntos. "
                "En el caso de Navidad, se sumarán 5 puntos, y en Año Nuevo, 3 puntos.\n"
                f"Las fechas especiales en el grupo son: <code>{group.get('special_dates')}</code>\n\n"
                "<b>Modo de uso:</b> <pre>/setup_add_fechas_nisman «Mes-Día»</pre>\n"
                "<b>Ejemplo:</b> <pre>/setup_add_fechas_nisman 01-27</pre>")


@kimberly.on_message(filters.group & filters.command("setup_rm_fechas_nisman"))
async def add_special_date(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (not await is_admin(chat_id, user_id)):
        message.reply_text("Este comando sólo está disponible para administradores.")
    else:
        if (len(message.command) > 1):
            fecha = message.command[1]
            if (await group_date_exists(chat_id, fecha)):
                await rm_group_special_date(chat_id, [fecha])
                await update_group_time_data(chat_id, special_dates=[fecha], rm_date=True)
                await message.reply_text(f"Se quitó la fecha especial {fecha}.")
            else:
                await message.reply_text(f"'{fecha}' no corresponde a una fecha existente.")
        else:
            group = await search_group_in_list(chat_id)
            # Because the group will always get added to the list as soon as the bot gets added to it
            assert group is not None
            await message.reply_text("Con este comando podés quitar "
                "fechas especiales de Nisman al grupo.\n"
                f"Las fechas especiales en el grupo son: <code>{group.get('special_dates')}</code>\n\n"
                "<b>Modo de uso:</b> <pre>/setup_rm_fechas_nisman «Mes-Día»</pre>\n"
                "<b>Ejemplo:</b> <pre>/setup_rm_fechas_nisman 01-27</pre>")

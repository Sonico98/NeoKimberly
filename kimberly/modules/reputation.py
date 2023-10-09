import re
from pyrogram import filters
from db.reputation import choose_rep_change_msg, get_user_reps, set_group_rep_msg, store_rep
from neokimberly import kimberly
from utils.leaderboard import send_leaderboard
from utils.users import is_admin


@kimberly.on_message(filters.group & filters.text & filters.reply &
                     filters.regex("^\\+{1,}$|^\\-{1,}$|^\\+[0-9]{1,}$|^\\-[0-9]{1,}$"), group=-2)
async def change_rep(_, message):
    chat_id = message.chat.id
    receiving_user_id = message.reply_to_message.from_user.id
    receiving_user_name = message.reply_to_message.from_user.first_name
    giving_user_id = message.from_user.id
    giving_user_name = message.from_user.first_name
    rep_change = 0

    if (receiving_user_id == giving_user_id):
        await message.reply_text("No te quieras hacer el canchero.")
        return

    patterns = [re.compile("\\+{1,}"), re.compile("\\-{1,}"),
                re.compile("\\+\\d{1,}"), re.compile("\\-\\d{1,}")]
    for index, pattern in enumerate(patterns):
        match = pattern.fullmatch(message.text)
        if (match is not None):
            rep_change_msg = ""

            # Pattern: +, +++, +++++... or -, ---, -----...
            if (index == 0 or index == 1):
                for _ in message.text:
                    if (index == 0):
                        rep_change += 1
                        # Hard limit rep changes to 10.
                        # Might make it configurable in the future
                        if (rep_change > 10):
                            rep_change = 10
                        rep_change_msg = await choose_rep_change_msg(chat_id)
                    else:
                        rep_change -= 1
                        if (rep_change < -10):
                            rep_change = -10
                        rep_change_msg = await choose_rep_change_msg(chat_id, dec=True)

            # Pattern: +2, +58, +98342... or -2, -58, -98342...
            if (index == 2 or index == 3):
                if (index == 2):
                    rep_change += int(message.text[1:])
                    if (rep_change > 10):
                        rep_change = 10
                    rep_change_msg = await choose_rep_change_msg(chat_id)
                else:
                    rep_change -= int(message.text[1:])
                    if (rep_change < -10):
                        rep_change = -10
                    rep_change_msg = await choose_rep_change_msg(chat_id, dec=True)

            await store_rep(chat_id, receiving_user_id, rep_change)
            reps = await get_user_reps(chat_id, giving_user_id, receiving_user_id)
            assert rep_change_msg is not None
            await message.reply_text(rep_change_msg.replace(
                "{usuario_da}", f"**{giving_user_name}**"
            ).replace(
                "{usuario_recibe}", f"**{receiving_user_name}**"
            ).replace(
                "{usuario_recibe}", f"**{receiving_user_name}**"
            ).replace(
                "{rep_usuario_da}", f"**{reps[0]}**"
            ).replace(
                "{rep_usuario_recibe}", f"**{reps[1]}**"
            ).replace(
                "{cambio_rep}", f"**{rep_change}**"
            ))
            return


@kimberly.on_message(filters.group & filters.text & filters.command("rep"))
async def rep_command(_, message):
    header_msg = "**Social credit leaderboard**"
    error_msg = "Todavía no hay un listado de reputaciones en este grupo.\n" + \
                "Respondé con + o - al mensaje de alguien."
    await send_leaderboard(_, message, "rep", "rep_list", header_msg=header_msg, error_msg=error_msg)


@kimberly.on_callback_query(filters.regex("rep_list"))
async def change_page(_, callback_query):
    next_page = int(callback_query.data.split(":")[1])
    message = callback_query.message
    header_msg = "**Social credit leaderboard**"
    await send_leaderboard(_, message, "rep", "rep_list", callback=True, page_number=next_page, header_msg=header_msg)


@kimberly.on_message(filters.group & filters.text & filters.command("setup_msg_rep"))
async def setup_msg_rep(_, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if (not await is_admin(chat_id, user_id)):
        await message.reply_text("Este comando sólo está disponible para administradores.")
    else:
        if (len(message.command) > 1):
            msg_type = message.command[1]
            if (msg_type == "inc" or msg_type == "dec"):
                msg_list = message.command[2:]
                msg = " ".join(map(str,msg_list)) 
                key_words = ["{usuario_recibe}", "{usuario_da}", "{rep_usuario_da}", "{rep_usuario_recibe}", "{cambio_rep}"]
                if all([word in msg for word in key_words]):
                    if (msg_type == "inc"):
                        await set_group_rep_msg(chat_id, msg)
                        await message.reply_text(f"Se actualizó el mensaje a mostrar "
                                                "al incrementar la reputación de un usuario.")
                    elif (msg_type == "dec"):
                        await set_group_rep_msg(chat_id, msg, dec=True)
                        await message.reply_text(f"Se actualizó el mensaje a mostrar "
                                                "al decrementar la reputación de un usuario.")
                else:
                    await message.reply_text("El formato del mensaje no es correcto. Asegúrate "
                                             "de haber escrito correctamente todos "
                                             "los campos requeridos, y que los mismos "
                                             "estén encerrados {entre llaves}")
            else:
                await message.reply_text("No seleccionaste el tipo de mensaje correcto. "
                                         "Antes de escribir tu nuevo mensaje de reputación, "
                                         "debes elegir si quieres cambiar el mensaje a mostrar "
                                         "cuando se incremente la reputación (<b>inc</b>) o el mensaje "
                                         "para cuando se decremente la reputación (<b>dec</b>).")
                return
        else:
            await message.reply_text("<b>[RECOMENDACIÓN]</b> Es más fácil comprender el uso "
                "de este comando al leer este mensaje en Telegram para escritorio.\n\n"
                "Con este comando podés configurar el mensaje a mostrar "
                "al incrementar o decrementar la reputación de un usuario.\n"
                "<b>Modo de uso:</b> <code>/setup_msg_rep «inc/dec» «mensaje»</code>\n"
                "Se debe especificar si se quiere cambiar el mensaje de"
                "incremento <b>(inc)</b> o decremento <b>(dec)</b>.\n\n"
                "El mensaje **debe** contener todos los campos "
                "mencionados a continuación, encerrados {entre llaves}:\n"
                "<code>{usuario_da}</code>: Es el usuario que está dando reputación a otro.\n"
                "<code>{usuario_recibe}</code>: Es el usuario que recibe un cambio de reputación.\n"
                "<code>{rep_usuario_da}</code>: Corresponde a la reputación del <code>{usuario_da}</code>.\n"
                "<code>{rep_usuario_recibe}</code>: Corresponde a la reputación del <code>{usuario_recibe}</code>.\n"
                "<code>{cambio_rep}</code>: Es cuánta reputación recibe o pierde el <code>{usuario_recibe}</code>.\n\n"
                "<b>Ejemplo:</b>\n<code>/setup_msg_rep inc {usuario_da} ({rep_usuario_da}) ha incrementado "
                "la reputación de {usuario_recibe} en {cambio_rep} puntos. La nueva reputación de "
                "{usuario_recibe} es de: {rep_usuario_recibe}.</code>")

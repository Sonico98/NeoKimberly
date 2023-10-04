import re
from pyrogram import filters
from db.reputation import get_user_reps, store_rep
from neokimberly import kimberly
from utils.leaderboard import send_leaderboard


@kimberly.on_message(filters.group & filters.text & filters.reply &
                     filters.regex("^\\+{1,}$|^\\-{1,}$|^\\+[0-9]{1,}$|^\\-[0-9]{1,}$"), group=-2)
async def change_rep(_, message):
    chat_id = message.chat.id
    receiving_user_id = message.reply_to_message.from_user.id
    receiving_user_name = message.reply_to_message.from_user.first_name
    giving_user_id = message.from_user.id
    giving_user_name = message.from_user.first_name
    rep_change = 0
    rep_change_msg = ""
    rep_decrease_msg = ("ATTENTION **{}** 不要再这样做! DO NOT DO THIS AGAIN!\n"
                        "**{} ({})** has decreased your social credit score "
                        "by **{}** points.\nYour new score: {}")

    rep_increase_msg = ("ATTENTION **{}** 中华人民共和国寄语 Great work!\n"
                        "**{} ({})**  has increased your social credit score "
                        "by **{}** points.\nYour new score: {}.")

    if (receiving_user_id == giving_user_id):
        await message.reply_text("No te quieras hacer el canchero.")
        return

    patterns = [re.compile("\\+{1,}"), re.compile("\\-{1,}"),
                re.compile("\\+\\d{1,}"), re.compile("\\-\\d{1,}")]
    for index, pattern in enumerate(patterns):
        match = pattern.fullmatch(message.text)
        if (match is not None):
            # Pattern: +, +++, +++++... or -, ---, -----...
            if (index == 0 or index == 1):
                for _ in message.text:
                    if (index == 0):
                        rep_change += 1
                        # Hard limit rep changes to 10.
                        # Might make it configurable in the future
                        if (rep_change > 10):
                            rep_change = 10
                        rep_change_msg = rep_increase_msg
                    else:
                        rep_change -= 1
                        if (rep_change < -10):
                            rep_change = -10
                        rep_change_msg = rep_decrease_msg

            # Pattern: +2, +58, +98342... or -2, -58, -98342...
            if (index == 2 or index == 3):
                if (index == 2):
                    rep_change += int(message.text[1:])
                    if (rep_change > 10):
                        rep_change = 10
                    rep_change_msg = rep_increase_msg
                else:
                    rep_change -= int(message.text[1:])
                    if (rep_change < -10):
                        rep_change = -10
                    rep_change_msg = rep_decrease_msg

            await store_rep(chat_id, receiving_user_id, rep_change)
            reps = await get_user_reps(chat_id, giving_user_id, receiving_user_id)
            await message.reply_text(rep_change_msg.format(
                receiving_user_name,
                giving_user_name, reps[0],
                rep_change, reps[1]
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

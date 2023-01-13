from db.reputation import store_rep, get_reps, get_all_reps
from neokimberly import kimberly
from pyrogram import filters
import re


@kimberly.on_message(filters.group & filters.text & filters.reply & \
                         filters.regex("^\\+{1,}$|^\\-{1,}$|^\\+[0-9]{1,}$|^\\-[0-9]{1,}$"), group=-2)
async def change_rep(client, message):
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


    patterns = [re.compile("\\+{1,}"), re.compile("\\-{1,}"), \
        re.compile("\\+\\d{1,}"), re.compile("\\-\\d{1,}")]
    for index, pattern in enumerate(patterns):
        match = pattern.fullmatch(message.text)
        if (match is not None):
            # Pattern: +, +++, +++++... or -, ---, -----...
            if (index == 0 or index == 1):
                for _ in message.text:
                    if (index == 0):
                        rep_change += 1
                        rep_change_msg = rep_increase_msg
                    else:
                        rep_change -= 1
                        rep_change_msg = rep_decrease_msg

            # Pattern: +2, +58, +98342... or -2, -58, -98342...
            if (index == 2 or index == 3):
                if (index == 2):
                    rep_change += int(message.text[1:])
                    rep_change_msg = rep_increase_msg
                else:
                    rep_change -= int(message.text[1:])
                    rep_change_msg = rep_decrease_msg

            await store_rep(chat_id, receiving_user_id, rep_change)
            reps = await get_reps(chat_id, giving_user_id, receiving_user_id)
            await message.reply_text(rep_change_msg.format(
                                             receiving_user_name,
                                             giving_user_name, reps[0],
                                             rep_change, reps[1]
                                     ))
            return


@kimberly.on_message(filters.group & filters.text & filters.command("rep"))
async def rep_list(client, message):
    chat_id = message.chat.id
    user_rep_list = await get_all_reps(chat_id)
    if (user_rep_list == {}):
        await message.reply_text("Todavía no hay un listado de reputaciones en este grupo.\n"
                                     "Respondé con + o - al mensaje de alguien")
        return

    reps = []
    user_ids = []
    users = []
    for index, group in enumerate(user_rep_list):
        reps.append(group[0])
        user_ids.append(group[1])
        # Untested - workaround 200 users limit
        # (we only get 100 users at a time to possibly avoid FloodWait errors)
        if (index == 100 or group[1] == user_rep_list[-1][1]):
            if (len(users) > 0):
                users.append(await kimberly.get_users(user_ids))
            else:
                users = await kimberly.get_users(user_ids)
            user_ids = []

    # Send the list without links first, then add the links
    # by editing the message. This way users are not mentioned
    printed_rep_list = "**Social credit leaderboard**\n\n"
    reply = await message.reply_text(printed_rep_list)
    for index, user in enumerate(users):
        printed_rep_list += f"{reps[index]}  -  [{user.first_name}](tg://user?id={user.id})\n"
    await reply.edit_text(printed_rep_list)


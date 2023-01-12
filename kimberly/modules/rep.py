from pyrogram.methods.messages import send_message
from db.rep import store_rep, get_reps
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




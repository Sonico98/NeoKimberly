from utils.lists import list_to_text
from db.reputation import store_rep, get_user_reps, get_all_reps
from neokimberly import kimberly
from pyrogram import filters
import re


@kimberly.on_message(filters.group & filters.text & filters.reply & \
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
            reps = await get_user_reps(chat_id, giving_user_id, receiving_user_id)
            await message.reply_text(rep_change_msg.format(
                                             receiving_user_name,
                                             giving_user_name, reps[0],
                                             rep_change, reps[1]
                                     ))
            return


# TODO: Armar la parte del teclado, para generar una nueva lista cada vez que se pasa de página
@kimberly.on_message(filters.group & filters.text & filters.command("rep"))
async def get_rep_list(_, message):
    chat_id = message.chat.id
    user_rep_list = await get_all_reps(chat_id) # [user_rep, user_id]
    if (user_rep_list == {}):
        await message.reply_text("Todavía no hay un listado de reputaciones en este grupo.\n"
                                     "Respondé con + o - al mensaje de alguien")
        return

    mem = []
    async for member in kimberly.get_chat_members(message.chat.id):
        mem.append(member.user.id)
    # Split the members into chunks of 15 members each
    chat_members = [mem[i * 15:(i + 1) * 15] for i in range((len(mem) + 15 - 1) // 15 )]

    rep_list_header = "**Social credit leaderboard**"
    reply = await message.reply_text(rep_list_header)
    rep_list = await build_rep_list(user_rep_list, chat_members, 1)
    await reply.edit_text(f"{rep_list_header}\n\n{rep_list}")


async def build_rep_list(user_rep_list, chat_members, page_number):
    all_user_reps_in_db = []
    all_user_ids_in_db = []
    for _, rep_list in enumerate(user_rep_list):
        all_user_reps_in_db.append(rep_list[0])
        all_user_ids_in_db.append(rep_list[1])

    # Group together only the Nth 15 members currently in the group
    # that had their reputation changed
    members_user_ids = []
    members_reps = []
    for member in chat_members[page_number-1]:
        if member in all_user_ids_in_db:
            mem_pos = all_user_ids_in_db.index(member)
            members_user_ids.append(all_user_ids_in_db[mem_pos])
            members_reps.append(all_user_reps_in_db[mem_pos])
            # Get rid of all the members currently in the group
            del all_user_ids_in_db[mem_pos]
            del all_user_reps_in_db[mem_pos]

    # Sort the reputation list from largest to smallest
    current_users = await kimberly.get_users(members_user_ids)
    old_users = await kimberly.get_users(all_user_ids_in_db)
    assert isinstance(current_users, list)
    assert isinstance(old_users, list)
    tmp = []
    for index, user in enumerate(current_users):
        tmp.append(f"{members_reps[index]}  -  [{user.first_name}](tg://user?id={user.id})\n")
    # Don't add a link to members who left the group,
    # otherwise Telegram throws an error
    for index, old_member in enumerate(old_users):
        tmp.append(f"{all_user_reps_in_db[index]}  -  {old_member.first_name}\n")
    tmp.sort(reverse=True)

    rep_list = await list_to_text(tmp)
    return rep_list
from utils.lists import list_to_text
from db.reputation import store_rep, get_user_reps, get_all_reps
from neokimberly import kimberly
from pyrogram import filters
import re
from pykeyboard import InlineKeyboard


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


@kimberly.on_message(filters.group & filters.text & filters.command("rep"))
async def rep_command(_, message):
    await send_leaderboard(_, message)


@kimberly.on_callback_query(filters.regex("rep_list"))
async def change_page(_, callback_query):
    next_page = int(callback_query.data.split(":")[1])
    message = callback_query.message
    await send_leaderboard(_, message, callback=True, page_number=next_page)


async def send_leaderboard(_, message, callback=False, page_number=1):
    users_rep_list, chat_members, msg_header = await get_rep_and_chat_members(_, message)
    if (users_rep_list is not None and chat_members is not None):
        if (not callback):
            reply = await message.reply_text(msg_header)
            message = reply
        total_pages, rep_list = await build_rep_list(users_rep_list, chat_members, page_number)
        keyboard = ""
        if (total_pages > 1):
            keyboard = InlineKeyboard()
            keyboard.paginate(total_pages, page_number, 'rep_list:{number}')
        await message.edit_text(
            f"{msg_header}\n\n{await list_to_text(rep_list)}", reply_markup=keyboard
        )


async def get_rep_and_chat_members(_, message):
    chat_id = message.chat.id
    users_rep_list = await get_all_reps(chat_id) # [user_rep, user_id]
    if (users_rep_list == []):
        await message.reply_text("Todavía no hay un listado de reputaciones en este grupo.\n"
                                     "Respondé con + o - al mensaje de alguien.")
        return None, None, None

    chat_members = []
    async for member in kimberly.get_chat_members(message.chat.id):
        chat_members.append(member.user.id)

    msg_header = "**Social credit leaderboard**"
    return users_rep_list, chat_members, msg_header


# TODO: Maybe we can avoid splitting users and reps into 2 different lists
async def build_rep_list(user_rep_list, chat_members, page_number):
    # We receive the ids and reps in groups,
    # so we have to split them into two lists
    all_user_ids_in_db = [[]]
    all_user_reps_in_db = [[]]
    pos = 0
    for i, rep_list in enumerate(user_rep_list):
        if (i > 0 and i % 15 == 0):
            all_user_ids_in_db.append([])
            all_user_reps_in_db.append([])
            pos += 1
        all_user_ids_in_db[pos].append(rep_list[1])
        all_user_reps_in_db[pos].append(rep_list[0])
    total_pages = len(all_user_ids_in_db)

    # Each group consists of 15 users, so that we query
    # Telegram only for 15 users per page
    group_of_users = all_user_ids_in_db[page_number - 1]
    group_of_reps = all_user_reps_in_db[page_number - 1]

    # Separate current group members from users that left the group
    members_user_ids = []
    current_users_reps = []
    for member in chat_members:
        if member in group_of_users:
            mem_pos = group_of_users.index(member)
            members_user_ids.append(group_of_users[mem_pos])
            current_users_reps.append(group_of_reps[mem_pos])
            # Get rid of all the members currently in the group
            del group_of_users[mem_pos]
            del group_of_reps[mem_pos]

    # Sort the reputation list from largest to smallest
    current_users = await kimberly.get_users(members_user_ids)
    old_users = await kimberly.get_users(group_of_users)
    assert isinstance(current_users, list)
    assert isinstance(old_users, list)
    rep_list = []
    for index, user in enumerate(current_users):
        rep_list.append(f"{current_users_reps[index]}  -  [{user.first_name}](tg://user?id={user.id})\n")
    # Don't add a link to members who left the group,
    # otherwise Telegram throws an error
    for index, old_member in enumerate(old_users):
        rep_list.append(f"{group_of_reps[index]}  -  {old_member.first_name}\n")
    rep_list.sort(reverse=True)

    return total_pages, rep_list

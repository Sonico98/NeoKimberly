from natsort import realsorted
from neokimberly import kimberly
from utils.lists import list_to_text
from pykeyboard import InlineKeyboard
from db.generic import get_user_ids_with_value


async def send_leaderboard(_, message, value, key_callback_name, callback=False, page_number=1, header_msg="", error_msg=""):
    users_and_value, chat_members = await get_value_and_chat_members(_, message, value)
    if (users_and_value is not None and chat_members is not None):
        if (not callback):
            reply = await message.reply_text(header_msg)
            message = reply
        total_pages, rep_list = await build_paginated_leaderboard(users_and_value, chat_members, page_number)
        keyboard = ""
        if (total_pages > 1):
            keyboard = InlineKeyboard()
            keyboard.paginate(total_pages, page_number, key_callback_name + ':{number}')
        await message.edit_text(
            f"{header_msg}\n\n{await list_to_text(rep_list)}", reply_markup=keyboard
        )
    else:
        await message.reply_text(error_msg)
                                 

async def get_value_and_chat_members(_, message, value):
    chat_id = message.chat.id
    users_and_value = await get_user_ids_with_value(chat_id, value)  # [user_value, user_id]
    if (users_and_value == []):
        return None, None

    chat_members = []
    async for member in kimberly.get_chat_members(message.chat.id):
        chat_members.append(member.user.id)

    return users_and_value, chat_members


async def build_paginated_leaderboard(users_and_value, chat_members, page_number):
    # Split the list into chunks of 15 users each
    # and work only with the Nth group of 15 users,
    # where N = page_number
    all_users_and_value_in_db = [
        users_and_value[i * 15:(i + 1) * 15]
        for i in range((len(users_and_value) + 15 - 1) // 15)
    ]
    users_and_value_in_db = all_users_and_value_in_db[page_number - 1]
    total_pages = len(all_users_and_value_in_db)

    # Separate values and ids into two different lists
    user_ids_in_db = [id[1] for id in users_and_value_in_db]
    values_in_db = [value[0] for value in users_and_value_in_db]

    # Separate current group members from users that left the group
    current_members_ids = []
    current_members_values = []
    for member in chat_members:
        if member in user_ids_in_db:
            memb_pos = user_ids_in_db.index(member)
            current_members_ids.append(user_ids_in_db[memb_pos])
            current_members_values.append(values_in_db[memb_pos])
            del user_ids_in_db[memb_pos], values_in_db[memb_pos]
    previous_members_ids = user_ids_in_db
    previous_members_values = values_in_db

    current_members = await kimberly.get_users(current_members_ids)
    old_members = await kimberly.get_users(previous_members_ids)
    assert isinstance(current_members, list)
    assert isinstance(old_members, list)

    value_list = []
    for index, member in enumerate(current_members):
        value_list.append(
            f"{current_members_values[index]}  -  [{member.first_name}](tg://user?id={member.id})\n")
    # Don't add a link to members who left the group,
    # otherwise Telegram throws an error
    for index, old_member in enumerate(old_members):
        value_list.append(
            f"{previous_members_values[index]}  -  {old_member.first_name}\n")
    # rep_list.sort(key=natural_keys, reverse=True)
    value_list = realsorted(value_list, reverse=True)

    return total_pages, value_list

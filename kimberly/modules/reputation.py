import re
from pykeyboard import InlineKeyboard
from pyrogram import filters
from db.reputation import get_user_ids_with_value, get_user_reps, store_rep
from neokimberly import kimberly
from utils.lists import list_to_text
from natsort import realsorted


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
    await send_leaderboard(_, message)


@kimberly.on_callback_query(filters.regex("rep_list"))
async def change_page(_, callback_query):
    next_page = int(callback_query.data.split(":")[1])
    message = callback_query.message
    await send_leaderboard(_, message, callback=True, page_number=next_page)


async def send_leaderboard(_, message, callback=False, page_number=1):
    users_and_rep, chat_members, msg_header = await get_rep_and_chat_members(_, message)
    if (users_and_rep is not None and chat_members is not None):
        if (not callback):
            reply = await message.reply_text(msg_header)
            message = reply
        total_pages, rep_list = await build_rep_list(users_and_rep, chat_members, page_number)
        keyboard = ""
        if (total_pages > 1):
            keyboard = InlineKeyboard()
            keyboard.paginate(total_pages, page_number, 'rep_list:{number}')
        await message.edit_text(
            f"{msg_header}\n\n{await list_to_text(rep_list)}", reply_markup=keyboard
        )


async def get_rep_and_chat_members(_, message):
    chat_id = message.chat.id
    users_and_rep = await get_user_ids_with_value(chat_id, "rep")  # [user_rep, user_id]
    if (users_and_rep == []):
        await message.reply_text("Todavía no hay un listado de reputaciones en este grupo.\n"
                                 "Respondé con + o - al mensaje de alguien.")
        return None, None, None

    chat_members = []
    async for member in kimberly.get_chat_members(message.chat.id):
        chat_members.append(member.user.id)

    msg_header = "**Social credit leaderboard**"
    return users_and_rep, chat_members, msg_header


async def build_rep_list(users_and_rep, chat_members, page_number):
    # Split the list into chunks of 15 users each
    # and work only with the Nth group of 15 users,
    # where N = page_number
    all_users_and_rep_in_db = [
        users_and_rep[i * 15:(i + 1) * 15]
        for i in range((len(users_and_rep) + 15 - 1) // 15)
    ]
    users_and_reps_in_db = all_users_and_rep_in_db[page_number - 1]
    total_pages = len(all_users_and_rep_in_db)

    # Separate reps and ids into two different lists
    user_ids_in_db = [id[1] for id in users_and_reps_in_db]
    reps_in_db = [rep[0] for rep in users_and_reps_in_db]

    # Separate current group members from users that left the group
    current_members_ids = []
    current_members_reps = []
    for member in chat_members:
        if member in user_ids_in_db:
            memb_pos = user_ids_in_db.index(member)
            current_members_ids.append(user_ids_in_db[memb_pos])
            current_members_reps.append(reps_in_db[memb_pos])
            del user_ids_in_db[memb_pos], reps_in_db[memb_pos]
    previous_members_ids = user_ids_in_db
    previous_members_reps = reps_in_db

    current_members = await kimberly.get_users(current_members_ids)
    old_members = await kimberly.get_users(previous_members_ids)
    assert isinstance(current_members, list)
    assert isinstance(old_members, list)

    rep_list = []
    for index, member in enumerate(current_members):
        rep_list.append(
            f"{current_members_reps[index]}  -  [{member.first_name}](tg://user?id={member.id})\n")
    # Don't add a link to members who left the group,
    # otherwise Telegram throws an error
    for index, old_member in enumerate(old_members):
        rep_list.append(
            f"{previous_members_reps[index]}  -  {old_member.first_name}\n")
    # rep_list.sort(key=natural_keys, reverse=True)
    rep_list = realsorted(rep_list, reverse=True)

    return total_pages, rep_list

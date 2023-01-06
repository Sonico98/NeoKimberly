# Stores which was the last message the bot read in a group
from os import replace
from db.mongodb import db
from db.generic import *
from neokimberly import kimberly
from pyrogram import filters

# Collection
msgs = db.mensajes

@kimberly.on_message(filters.group & filters.all, group=-1)
async def save_message(client, message):
    chat_id = message.chat.id
    msg_id = message.id
    new_data = {
        "group": str(chat_id),
        "last_msg_id": str(msg_id)
    }

    # Check if the group is already present in the DB and save the data
    existing_group_doc = await find_one_doc(msgs, {"group": str(chat_id)})
    if (len(existing_group_doc) > 0):
        await replace_doc(msgs, existing_group_doc, new_data)
    else:
        await msgs.insert_one(new_data)


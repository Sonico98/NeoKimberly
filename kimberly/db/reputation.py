from db.generic import *
from db.mongodb import db

# Collection
grps = db.groups


async def get_user_reps(chat_id, giving_user_id, receiving_user_id):
    # The user giving rep is probably not on the DB yet
    giving_user_doc = {}
    while (giving_user_doc == {}):
        giving_user_doc = await find_one_doc(
            grps, { 
                "_id": chat_id, "users": { 
                    "$elemMatch": { 
                        "user_id": giving_user_id, \
                        "rep": { 
                            "$exists": "true"
                        } 
                    } 
                } 
            },
            { "users.rep.$": 1 }
        )
        if (giving_user_doc == {}):
            await modify_db_value(grps, chat_id, "rep", 0, "$set", giving_user_id)

    receiving_user_doc = await find_one_doc(grps, { "$and": [{"_id": chat_id}, \
                               {"users.user_id": receiving_user_id}] }, {"users.rep.$":1})
    # Get the last value in the list (an array), 
    # then the only element in that array (a dictionary),
    # and lastly get the value of the "rep" key in the dictionary
    giving_user_rep = list(giving_user_doc.values())[-1][0]["rep"]
    receiving_user_rep = list(receiving_user_doc.values())[-1][0]["rep"]

    return [giving_user_rep, receiving_user_rep]


async def choose_rep_change_msg(chat_id, dec=False):
    rep_change_msg = ""
    group_rep_msg = await get_group_rep_msg(chat_id, dec)
    if (dec):
        if not group_rep_msg:
            # Default decrease message
            rep_change_msg = ("{usuario_da} ({rep_usuario_da}) ha "
                              "decrementado la reputación de {usuario_recibe} en "
                              "{cambio_rep} puntos. La nueva reputación de "
                              "{usuario_recibe} es de: {rep_usuario_recibe}.")
        else:
            rep_change_msg = group_rep_msg.get("rep_dec_msg")
    else:
        if not group_rep_msg:
            # Default increase message
            rep_change_msg = ("{usuario_da} ({rep_usuario_da}) ha "
                              "incrementado la reputación de {usuario_recibe} en "
                              "{cambio_rep} puntos. La nueva reputación de "
                              "{usuario_recibe} es de: {rep_usuario_recibe}.")
        else:
            rep_change_msg = group_rep_msg.get("rep_inc_msg")
    return rep_change_msg


async def toggle_group_rep_msg(chat_id):
    filter = "rep_msg_enabled"
    enabled = await get_group_rep_msg_enabled(chat_id)
    await modify_db_value(grps, chat_id, filter, not enabled, "$set")


async def get_group_rep_msg_enabled(chat_id):
    filter = "rep_msg_enabled"
    enabled = await find_one_doc(grps, { "_id": chat_id, filter: { "$exists": True } }, { filter: 1 })
    if not enabled:
        await modify_db_value(grps, chat_id, filter, True, "$set")
        return True
    return enabled[filter]


async def get_group_rep_msg(chat_id, dec=False):
    filter = "rep_inc_msg"
    if (dec):
        filter = "rep_dec_msg"
    return await find_one_doc(grps, { "_id": chat_id, filter: { "$exists": True } }, { filter: 1 })


async def set_group_rep_msg(chat_id, msg, dec=False):
    field = "rep_inc_msg"
    if (dec):
        field = "rep_dec_msg"
    await modify_db_value(grps, chat_id, field, msg, "$set")


async def store_rep(chat_id, user_id, rep_change):
    await modify_db_value(grps, chat_id, "rep", rep_change, "$inc", user_id)

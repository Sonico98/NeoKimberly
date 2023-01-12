from db.generic import *
from db.mongodb import db

# Collection
grps = db.groups


async def get_reps(chat_id, giving_user_id, receiving_user_id):
    # The user giving rep is probably not on the DB yet
    giving_user_doc = {}
    while (giving_user_doc == {}):
        giving_user_doc = await find_one_doc(grps, { "$and": [{"group": chat_id}, \
                                 {"users.user_id": giving_user_id}] }, {"users.rep.$":1})

        if (giving_user_doc == {}):
            await insert_doc(grps, { "group": chat_id, "users": \
                                 [ { "user_id": giving_user_id, "rep": 0} ] })


    receiving_user_doc = await find_one_doc(grps, { "$and": [{"group": chat_id}, \
                                 {"users.user_id": receiving_user_id}] }, {"users.rep.$":1})

    # Get the last value in the list (an array), 
    # then the only element in that array (a dictionary),
    # and lastly get the value of the "rep" key in the dictionary
    giving_user_rep = list(giving_user_doc.values())[-1][0]["rep"]
    receiving_user_rep = list(receiving_user_doc.values())[-1][0]["rep"]

    return [giving_user_rep, receiving_user_rep]


async def store_rep(chat_id, user_id, rep_change):
    existing_group_doc = await find_one_doc(grps, {"group": chat_id})
    if (len(existing_group_doc) > 0):
        matching_doc = {"group": chat_id, "users.user_id": user_id}
        # Try to update an existing user's rep
        result = await update_doc(grps, matching_doc, {"$inc": {"users.$.rep": rep_change}})
        # If the user is not yet present in the group's user array, add it
        if (repr(result.modified_count) == "0"):
            res = await update_doc(grps, {"group": chat_id}, {"$push": {"users": {"user_id": user_id, "rep": rep_change}}})
    else:
        await insert_doc(grps, { "group": chat_id, "users": [ { "user_id": user_id, "rep": rep_change } ] })

from db.generic import *
from db.mongodb import db

# Collection
grps = db.groups


async def get_all_reps_and_ids(chat_id):
    user_rep_list = await find_one_doc(grps, {"group": chat_id}, {"_id": 0, "users":1})
    if (user_rep_list != {}):
        users_array = user_rep_list["users"]
        user_rep_list = []
        for u in users_array:
            user_rep_list.append([u["rep"], u["user_id"]])

    return sorted(user_rep_list, reverse=True)


async def get_user_reps(chat_id, giving_user_id, receiving_user_id):
    # The user giving rep is probably not on the DB yet
    giving_user_doc = {}
    while (giving_user_doc == {}):
        giving_user_doc = await find_one_doc(grps, { "$and": [{"group": chat_id}, \
                               {"users.user_id": giving_user_id}] }, {"users.rep.$":1})
        if (giving_user_doc == {}):
            await update_doc(grps, {"group": chat_id}, {"$push": {"users": \
                               {"user_id": giving_user_id, "rep": 0}}})

    receiving_user_doc = await find_one_doc(grps, { "$and": [{"group": chat_id}, \
                               {"users.user_id": receiving_user_id}] }, {"users.rep.$":1})
    # Get the last value in the list (an array), 
    # then the only element in that array (a dictionary),
    # and lastly get the value of the "rep" key in the dictionary
    giving_user_rep = list(giving_user_doc.values())[-1][0]["rep"]
    receiving_user_rep = list(receiving_user_doc.values())[-1][0]["rep"]

    return [giving_user_rep, receiving_user_rep]


async def store_rep(chat_id, user_id, rep_change):
    await store_user_value(grps, chat_id, user_id, "rep", rep_change)

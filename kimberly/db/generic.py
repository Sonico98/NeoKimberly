from utils import generic_messages as gm


error_result = {
    "acknowledged": "Error",
    "inserted_id": "Error",
    "matched_count": "Error",
    "modified_count": "Error",
    "upserted_count": "Error"
}


async def find_one_doc(collection, data: dict, parameter: dict = {}):
    try:
        doc = await collection.find_one(data, parameter)
        if doc is not None:
            return doc
    except:
        print(gm.db_error_message)

    return {}


async def find_docs(collection, key: dict):
    try:
        cursor = collection.find(key)
        docs = cursor.to_list(length=1000)
        if docs is not None:
            return docs
    except:
        print(gm.db_error_message)
    return []


async def insert_doc(collection, new_doc):
    try:
        result = await collection.insert_one(new_doc)
    except:
        print(gm.db_error_message)
        result = error_result
    return result


async def replace_doc(collection, old_doc: dict, new_data: dict):
    try:
        _id = old_doc['_id']
        result = await collection.replace_one({'_id': _id}, new_data)
    except:
        print(gm.db_error_message)
        result = error_result
    return result


async def update_doc(collection, match_condition: dict, new_data: dict):
    try:
        result = await collection.update_one(match_condition, new_data)
    except:
        print(gm.db_error_message)
        result = error_result
    return result


async def store_user_value(collection, chat_id, user_id, field, value):
    existing_group_doc = await find_one_doc(collection, {"group": chat_id})
    if (len(existing_group_doc) > 0):
        matching_doc = {"group": chat_id, "users.user_id": user_id}
        # Try to update an existing user's field
        result = await update_doc(collection, matching_doc, {"$inc": {f"users.$.{field}": value}})
        # If the user is not yet present in the group's user array, add it
        if (repr(result.modified_count) == "0"):
            await update_doc(collection, {"group": chat_id}, \
                            {"$push": {"users": {"user_id": user_id, f"{field}": value}}})
    else:
        await insert_doc(collection, { "group": chat_id, "users": \
                               [ { "user_id": user_id, f"{field}": value } ] })

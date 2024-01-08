from utils import generic_messages as gm
from db.mongodb import db


grps = db.groups
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


async def find_docs(collection, match_condition: dict, parameter: dict = {}):
    try:
        cursor = collection.find(match_condition, parameter)
        docs = await cursor.to_list(length=1000)
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
    except Exception as e:
        # print(gm.db_error_message)
        result = error_result
        # print(e)
    return result


async def modify_db_value(collection, chat_id, field, value, operation, user_id=None):
    existing_group_doc = await find_one_doc(collection, {"_id": chat_id})
    if (len(existing_group_doc) > 0):
        field_prefix = ""
        matching_doc = {"_id": chat_id}
        if (user_id is not None):
            matching_doc = {"_id": chat_id, "users.user_id": user_id}
            field_prefix = "users.$."
        # Try to update an existing group's field
        result = await update_doc(collection, matching_doc, { operation: { f"{field_prefix}{field}": value } } )
        # If the property is not yet present in the group, add it
        if (repr(result.modified_count) == "0"):
            push_operation = { "$push": { field: value } }
            if (user_id is not None):
                push_operation = { "$push": { "users": { "user_id": user_id, f"{field}": value } } }
            await update_doc(collection, {"_id": chat_id}, push_operation)
    else:
        insert_operation = { "_id": chat_id, field: value }
        if (user_id is not None):
            insert_operation = { "_id": chat_id, "users": \
                               [ { "user_id": user_id, f"{field}": value } ] }

        await insert_doc(collection, insert_operation)


async def get_user_ids_with_value(chat_id, value):
    complete_users_list = await find_one_doc(grps, {"_id": chat_id}, {"users":1})
    if (complete_users_list != {}):
        users_list = complete_users_list["users"]
        complete_users_list = []
        for u in users_list:
            try:
                complete_users_list.append([u[value], u["user_id"]])
            except KeyError:
                pass

    return sorted(complete_users_list, reverse=True)


async def get_doc_id(query: dict):
    doc = await find_one_doc(grps, query, { "_id": 1 })
    if (len(doc) > 0):
        doc_id = doc.get("id")
        return doc_id
    return -1

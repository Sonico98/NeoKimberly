from db.mongodb import db


async def find_one_doc(collection, data: dict):
    doc = await collection.find_one(data)
    if doc is not None:
        return doc
    return {}


async def find_docs(collection, key: dict):
    cursor = collection.find(key)
    docs = cursor.to_list(length=1000)
    if docs is not None:
        return docs
    return []


async def replace_doc(collection, old_doc: dict, new_data: dict):
    _id = old_doc['_id']
    await collection.replace_one({'_id': _id}, new_data)

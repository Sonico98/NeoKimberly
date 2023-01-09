from pyrogram import filters
from neokimberly import kimberly

def trinsfirmir(message):
    vocalesmin = "aeouäëöüâêôûàèòù"
    vocalesmax = "AEOUÄËÖÜÂÊÔÛÀÈÒÙ"
    vocalmintil = "áéóú"
    vocalmaxtil = "ÁÉÓÚ"
    if (message.reply_to_message is None):
        texto = "Respondele a algo que tenga texto."
        return texto
    
    string = (message.reply_to_message.text)
    for x in range(len(vocalesmin)):
        string = string.replace(vocalesmin[x],"i").replace(vocalesmax[x],"I")
    for x in range(len(vocalmintil)):
        string = string.replace(vocalmintil[x],"í").replace(vocalmaxtil[x],"Í")
    return string
       
@kimberly.on_message(filters.command("trinsfirmir"))
async def reply(client, message):
    answer = trinsfirmir(message)
    sticker = "CAACAgIAAxkBAAEb0vBjvEJxq6StpCBzN4eeZ0-xaap6IQACQQEAAksODwABJlVW31Lsf6stBA"
    try:
        await message.reply_text(answer, reply_to_message_id=message.reply_to_message.id, quote=True)
        await message.reply_sticker(sticker, disable_notification=True, quote=False)
    except:
        await message.reply_text(answer, quote=True)

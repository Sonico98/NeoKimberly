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
    await message.reply_text(answer, quote=True)


from pyrogram import filters
from neokimberly import kimberly

def trinsfirmir(message):
    vocalesmin = "aeouäëöüâêôûàèòù"
    vocalesmax = "AEOUÄËÖÜÂÊÔÛÀÈÒÙ"
    vocalmintil = "áéóú"
    vocalmaxtil = "ÁÉÓÚ"
    if len(message.reply_to_message.text) == "":
        print(len(message.reply_to_message.text))
        texto = "Respondele a algo que tenga texto."
        # @kimberly.send_message(message.chat.id, texto)
        return texto
    else:
        string = (message.reply_to_message.text)
        for x in range(len(vocalesmin)):
            string = string.replace(vocalesmin[x],"i")
        for x in range(len(vocalesmax)):            
            string = string.replace(vocalesmax[x],"I")
        for x in range(len(vocalmintil)):            
            string = string.replace(vocalmintil[x],"í")
        for x in range(len(vocalmaxtil)):            
            string = string.replace(vocalmaxtil[x],"Í")
    return string
       
@kimberly.on_message(filters.regex("^/trinsfirmir$"))
async def reply(client, message):
    answer = trinsfirmir(message)
    await message.reply_text(answer, quote=False)
    
    # (\)

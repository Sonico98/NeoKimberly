from pyrogram import filters
from neokimberly import kimberly
from pyrogram import Client

def trinsfirmir(message):
    "poner condicional de respuesta a texto. ver"
    for i in range(len(message)):
        if message[i] == "aeouäëöüâêôûàèòù":
            message[i] = "i"
        elif message[i] == "AEOUÄËÖÜÂÊÔÛÀÈÒÙ":
            message[i] = "I"
        elif message[i] == "áéóú":
            message[i] = "í"
        elif message[i] == "ÁÉÓÚ":
            message[i] = "Í"
    return message


@kimberly.on_message(filters.command(["Trinsfirmir"]))
async def reply(client, message):
    answer = trinsfirmir(message)
    await message.reply_text(answer, quote=False)
    print("Me falta el sticker lmao.")

    # (\)

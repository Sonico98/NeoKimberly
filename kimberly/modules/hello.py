from pyrogram import filters
from neokimberly import kimberly
import random

regex_salute = "\\bhola\\b|\\bholi(s)?\\b|\\baló\\b|\\bola\\b|(bu|w)enas|\\bbuenos\\sd(i|í)as\\b"
regex_gn = "\\bbuenas noches\\b|\\bhasta mañana\\b|\\bgn\\b|\\boyasumi\\b|\\bkonbanwa\\b|\\bgood night\\b"
salute_answers = ['Hola ', 'Hola a todos, menos a ', 'Saludos, ']
gn_answers = ['Buenas noches ', 'Tengan todos una buena noche, excepto ']


def build_reply(message, answer):
    user = message.from_user.first_name
    answer = random.choice(answer) + user
    return answer


@kimberly.on_message(filters.group & filters.regex(regex_salute))
@kimberly.on_edited_message(filters.group & filters.regex(regex_salute))
async def hello(client, message):
    answer = build_reply(message, salute_answers)
    await message.reply_text(answer, quote=False)


@kimberly.on_message(filters.group & filters.regex(regex_gn))
@kimberly.on_edited_message(filters.group & filters.regex(regex_gn))
async def night(client, message):
    answer = build_reply(message, gn_answers)
    await message.reply_text(answer, quote=False)

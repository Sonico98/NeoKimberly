import random
from pyrogram import filters
from neokimberly import kimberly


regex_salute = "(?i)\\bhola\\b|" + \
               "\\bholi(s)?\\b|" + \
               "\\baló\\b|" + \
               "\\bola\\b|" + \
               "^(muy)?(bu|w)enas(\\s)?(a\\stod(a|o)s|gente|chic(a|o)s|amig(a|o)s)?$|" + \
               "\\bbuenos\\sd(i|í)as\\b"

regex_gn = "(?i)\\bbuenas noches\\b|" + \
           "^hasta mañana(\\s)?(gente|chic(a|o)s|amig(a|o)s)?$|" + \
           "\\bgn\\b|" + \
           "\\boyasumi\\b|" + \
           "\\bkonbanwa\\b|" + \
           "\\bgood night\\b"

salute_answers = ['Hola ', 'Hola a todos, menos a ', 'Saludos, ']
gn_answers = ['Buenas noches ', 'Tengan todos una buena noche, excepto ']


def build_reply(message, answer):
    user = message.from_user.first_name
    answer = random.choice(answer) + user
    return answer


@kimberly.on_message(filters.group & filters.regex(regex_salute))
@kimberly.on_edited_message(filters.group & filters.regex(regex_salute))
async def hello(_, message):
    answer = build_reply(message, salute_answers)
    await message.reply_text(answer, quote=False)


@kimberly.on_message(filters.group & filters.regex(regex_gn))
@kimberly.on_edited_message(filters.group & filters.regex(regex_gn))
async def night(_, message):
    answer = build_reply(message, gn_answers)
    await message.reply_text(answer, quote=False)

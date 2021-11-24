import telebot
import math
from get_position import *

bot = telebot.TeleBot("2102905381:AAHbjtUofTgIvm0muTYZbbcTkeVSQlI5es4")


@bot.message_handler(commands=["start"])  # Хендлер на команду start
def start_message(message):
    tg_analytic.statistics(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Узнайте, на каком месте находиться ваш товар в поисковой выдачи на Wildberries.\nДля этого нужно ввести артикул и интересующий вас запрос.\nНапример: 43915761 контейнер для линз")


@bot.message_handler(content_types=["text"])
def message_handler(message):
    tg_analytic.statistics(message.chat.id, message.text)
    data = str(message.text).split(" ")
    if len(data) > 1 and data[0].isnumeric():
        id = data[0]
        key = str(message.text).replace(id,"")
        msg = "🔎 Поиск запущен.. артикул и запрос проверяется в полной версии сайта первые 20 страниц."
        bot.send_message(message.chat.id,
                         msg)
        res = get_keyword_position(1000, key,id)
        if res is None:
            res = "Артикул "+id+" по запросу '"+key+"' на первых 20 страницах не обнаружен"
        else:
            res = "Артикул находится на позиции "+str(res)+" на странице "+str(math.ceil(res/50))
        bot.send_message(message.chat.id,
                         res)

    else:
        bot.send_message(message.chat.id,
                         "Запрос введен в неправильном формате или содержит ошибки. .\nВведите запрос в формате: 43915761 контейнер для линз")


bot.polling(none_stop=True, interval=0)
import telebot
import math
from new_wb_bot import *

region_list = "Выберете один или несколько городов из списка и ввелит их номера через пробел\n"
for n, key in enumerate(list(regions.keys())):
    region_list += f"{n+1}. {key}\n"
bot = telebot.TeleBot("2102905381:AAHbjtUofTgIvm0muTYZbbcTkeVSQlI5es4")
user_data = dict()


@bot.message_handler(commands=["start"])  # Хендлер на команду start
def start_message(message):
    # tg_analytic.statistics(message.chat.id, message.text)
    bot.send_message(message.chat.id, "Узнайте, на каком месте находиться ваш товар в поисковой выдачи на "
                                      "Wildberries.\nДля этого нужно выбрать регион поиска c помощью команды /region "
                                      "и ввести артикул и интересующий Вас запрос поиска.\nНапример: 43915761 "
                                      "контейнер для линз, линзы")
    if message.chat.id not in user_data.keys():
        user_data[message.chat.id] = ["request", set()]


@bot.message_handler(commands=["region"])
def select_region(message):
    bot.send_message(message.chat.id, region_list)
    user_data[message.chat.id] = ["region", set()]


@bot.message_handler(content_types=["text"])
def message_handler(message):
    # tg_analytic.statistics(message.chat.id, message.text)
    if message.chat.id in user_data.keys():

        start_message(message)
    elif user_data[message.chat.id][0] == "region":
        try:
            user_n_regions = set(map(int, message.text.split()))
            user_regions = set(list(regions.keys())[user_n_region-1] for user_n_region in user_n_regions)
            user_data[message.chat.id] = ["request", user_regions]
            bot.send_message(message.chat.id, "Поиск будет производиться по следущим городам: "
                                              f"{', '.join(list(user_regions))}, введите ваш запрос в формате: 3915761 "
                                              "контейнер для линз, линзы. Максимум за один раз может быть 5 запрсов "
                                              "поиска")
        except:
            bot.send_message(message.chat.id, "В вашем запросе ошибка, повторите запрос")
    elif user_data[message.chat.id][0] == "request":
        data = str(message.text)
        ldata = data.split()
        if len(ldata) > 1 and ldata[0].isnumeric():
            id = int(ldata[0])
            data = data.replace(str(id), '')[1:]
            keys = data.split(", ")
            if len(keys) > 5:
                bot.send_message(message.chat.id, "Вы ввели более 5 запросов поиска, введите заппрос заново.")
            else:
                msg = "🔎 Поиск запущен.. артикул и запрос проверяется в полной версии сайта первые 20 страниц."
                bot.send_message(message.chat.id, msg)
                user_data[message.chat.id][0] = "pending"
                for key in keys:
                    msg = f"{key}\n"
                    for region in [1,2,3,5,7]:#user_data[message.chat.id][1]:

                        res = get_vendor_pos(id, region, key, 20)
                        if not res:
                            msg += f"{region} - на первых 20 страниах не найден\n"
                        elif type(res) == str:
                            msg += f"{region} - {res}\n"
                        else:
                            msg += f"{region} - позиция {res} страница {math.ceil(res / 50)}\n"
                    bot.send_message(message.chat.id, msg)
                user_data[message.chat.id][0] = "request"
        else:
            bot.send_message(message.chat.id,
                             "Запрос введен в неправильном формате или содержит ошибки. .\nВведите запрос в формате: "
                             "43915761 контейнер для линз, линзы")
    elif user_data[message.chat.id][0] == "pending":
        bot.send_message(message.chat.id, "Ваш запрос уже обрабатывается, дождитесь завершения обработки запроса")


bot.polling(none_stop=True, interval=0)

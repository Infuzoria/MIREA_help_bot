from part_with_parser import parser
import telebot
from telebot import types
from db import BotDB
from url import URLS
from parser_for_contest_lists import general_paser
from parser_for_targeted_and_separate import parser_targeted_and_separate
from parser_contract import parser_contract
from parser_time import parser_time
from parser_places import parser_places
import re

API_KEY = '6137871025:AAFUh6ZxKtSzAZYhviA-_JuYSUb-iNjrop4'
NUMBERS = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']

bot = telebot.TeleBot(API_KEY)
user = BotDB('accountant.db')

# Добавить СНИЛС
def add_snils(message):
    find_snils = re.findall(r"\d{3}-\d{3}-\d{3}-\d{2}", message.text)
    if len(find_snils) != 0:
        check_position = BotDB.get_snils(user, message.from_user.id)
        if check_position == "NULL":
            BotDB.add_snils(user, message.from_user.id, find_snils[0])
            bot.send_message(message.chat.id, "СНИЛС успешно добавлен")
        else:
            BotDB.add_snils(user, message.from_user.id, find_snils[0])
            bot.send_message(message.chat.id, "СНИЛС успешно обновлен")
    else:
        bot.send_message(message.chat.id, "СНИЛС введен некорректно, попробуйте ещё раз")

# Добавить ссылку
def add_url(message):
    find_record = re.findall(r"(https?://[\S]+)", message.text)
    if len(find_record) != 0:
        result = BotDB.get_records(user, message.from_user.id)
        for i in result:
            if i == find_record[0]:
                bot.send_message(message.chat.id, "Такая ссылка уже есть")
                return True
        BotDB.add_record(user, message.from_user.id, find_record[0])
        bot.send_message(message.chat.id, "Ссылка успешно добавлена")
    else:
        bot.send_message(message.chat.id, "Ссылка введена некорректно, попробуйте ещё раз")

def check_list(message):
    if all([x.isdigit() for x in message.text]):
        number = int(message.text)
        count = BotDB.count_of_records(user, message.from_user.id)
        if 1 <= number <= count:
            result = BotDB.get_records(user, message.from_user.id)
            url = result[number - 1]

            # Разбиваем на части и выводим список по 10 позиций
            table = parser(str(url))
            for i in range(len(table) // 10):
                if i == 0:
                    text = "Конкурсный список:"
                else:
                    text = ""
                for row in range(i * 10, i * 10 + 10):
                    for key, val in table[row].items():
                        text += f'\n{key}: {val}'
                    text += '\n---------------------------'
                bot.send_message(message.chat.id, text)

            # Выводим оставшиеся записи
            text = ""
            for i in range((len(table) // 10) * 10, len(table)):
                for key, val in table[i].items():
                    text += f'\n{key}: {val}'
                text += '\n---------------------------'
            if text != "":
                bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, "Такого номера нет в списке, попробуйте ввести значение ещё раз")
    else:
        bot.send_message(message.chat.id, "Номер введен некорректно, попробуйте ещё раз")

def get_id(message):
    id = re.findall(r"\d{2}.\d{2}.\d{2}", message.text)

    if id == []:
        bot.send_message(message.chat.id, "Номер указан некорректно, попробуйте ещё раз.")
    else:
        id = id[0]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Общий конкурс")
        btn2 = types.KeyboardButton("Без вступительных испытаний")
        btn3 = types.KeyboardButton("Квота для особых прав")
        btn4 = types.KeyboardButton("Целевое обучение")
        btn5 = types.KeyboardButton("Отдельная квота")
        btn6 = types.KeyboardButton("Платные места")
        btn7 = types.KeyboardButton("Прием иностранцев")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2)
        markup.add(btn3, btn4)
        markup.add(btn5, btn6)
        markup.add(btn7, back)

        bot.send_message(message.chat.id, "Укажите основание отбора. Для этого нажмите на соответствующую кнопку.", reply_markup=markup)
        bot.register_next_step_handler(message, check_position, id)

def check_position(message, id):
    for key, value in URLS.items():
        if key == id:
            for k, v in value.items():
                if k == message.text:
                    url = v

    if url == "-":
        bot.send_message(message.chat.id, "К сожалению, списка по выбранному направлению нет. Убедитесь в правильности ввода.")
        return True
    else:
        bot.send_message(message.chat.id, "Пару секунд, идет обработка информации")
        snils = BotDB.get_snils(user, message.from_user.id)
        time = parser_time(url)
        places = parser_places(url)

        if message.text == "Общий конкурс" or message.text == "Без вступительных испытаний":
            table = general_paser(url)

            for row in table:
                if row["СНИЛС/уникальный номер"] == snils:
                    text = f"Ваш порядковый номер: {row['№']}"
                    if places != "-":
                        text += f"\nВсего мест: {places}"
                    text += f"\n{time}"
                    text += '\n---------------------------------------------------------'
                    text += f"\nСНИЛС/уникальный номер: {row['СНИЛС/уникальный номер']}"
                    text += f"\nПриоритет: {row['Приоритет']}"
                    text += f"\nВП Все: {row['ВП Все']}"
                    text += f"\nВП по оригиналам: {row['ВП по оригиналам']}"
                    text += f"\nНаличие подлинника: {row['Наличие подлинника']}"
                    text += f"\nПотребность в общежитии: {row['Потребность в общежитии']}"
                    text += f"\nСумма баллов за ВИ: {row['Сумма баллов за ВИ']}"
                    text += f"\nБалл за ИД: {row['Балл за ИД']}"
                    text += f"\nСумма баллов: {row['Сумма баллов']}"
                    if message.text == "Общий конкурс":
                        text += f"\nУчастие в грантовой программе: {row['Участие в грантовой программе']}"
                    text += f"\nПримечание: {row['Примечание']}"
                    if places != "-":
                        text += '\n---------------------------------------------------------'
                        text += f"\n❗ Обратите внимание на количество мест. Учитывайте, что не все абитуриенты, находящиеся " \
                                f"в списке выше вас, предоставили подленник аттестата. \nДля того, чтобы увидеть " \
                                f"отсортированный список, выберете функцию 'Посмотреть список' или " \
                                f"перейдите по ссылке: \n{url}"
                    bot.send_message(message.chat.id, text)
                    return True

            bot.send_message(message.chat.id, "Кажется, вас нет в этом списке. Проверьте введенный СНИЛС и номер выбранного направления")


def check_positio(message):
    if all([x.isdigit() for x in message.text]):
        number = int(message.text)
        count = BotDB.count_of_records(user, message.from_user.id)

        if 1 <= number <= count:
            snils = BotDB.get_snils(user, message.from_user.id)
            result = BotDB.get_records(user, message.from_user.id)
            url = result[number - 1]
            table = parser(str(url))

            for row in table:
                if row['ID'] == snils:
                    text = f"Ваш порядковый номер: {row['№']}"
                    text += '\n---------------------------'
                    text += f"\nID: {row['ID']}"
                    text += f"\nРус. язык: {row['Рус. язык']}"
                    text += f"\nМатематика(профиль): {row['Математика(профиль)']}"
                    text += f"\nИнформатика и ИКТ: {row['Информатика и ИКТ']}"
                    text += f"\nДоп. баллы: {row['Доп. баллы']}"
                    text += f"\nСумма баллов: {row['Сумма баллов']}"
                    text += f"\nСогласие на зачисление: {row['Согласие на зачисление']}"
                    bot.send_message(message.chat.id, text)
                    return True
            bot.send_message(message.chat.id, "Кажется, вас нет в этом списке. Проверьте введенный номер СНИЛС и номер выбранного списка")

        else:
            bot.send_message(message.chat.id, "Такого номера нет в списке, попробуйте ввести значение ещё раз")
    else:
        bot.send_message(message.chat.id, "Номер введен некорректно, попробуйте ещё раз")

def check_by_number(message):
    request = message.text.split()

    if all([x.isdigit() for x in request[0]]):
        number = int(request[0])
        count = BotDB.count_of_records(user, message.from_user.id)

        if 1 <= number <= count:
            if all([x.isdigit() for x in request[1]]):
                result = BotDB.get_records(user, message.from_user.id)
                url = result[number - 1]
                table = parser(str(url))
                text = ""

                if 1 <= int(request[1]) <= len(table):
                    for row in table:
                        if row['№'] == request[1]:
                            text += '\n---------------------------'
                            text += f"\n№: {row['№']}"
                            text += f"\nID: {row['ID']}"
                            text += f"\nРус. язык: {row['Рус. язык']}"
                            text += f"\nМатематика(профиль): {row['Математика(профиль)']}"
                            text += f"\nИнформатика и ИКТ: {row['Информатика и ИКТ']}"
                            text += f"\nДоп. баллы: {row['Доп. баллы']}"
                            text += f"\nСумма баллов: {row['Сумма баллов']}"
                            text += f"\nСогласие на зачисление: {row['Согласие на зачисление']}"
                            text += '\n---------------------------'
                            bot.send_message(message.chat.id, text)
                else:
                    bot.send_message(message.chat.id, "Такого номера нет в списке, проверьте введенные данные")
            else:
                bot.send_message(message.chat.id, "Номер строки введен некорректно, попробуйте ещё раз")
        else:
            bot.send_message(message.chat.id, "Такого номера нет в списке, попробуйте ввести значение ещё раз")
    else:
        bot.send_message(message.chat.id, "Номер списка введен некорректно, попробуйте ещё раз")

def statistics(message, year, form):
    bot.send_message(message.chat.id, "Пару секунд")

    if year == "2013":
        ids = set(re.findall(r"\d{6}.\d{2}", message.text))
    else:
        ids = set(re.findall(r"\d{2}.\d{2}.\d{2}", message.text))

    if len(ids) == 0:
        bot.send_message(message.chat.id, "Номера указаны некорректно, попробуйте ещё раз.")
    else:
        url = f'https://priem.mirea.ru/first-degree/selection/{year}'
        if form == 'Очная форма обучения':
            table = parser(url)[0]

            for id in ids:
                counter = 0
                for row in table:
                    if row['Шифр'] == id:
                        text = ''
                        index = 0
                        for key, val in row.items():
                            text += f'{NUMBERS[index]} {key}: {val}\n'
                            index += 1
                        bot.send_message(message.chat.id, text)
                    else:
                        counter += 1

                if counter == len(table):
                    bot.send_message(message.chat.id, f"{id} - не найден")

            bot.send_message(message.chat.id, f"Полный список можно увидеть на сайте: {url}")

        elif form == 'Очно-заочная форма обучения':
            table = parser(url)[1]

            for id in ids:
                counter = 0
                for row in table:
                    if row['Шифр'] == id:
                        text = ''
                        for key, val in row.items():
                            text += f'{key}: {val}\n'
                        bot.send_message(message.chat.id, text)
                    else:
                        counter += 1

                if counter == len(table):
                    bot.send_message(message.chat.id, f"{id} - не найден")

            bot.send_message(message.chat.id, f"Полный список можно увидеть на сайте: {url}")

        elif form == 'Заочная форма обучения':
            table = parser(url)[2]

            for id in ids:
                counter = 0
                for row in table:
                    if row['Шифр'] == id:
                        text = ''
                        for key, val in row.items():
                            text += f'{key}: {val}\n'
                        bot.send_message(message.chat.id, text)
                    else:
                        counter += 1

                if counter == len(table):
                    bot.send_message(message.chat.id, f"{id} - не найден")

            bot.send_message(message.chat.id, f"Полный список можно увидеть на сайте: {url}")


def number_request(message, year):
    if message.text in ['Вернуться к выбору года', 'Вернуться в главное меню']:
        func(message)
    else:
        form = message.text
        if year == '2013':
            bot.send_message(message.chat.id, "Через пробел укажите все номера интересующих направлений.\n"
                                              "Пример ввода: 200400.62 030900.62 080200.62")
        else:
            bot.send_message(message.chat.id, "Через пробел укажите все номера интересующих направлений.\n"
                                              "Пример ввода: 09.03.01 09.03.02 09.03.03")
        bot.register_next_step_handler(message, statistics, year, form)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Добавление клавиатуры с кнопками
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🪪 СНИЛС")
    btn2 = types.KeyboardButton("🌐 Cсылки")
    btn3 = types.KeyboardButton("📊 Текущий конкурс")
    btn4 = types.KeyboardButton("📚 Статистика прошлых лет")
    markup.add(btn1, btn2, btn3, btn4)

    # Описание команды start
    if (message.text == '/start'):
        if (not BotDB.user_exists(user, message.from_user.id)):
            BotDB.add_user(user, message.from_user.id)
            bot.send_message(message.chat.id, "Добро пожаловать! Этот бот призван упростить жизнь абитуриента, "
                                              "с его помощью можно легко следить за ходом приемной компании."
                                              "\n\nЧто умеет бот:"
                                              "\n\n/start - информация о командах бота"
                                              "\n\n🪪 *СНИЛС* - добавить или изменить СНИЛС. Страховой номер понадобится вам"
                                              "для просмотра конкурсных списков. Статистику прошлых лет можно посмотреть без"
                                              "СНИЛСа."
                                              "\n\n🌐 *Cсылки* - просмотр полезных ссылок"
                                              "\n\n📊 *Текущий конкурс* - раздел с информацией по текущему конкурсу. Нажмите на эту кнопку,"
                                              "чтобы посмотреть конкурсные списки по интересующим направлениям и проверить свою "
                                              "позицию в рейтинге."
                                              "\n\n📚 *Статистика прошлых лет* - раздел с информацией о приемной компании прошлых лет."
                                              "Нажмите на эту кнопку, чтобы посмотреть проходные баллы за прошлые года.",
                                              reply_markup=markup, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "С возвращением!"
                                              "\n\nСписок команд:"
                                              "\n\n/start - информация о командах бота"
                                              "\n\n🪪 *СНИЛС* - добавить или изменить СНИЛС. Страховой номер понадобится вам"
                                              "для просмотра конкурсных списков. Статистику прошлых лет можно посмотреть без"
                                              "СНИЛСа."
                                              "\n\n🌐 *Cсылки* - просмотр полезных ссылок"
                                              "\n\n📊 *Текущий конкурс* - раздел с информацией по текущему конкурсу. Нажмите на эту кнопку,"
                                              "чтобы посмотреть конкурсные списки по интересующим направлениям и проверить свою "
                                              "позицию в рейтинге."
                                              "\n\n📚 *Статистика прошлых лет* - раздел с информацией о приемной компании прошлых лет."
                                              "Нажмите на эту кнопку, чтобы посмотреть проходные баллы за прошлые года.",
                                              reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "/get_snils"):
        bot.send_message(message.chat.id, BotDB.get_snils(user, message.from_user.id))

    elif(message.text == "🪪 СНИЛС"):
        bot.send_message(message.chat.id, "Отправьте свой снился в формате: 200-650-900-42")
        bot.register_next_step_handler(message, add_snils)

    elif(message.text == "🔗 Добавить ссылку"):
        bot.send_message(message.chat.id, "Введите ссылку на страницу с конкурсным списком")
        bot.register_next_step_handler(message, add_url)

    elif(message.text == "💻 Просмотр всех ссылок"):
        result = BotDB.get_records(user, message.from_user.id)
        if len(result) != 0:
            text = "Список введенных ссылок:"
            for index, url in enumerate(result):
                text += f'\n{index+1}. {url}'
            bot.send_message(message.chat.id, text)
        else:
            bot.send_message(message.chat.id, "Вы не добавили ни одной ссылки")

    elif(message.text == "📍 Проверить позицию"):
        bot.send_message(message.chat.id, "Введите номер интересующего направления. Пример ввода: 09.03.01.")
        bot.register_next_step_handler(message, get_id)

    elif(message.text == "📑 Посмотреть список"):
        bot.send_message(message.chat.id, "Введите порядковый номер url из списка ваших добавленных ссылок. "
                                          "Для того, чтобы посмотреть список ссылок, используйте команду: 💻 Просмотр всех ссылок")
        bot.register_next_step_handler(message, check_list)

    elif(message.text == "🔎 Поиск по номеру"):
        bot.send_message(message.chat.id, "Введите порядковый номер списка, в котором желаете посмотреть информацию. "
                                          "Через пробел укажите порядковый номер записи в списке. "
                                          "Для того, чтобы посмотреть список ссылок, используйте команду: 💻 Просмотр всех ссылок")
        bot.register_next_step_handler(message, check_by_number)

    elif (message.text == "📊 Текущий конкурс"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("⚙ Помощь")
        btn2 = types.KeyboardButton("📍 Проверить позицию")
        btn3 = types.KeyboardButton("📑 Посмотреть список")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2)
        markup.add(btn3, back)

        bot.send_message(message.chat.id, "Для того, чтобы подробнее узнать о функционале, "
                                          "нажмите на кнопку '*Помощь*'.", reply_markup=markup, parse_mode="Markdown")

    elif (message.text == "⚙ Помощь"):
        bot.send_message(message.chat.id, "Для того, чтобы посмотреть конкурсные списки или узнать свою позицию в рейтинге, "
                                          "нажмите на соответствующую кнопку, введите номер направления и укажите основание отбора."
                                          "\n\n📍 *Проверить позицию* - проверить свою позицию в списке."
                                          "\n\n📑 *Посмотреть список* - просмотр конкурсного списка.", parse_mode="Markdown")

    elif (message.text == "📚 Статистика прошлых лет" or message.text == "Вернуться к выбору года"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("2022")
        btn2 = types.KeyboardButton("2021")
        btn3 = types.KeyboardButton("2020")
        btn4 = types.KeyboardButton("2019")
        btn5 = types.KeyboardButton("2018")
        btn6 = types.KeyboardButton("2017")
        btn7 = types.KeyboardButton("2016")
        btn8 = types.KeyboardButton("2015")
        btn9 = types.KeyboardButton("2014")
        btn10 = types.KeyboardButton("2013")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3)
        markup.add(btn4, btn5, btn6)
        markup.add(btn7, btn8, btn9)
        markup.add(btn10, back)

        bot.send_message(message.chat.id, "Выберите нужный год:", reply_markup=markup)

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("🪪 СНИЛС")
        btn2 = types.KeyboardButton("🌐 Ссылки")
        btn3 = types.KeyboardButton("📊 Текущий конкурс")
        btn4 = types.KeyboardButton("📚 Статистика прошлых лет")
        markup.add(btn1, btn2, btn3, btn4)

        bot.send_message(message.chat.id, "Вы вернулись в главное меню", reply_markup=markup)

    elif (message.text in ["2022", "2021", "2020", "2019", "2018"]):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Очная форма обучения")
        btn2 = types.KeyboardButton("Очно-заочная форма обучения")
        btn3 = types.KeyboardButton("Вернуться к выбору года")
        btn4 = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4)

        year = message.text
        bot.send_message(message.chat.id, "Выберите форму обучения:", reply_markup=markup)
        bot.register_next_step_handler(message, number_request, year)

    elif (message.text in ["2017", "2016", "2015", "2014", "2013"]):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Очная форма обучения")
        btn2 = types.KeyboardButton("Очно-заочная форма обучения")
        btn3 = types.KeyboardButton("Заочная форма обучения")
        btn4 = types.KeyboardButton("Вернуться к выбору года")
        btn5 = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, btn3, btn4, btn5)

        year = message.text
        bot.send_message(message.chat.id, "Выберите форму обучения:", reply_markup=markup)
        bot.register_next_step_handler(message, number_request, year)

    elif (message.text == "🌐 Cсылки"):
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton("Официальные документы", url='https://priem.mirea.ru/official')
        button2 = types.InlineKeyboardButton("Гид по специальностям", url='https://priem.mirea.ru/guide?eduLevel=bach-spec&sorting=')
        button3 = types.InlineKeyboardButton("Гид по олимпиадам", url="https://priem.mirea.ru/olympiads")
        button4 = types.InlineKeyboardButton("Дни открытых дверей", url="http://priem.mirea.ru/open-doors/")
        button5 = types.InlineKeyboardButton("Мероприятия для школьников", url="https://priem.mirea.ru/events")
        button6 = types.InlineKeyboardButton("Подготовка к поступлению", url="https://dovuz.mirea.ru/")
        button7 = types.InlineKeyboardButton("Многопрофильная олимпиада МИРЭА", url="https://priem.mirea.ru/olymp-landing/")
        button8 = types.InlineKeyboardButton("Особенности приема", url="https://priem.mirea.ru/first-degree/admission-features")
        markup.add(button1, button2)
        markup.add(button3, button4)
        markup.add(button5, button6)
        markup.add(button7, button8)
        bot.send_message(message.chat.id, "Нажмите на кнопку и перейдите на сайт)".format(message.from_user), reply_markup=markup)

bot.polling()

"""
"\n🔗 Добавить ссылку - добавить ссылку на конкурсный список"
"\n💻 Просмотр всех ссылок - просмотр всех добавленных ссылок"
"\n📑 Посмотреть список - просмотр конкурсного списка"
"\n📍 Проверить позицию - проверить свою позицию в списке"
"\n🔎 Поиск по номеру - посмотреть информацию по порядковому номеру"
"""
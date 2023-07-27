from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def parser_targeted_and_separate(url):
    """
    Функция собирает данные из списков на целевое обучение
    и списков по отдельной квоте.
    :param url: ссылка на список
    :return: main_table: список списков с информацией из таблицы
    """

    ops = webdriver.ChromeOptions()
    ops.add_argument('headless')
    driver_service = Service(executable_path="C:/chromedriver.exe")
    driver = webdriver.Chrome(service=driver_service, options=ops)

    driver.get(url)
    html = driver.page_source

    main_table = []
    parse = BeautifulSoup(html, features="html.parser")
    table = parse.find("table", class_="namesTable")
    head = table.find("thead")

    # Собираем заголовки в список
    headers = []
    for i, data in enumerate(head.find_all("td")):
        if i == 7:
            continue

        title = data.text.strip()
        title = title.replace("\xa0", " ")
        headers.append(title)

    body = table.find("tbody")

    # Считываем строки таблицы
    counter = 0
    for row in body.find_all("tr"):
        # Ищем надпись с видом ЦП
        company_name = row.find("td", class_="tgtOrgTr")
        if company_name:
            if counter > 0:
                main_table.append(temp_list)
            temp_list = []
            string = company_name.find("strong")
            text = string.text
            text = text.replace("\xa0", " ")
            temp_list.append(text)
            continue

        # Считываем обычные строки таблицы
        data = row.find_all("td")
        list_for_inf = []
        for inf in data:
            txt = inf.text
            txt = txt.replace("\xa0", " ")
            list_for_inf.append(txt)

        # Удаляем запись с баллами
        del list_for_inf[7]

        # Объединяем два списка в словарь
        temp_dict = {}
        for index, inf in enumerate(headers):
            temp_dict[inf] = list_for_inf[index]
        temp_list.append(temp_dict)
        counter += 1

    main_table.append(temp_list)
    return main_table

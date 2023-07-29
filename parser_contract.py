from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def parser_contract(url):
    """
    Функция собирает данные из списков поступающих по договору
    :param url: ссылка на список
    :return: main_table: список словарей с информацией из таблицы
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
        if i == 5:
            continue

        title = data.text.strip()
        title = title.replace("\xa0", " ")
        headers.append(title)

    body = table.find("tbody")

    # Собираем информацию с каждой строки
    for row in body.find_all("tr"):
        temp_dict = {}
        temp = []
        data = row.find_all("td")
        for inf in data:
            text = inf.text
            text = text.replace("\xa0", " ")
            temp.append(text)

        # Удаляем запись с баллами
        del temp[5]

        # Объединяем два списка в словарь
        for index, inf in enumerate(headers):
            temp_dict[inf] = temp[index]
        main_table.append(temp_dict)

    return main_table

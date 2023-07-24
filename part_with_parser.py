from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
BROKEN_YEARS = ['2018', '2017', '2016']

def parser(url):
    ops = webdriver.ChromeOptions()
    ops.add_argument('headless')
    driver_service = Service(executable_path="C:/chromedriver.exe")
    driver = webdriver.Chrome(service=driver_service, options=ops)

    driver.get(url)
    html = driver.page_source

    main_table = []
    parse = BeautifulSoup(html, features="html.parser")
    tables = parse.find_all("div", class_="accordion")  # кнопочки на главной

    for table in tables:
        forms_of_education = table.find_all("div", class_="card-body")

        for form in forms_of_education:
            form_of_education = [] # Сюда надо закинуть все записи
            all_tables = form.find_all("tr", class_="table-primary") # Все таблицы

            # Собираем заголовки в список
            headers = []
            header = all_tables[0]
            for i in header.find_all("td"):
                title = i.text.strip()
                title = title.replace("\xa0", " ")
                title = title.replace("\n", "")
                headers.append(title)

            rows = form.find_all("tr")[1:]  # Все строки из таблицы

            # Собираем инфу с каждой строки
            for row in rows:
                temp = {}
                data = row.find_all("td")
                for index, inf in enumerate(data):
                    sup = inf.find_all("sup")
                    if len(sup) > 0:
                        inf.sup.decompose()
                    text = inf.text
                    text = text.replace("\xa0", " ")
                    temp[headers[index]] = text

                form_of_education.append(temp)

            main_table.append(form_of_education)
            if url[-4:] in BROKEN_YEARS:
                break

        # Удаляем лишние записи
        for i in main_table:
            for index, dict in enumerate(i):
                if len(list(dict.keys())) == 1:
                    del i[index]

    return main_table

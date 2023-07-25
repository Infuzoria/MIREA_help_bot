from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def parser_general_competition(url):
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

    print(headers)

parser_general_competition("https://priem.mirea.ru/accepted-entrants-list/personal_code_rating.php?competition=1748193468849593654")
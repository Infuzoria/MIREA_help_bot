from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def parser_places(url):
    """
    Функция отправляет запрос на сайт и возвращает количество мест
    :param url: ссылка на список
    :return: places: количество мест на направлении
    """

    ops = webdriver.ChromeOptions()
    ops.add_argument('headless')
    driver_service = Service(executable_path="C:/chromedriver.exe")
    driver = webdriver.Chrome(service=driver_service, options=ops)

    driver.get(url)
    html = driver.page_source

    parse = BeautifulSoup(html, features="html.parser")
    temp_div = parse.find("div", class_="names")
    list_with_p = temp_div.find_all("p")
    if list_with_p[1].text[:10] == "Всего мест":
        places = list_with_p[1].text[-2:]
    else:
        places = "-"

    return places

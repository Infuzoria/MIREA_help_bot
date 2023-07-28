from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

def general_paser(url):
    """
    Функция отправляет запрос на сайт и возвращает время последнего обновления списка
    :param url: ссылка на список
    :return: places: время последнего обновления списка
    """

    ops = webdriver.ChromeOptions()
    ops.add_argument('headless')
    driver_service = Service(executable_path="C:/chromedriver.exe")
    driver = webdriver.Chrome(service=driver_service, options=ops)

    driver.get(url)
    html = driver.page_source


    parse = BeautifulSoup(html, features="html.parser")

    temp_div = parse.find("div", class_="names")
    time = temp_div.find("p", class_="lastUpdate").text

    return time

from selenium import webdriver
import json

# Настройка драйвера
driver = webdriver.Chrome()

# Открываем страницу
driver.get("https://ovoko.pl/szukaj?man_id=3&cmc=137&cpc=498&mfi=3,137;&prs=1")

# Дожидаемся полной загрузки страницы
driver.implicitly_wait(10)

# Ищем скрытый JSON или данные, загружаемые динамически
# В зависимости от структуры страницы вы можете искать элемент с данными
page_source = driver.page_source

# Если данные содержатся в скрипте на странице
# Используем BeautifulSoup для поиска и извлечения JSON, если он встроен в HTML
from bs4 import BeautifulSoup

soup = BeautifulSoup(page_source, 'html.parser')
script_tag = soup.find('script', {'type': 'application/ld+json'})
if script_tag:
    json_data = json.loads(script_tag.string)
    print(json_data)

driver.quit()

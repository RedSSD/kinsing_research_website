import os
import csv
from bs4 import BeautifulSoup
import random
import time
import json
import logging
from pprint import pprint
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait

from core_app.models import Advertisement, ExportedFile

logger = logging.getLogger(__name__)


def wait_for_page_load(driver, timeout=60):
    """Wait until the page is fully loaded, including JavaScript."""
    try:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        return None

def wait_for_ajax(driver, timeout=60):
    try:
        WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return jQuery.active == 0"))
    except Exception as e:
        return None

class PageScraper:
    def __init__(self, proxies, parsing_link_object, max_tabs=15):
        self.proxies = proxies
        self.parsing_link_object = parsing_link_object
        self.all_links = []
        self.max_tabs = max_tabs  # Количество вкладок на один драйвер
        self.driver = None  # Драйвер будет сохраняться
        self.current_tab_count = 0  # Текущее количество открытых вкладок

    def check_driver(self):
        try:
            # Попробуем выполнить простую команду для проверки состояния драйвера
            if self.driver:
                self.driver.current_url
            else:
                raise WebDriverException("Драйвер не инициализирован")
        except WebDriverException:
            print("Драйвер не отвечает, инициализируем новый драйвер...")
            self.driver = self.configure_driver()

    def configure_driver(self):
        if self.driver is None:
            if self.driver is not None:
                self.driver.quit()  # Закрываем старый драйвер
            options = uc.ChromeOptions()
            options.add_argument('--headless')  # Убрать строку, если нужен полноценный браузер
            options.add_argument("--disable-gpu")
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--user-agent={UserAgent().random}')
            proxy = random.choice(self.proxies)
            print(f"Создали новый драйвер")
            self.driver = uc.Chrome(options=options, version_main=123)
            self.current_tab_count = 0  # Сбрасываем счетчик вкладок

    def open_new_tab(self, url):
        """Открывает новую вкладку для указанного URL и переключается на неё."""
        self.configure_driver()  # Убедиться, что драйвер существует или создан
        self.driver.execute_script(f"window.open('{url}', '_blank');")  # Открываем новую вкладку
        self.current_tab_count += 1  # Увеличиваем счётчик вкладок
        self.driver.switch_to.window(self.driver.window_handles[-1])  # Переключаемся на последнюю вкладку

    def accept_cookies(self):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            ).click()
            print("Куки приняты.")
        except Exception as e:
            print(f"Не удалось нажать кнопку куки, или её просто нет: {e}")

    def collect_links(self, url):
        self.check_driver()
        self.driver.get(url)
        wait = WebDriverWait(self.driver, 15)
        self.accept_cookies()
        all_links = []

        while True:
            try:
                wait_for_page_load(self.driver)
                wait_for_ajax(self.driver)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.products__items__link')))
                product_links = self.driver.find_elements(By.CSS_SELECTOR, '.products__items__link')
                all_links.extend([link.get_attribute('href') for link in product_links])
                print(f"Найдено {len(product_links)} ссылок на этой странице.")

                try:
                    next_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH,
                         "//a[contains(@class, 'pages__links') and contains(text(), 'Następny') and not(contains(@class, 'pages__links--disabled'))]")))
                    if next_button.is_enabled():
                        next_url = next_button.get_attribute('href')
                        print(f"Переход на следующую страницу: {next_url}")
                        self.driver.get(next_url)  # Переход на следующую страницу
                    else:
                        print("Кнопка 'Далее' отключена. Страницы закончились.")
                        break
                except TimeoutException:
                    print("Timeout: Кнопка 'Далее' не стала активной вовремя.")
                    break

            except TimeoutException:
                print("Timeout: Ссылки на продукты не загрузились вовремя.")
                break
            except WebDriverException as e:
                print(f"WebDriverException: {e}. Пауза на 10 секунд перед повторной попыткой.")
                time.sleep(4)
                self.driver = self.configure_driver()# Пауза перед повторной попыткой

        return all_links

    def parse_page(self, url):
        print(f"Парсинг страницы: {url}")

        # Устанавливаем начальную попытку
        attempt = 0
        max_attempts = 3  # Максимальное количество попыток

        while attempt < max_attempts:
            try:
                self.check_driver()
                self.driver.get(url)
                self.driver.implicitly_wait(7)
                content = self.driver.page_source
                soup = BeautifulSoup(content, 'html.parser')

                # Парсинг данных страницы
                title = soup.find('h1', class_='part__title').get_text(strip=True)
                price = soup.find('span', {'data-testid': 'part-price'}).get_text(strip=True)
                offer_number = soup.find('a', {'data-testid': 'part-code-desktop'}).get_text(strip=True)

                product_data = {}
                delivery_section = soup.find('div', class_='product_desc__block')
                if delivery_section:
                    delivery_details = {}
                    delivery_caption = delivery_section.find('span', class_='product_desc__links__delivery--caption')
                    if delivery_caption:
                        delivery_details['caption'] = delivery_caption.text.strip()

                    delivery_select = delivery_section.find('span', class_='product_desc__links__delivery--select')
                    if delivery_select:
                        delivery_details['delivery_area'] = delivery_select.text.strip()

                    product_data['delivery'] = delivery_details

                part_description_block = soup.find('div', {'data-testid': 'part-description-block'})
                if part_description_block:
                    part_details = {}
                    details_dl = part_description_block.find_all('dl', class_='product_details')
                    for dl in details_dl:
                        for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                            term = dt.get_text(strip=True)
                            description = dd.get_text(strip=True)
                            part_details[term] = description

                    product_data['part_details'] = part_details

                car_description_block = soup.find('div', {'data-testid': 'car-description-block'})
                if car_description_block:
                    car_details = {}
                    car_details_dl = car_description_block.find_all('dl', class_='product_details')
                    for dl in car_details_dl:
                        for dt, dd in zip(dl.find_all('dt'), dl.find_all('dd')):
                            term = dt.get_text(strip=True)
                            description = dd.get_text(strip=True)
                            car_details[term] = description

                    product_data['car_details'] = car_details

                other_parts_block = soup.find('div', {'data-testid': 'product-desc-4'})
                if other_parts_block:
                    other_parts = []
                    parts_items = other_parts_block.find_all('li', class_='product_other__items')
                    for item in parts_items:
                        part_info = {}
                        part_link = item.find('a', class_='product_other__links')
                        if part_link:
                            part_info['title'] = part_link.get('title')
                            part_info['url'] = part_link.get('href')

                        part_image = item.find('img')
                        if part_image:
                            part_info['image'] = part_image.get('data-full-img')

                        other_parts.append(part_info)

                    product_data['other_parts'] = other_parts

                seller_name = soup.find('span', {'class': 'seller__title', 'data-testid': 'seller-title'}).get_text(
                    strip=True)
                gallery = soup.find(class_='product_gallery_for product_gallery_for--main is-draggable')
                image_links = [img['src'] for img in gallery.find_all('img')] if gallery else []

                return {
                    'link': url,
                    'title': title,
                    'image': image_links,
                    'price': float(price.replace('zł', '').replace(',', '.').strip()),
                    'offer_number': offer_number,
                    'product_data': product_data,
                    'image_links': image_links,
                    'seller': seller_name
                }

            except WebDriverException as e:
                if "disconnected: not connected to DevTools" in str(e):
                    print(
                        "WebDriverException: Потеряно соединение с DevTools. Пауза на 10 секунд перед повторной попыткой.")
                    time.sleep(4)
                    self.driver= self.configure_driver()  # Повторная настройка драйвера
                    attempt += 1
                else:
                    print(f"WebDriverException: {e}")
                    break
            except Exception as e:
                print(f"Ошибка: {e}")
                break
        return None

    def save_to_db(self, data):
        part = self.parsing_link_object.part
        part_group = part.part_group
        brand = self.parsing_link_object.brand
        model = self.parsing_link_object.model

        try:
            Advertisement.objects.create(
            part_name_ua=part.name_ua,
            part_name_ru=part.name_ru,
            part_group_name_ua=part_group.name_ua,
            part_group_name_ru=part_group.name_ru,
            part_site_id=part.site_id,
            part_group_site_id=part_group.site_id,
            symbolic_code=part.symbolic_code,
            brand=brand.name,
            brand_site_id=brand.site_id,
            model=model.name,
            model_site_id=model.site_id,
            generation=self.parsing_link_object.generation,
            description_ua=self.parsing_link_object.description_ua,
            description_ru=self.parsing_link_object.description_ru,
            label_1=self.parsing_link_object.label_1,
            label_2=self.parsing_link_object.label_2,
            label_3=self.parsing_link_object.label_3,
            price_euro=self.parsing_link_object.price_formula,
            symbolic_code_site=None,
            allegro_link=data['link'],
            allegro_id=data['offer_number'],
            allegro_price_pln=data['price'],
            allegro_title=data['title'],
            vin=data.get('product_data', {}).get('car_details', {}).get('Numer VIN', 'N/A'),
            allegro_seller=data['seller'],
            allegro_images="; ".join(data['image_links']),
            parsing_link=self.parsing_link_object,
            exported=False,
            )
        except Exception as e:
            print("Problem to save db", e)

    def save_to_file(self, data, file_name="scraped_data2.json"):
        with open(file_name, 'a') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write('\n')  # Ensure each item is on a new line

    def scrape(self, url):
        self.configure_driver()
        links = self.collect_links(url)
        print(f"Collected {len(links)} product links.")
        start_time = time.time()  # Track the start time
        total_saved = 0  # Count of saved products

        for i, link in enumerate(links, start=1):
            try:
                product_data = self.parse_page(link)
                if product_data:
                    
                    #self.save_to_file(product_data)
                    self.save_to_db(product_data)
                    total_saved += 1
                    print(f"Data saved for {product_data['title']}")
                else:
                    print("Problem in scrape")
            except Exception as e:
                    print(e)
            # Print statistics every 10 seconds
            if i % 10 == 0:  # Print stats every 10 products
                elapsed_time = time.time() - start_time
                speed = i / elapsed_time  # Speed of scraping (products per second)
                print(f"Saved {total_saved} products. Speed: {speed:.2f} products/second")
                print(f"Elapsed time: {elapsed_time:.2f} seconds.")
            
            

        total_time = time.time() - start_time
        print(f"Scraping completed. Total time: {total_time:.2f} seconds.")
        print(f"Total products saved: {total_saved}")

    def start(self):
        print("Starting parsing")
        self.scrape(self.parsing_link_object.allegro_catalog_link)
        #self.scrape("https://ovoko.pl/szukaj?man_id=3&cmc=141&cpc=498&mfi=3,141;&prs=1&page=1")



def parse_allegro_catalog(parsing_link_object):
    # Example usage
    proxies = [
        ""]

    scraper = PageScraper(proxies, parsing_link_object)
    # scraper.scrape("https://ovoko.pl/szukaj?man_id=3&cmc=141&cpc=498&mfi=3,141;&prs=1&page=1")
    scraper.start()


def export_advertisements(export_file, advertisements):
    exports_dir = "exports"
    os.makedirs(exports_dir, exist_ok=True)

    custom_headers = export_file.custom_headers
    header_row = [k for k, v in custom_headers.items()]

    file_index = 1
    remaining_advertisements = advertisements

    while remaining_advertisements:
        file_path = os.path.join(exports_dir, f"{export_file.file_name}_{file_index}.csv")
        logger.info(f"Exporting to {file_path} with headers: {custom_headers}")

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_row)

            ads_to_export = remaining_advertisements[: export_file.items_count]
            for ad in ads_to_export:
                row = [getattr(ad, v, "") for k, v in custom_headers.items()]
                writer.writerow(row)

            exported_file = ExportedFile.objects.create(
                filename=f"{export_file.file_name}_{file_index}",
                filepath=csvfile.name
            )
            exported_file.save()

        remaining_advertisements = remaining_advertisements[export_file.items_count:]
        file_index += 1

    advertisements.update(exported=True)

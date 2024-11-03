import random
import time
import json
from pprint import pprint

from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from core_app.models import Advertisement

def wait_for_page_load(driver, timeout=60):
    """Wait until the page is fully loaded, including JavaScript."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script('return document.readyState') == 'complete'
    )


def wait_for_ajax(driver, timeout=60):
    """Waits until all AJAX requests have completed."""
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return jQuery.active == 0"))


class PageScraper:
    def __init__(self, proxies, parsing_link_object):
        self.proxies = proxies
        self.parsing_link_object = parsing_link_object
        self.all_links = []


    def configure_driver(self):
        options = uc.ChromeOptions()
        #options.add_argument('--headless')  # Uncomment this line to run in headless mode
        options.add_argument('--no-sandbox')
        options.add_argument(f'--user-agent={UserAgent().random}')

        # Select a random proxy from the list and apply it
        proxy = random.choice(self.proxies)
        print(proxy)
        #options.add_argument(f'--proxy-server={proxy}')

        # Initialize the undetected ChromeDriver
        driver = uc.Chrome(options=options)

        return driver

    def accept_cookies(self, driver):
        try:
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
            ).click()
            print("Куки приняты.")
        except Exception as e:
            print(f"Не удалось нажать кнопку куки, или ее просто нет: {e}")

    def collect_links(self, url):
        driver = self.configure_driver()
        driver.get(url)
        wait = WebDriverWait(driver, 15)
        self.accept_cookies(driver)# Set up WebDriverWait with a timeout of 10 seconds
        all_links = []

        while True:
            try:
                # Wait until the product links are visible on the page

                wait_for_page_load(driver)
                wait_for_ajax(driver)
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.products__items__link')))
                # Collect product links from the current page
                product_links = driver.find_elements(By.CSS_SELECTOR, '.products__items__link')
                all_links.extend([link.get_attribute('href') for link in product_links])
                print(f"Found {len(product_links)} links on this page.")
            except TimeoutException:
                print("Timeout: Product links did not load in time.")
                break

            try:

                # Wait for the "Next" button to be clickable and then move to the next page
                next_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//a[contains(@class, 'pages__links') and contains(text(), 'Następny') and not(contains(@class, 'pages__links--disabled'))]")))

                if next_button.is_enabled():
                    next_url = next_button.get_attribute('href')
                    print(f"Going to the next page: {next_url}")
                    driver.get(next_url)  # Go to the next page
                else:
                    print("Next button is disabled. No more pages.")
                    break
            except TimeoutException:
                print("Timeout: Next button did not become clickable in time.")
                break
            except Exception as e:
                print(f"Error navigating to the next page: {e}")
                break

        driver.quit()
        return all_links

    def parse_page(self, url):
        print(url)
        driver = self.configure_driver()
        driver.get(url)

        driver.implicitly_wait(7)
        driver.find_element(By.CSS_SELECTOR, '.product_column.product_column--right')

        content = driver.page_source
        soup = BeautifulSoup(content, 'html.parser')
        try:
            title = soup.find('h1', class_='part__title').get_text(strip=True)
            price = soup.find('span', {'data-testid': 'part-price'}).get_text(strip=True)
            offer_number = soup.find('a', {'data-testid': 'part-code-desktop'}).get_text(strip=True)

            driver.quit()

            product_data = {}
            # Extract delivery information
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

            # Extract part details
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

            # Extract car details
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

            # Extract other parts information
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
            seller_name = soup.find('span', {'class': 'seller__title', 'data-testid': 'seller-title'}).get_text(strip=True)
            #image_links = [img['data-src'] for img in soup.find_all('div', {'data-testid': 'product-image'})]
            return {
                'link': url,
                'title': title,
                'image': image_links,
                'price': float(price.replace('zł', '').replace(',', '.').strip()),
                'offer_number': offer_number,
                'product_data': product_data,
                'seller': seller_name
            }
        except Exception as e:
            return e

    def save_to_db(self, data):
        part = self.parsing_link_object.part
        part_group = part.part_group
        brand = self.parsing_link_object.brand
        model = self.parsing_link_object.model
        Advertisement.objects.acreate(
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
            #allegro_images="; ".join(images) if images else "",
            parsing_link=self.parsing_link_object,
            exported=False,
        )

    def save_to_file(self, data, file_name="scraped_data2.json"):
        with open(file_name, 'a') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
            file.write('\n')  # Ensure each item is on a new line

    def scrape(self, url):
        links = self.collect_links(url)
        print(f"Collected {len(links)} product links.")

        start_time = time.time()  # Track the start time
        total_saved = 0  # Count of saved products

        for i, link in enumerate(links, start=1):
            product_data = self.parse_page(link)
            #self.save_to_file(product_data)
            total_saved += 1

            # Print statistics every 10 seconds
            if i % 10 == 0:  # Print stats every 10 products
                elapsed_time = time.time() - start_time
                speed = i / elapsed_time  # Speed of scraping (products per second)
                print(f"Saved {total_saved} products. Speed: {speed:.2f} products/second")
                print(f"Elapsed time: {elapsed_time:.2f} seconds.")
            pprint(product_data)
            print(f"Data saved for {product_data['title']}")

        total_time = time.time() - start_time
        print(f"Scraping completed. Total time: {total_time:.2f} seconds.")
        print(f"Total products saved: {total_saved}")

    def start(self):
        print("Starting parsing")
        #self.scrape(self, self.parsing_link_object.allegro_catalog_link)
        self.scrape("https://ovoko.pl/szukaj?man_id=3&cmc=141&cpc=498&mfi=3,141;&prs=1&page=1")


# Example usage
proxies = [
""]

scraper = PageScraper(proxies, None)
#scraper.scrape("https://ovoko.pl/szukaj?man_id=3&cmc=141&cpc=498&mfi=3,141;&prs=1&page=1")
scraper.start()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import csv
import os

with open('data/cities.txt', 'r', encoding='utf-8') as file:
    cities = [row.strip() for row in file.readlines()]

with open('data/types.txt', 'r', encoding='utf-8') as file:
    types = [row.strip() for row in file.readlines()]

with open('data/state.txt', 'r', encoding='utf-8') as file:
    state = [row.strip() for row in file.readlines()]

length_cities = len(cities)
length_types = len(types)
state = state[0]
file_path = f'data/{state.lower()}_raw.csv'

print(f'{state}\nCount of cities: {length_cities}\nCount of types: {length_types}')

# [101/714]
city_count = int(input("Type a number of city to start: ")) - 1
cities = cities[city_count:]

print(f'We\'ll start with {cities[0]}')

def create_file():
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Title', 'MainType', 'GoogleMapsType', 'Website', 'Phone', 'City', 'Location', 'Link'
            ])

def scroll_to_end(driver):
    timeout = 60
    def is_element_present():
        try:
            driver.find_element(By.CSS_SELECTOR, "span.HlvSq")
            return True
        except:
            return False

    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_element_present():
            break

        records = fetch_all_records(driver)
        if len(records) > 0:
            ActionChains(driver).move_to_element(records[-1]).perform()
            records[-1].send_keys(Keys.PAGE_DOWN)

        time.sleep(0.5)
def fetch_all_records(driver):
    return driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')

def run_browser():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    base_url = "https://www.google.com/maps?hl=en"
    driver.get(base_url)
    # driver.execute_script("document.body.style.zoom = '80%'")
    time.sleep(10)

    for i, city in enumerate(cities, start=city_count+1):
        total = 0
        for j, type in enumerate(types, start=1):
            search_box = driver.find_element(By.CSS_SELECTOR, "input[class='searchboxinput xiQnY']")
            search_box.send_keys(f'{city} California {type}')
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            try:
                scroll_to_end(driver)
            except Exception as ex:
                print(ex)
            try:
                records = fetch_all_records(driver)
                count = len(records)
            except:
                records = []

            for k, record in enumerate(records, start=1):
                time.sleep(1)

                try:
                    record.click()
                    time.sleep(3)
                except:
                    pass

                try:
                    title = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob').text
                except:
                    title = None
                try:
                    actual_type = driver.find_element(By.CSS_SELECTOR, 'button.DkEaL ').text
                except:
                    actual_type = None

                location = None
                phone = None
                website = None
                try:
                    all_divs = driver.find_elements(By.CSS_SELECTOR, 'div.rogA2c div.Io6YTe.fontBodyMedium.kR99db')
                    for div_el in all_divs:
                        el_text = div_el.text
                        if 'United States' in el_text:
                            location = el_text
                        elif '+1' in el_text:
                            phone = el_text
                        elif '.' in el_text:
                            website = el_text
                except:
                    try:
                        location = driver.find_elements(By.CSS_SELECTOR, 'div.rogA2c div.Io6YTe.fontBodyMedium.kR99db')[0].text
                    except:
                        location = None
                    try:
                        website = driver.find_elements(By.CSS_SELECTOR, 'div.rogA2c div.Io6YTe.fontBodyMedium.kR99db')[1].text
                    except:
                        website = None
                    try:
                        phone = driver.find_elements(By.CSS_SELECTOR, 'div.rogA2c div.Io6YTe.fontBodyMedium.kR99db')[2].text
                    except:
                        phone = None
                try:
                    link = record.get_attribute('href')
                except:
                    link = None


                if title or location or phone or website:
                    with open(file_path, 'a', encoding='utf-8', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([
                            title, type, actual_type, website, phone, city, location, link
                        ])

                print(f'[{i}/{length_cities}] [{j}/{length_types}] - [{k}/{count}] {title} - {actual_type} - {website} - {phone} - {location} - {link}')

            search_box.send_keys(Keys.CONTROL + "a")
            search_box.send_keys(Keys.DELETE)

        print(f'[{i}/{length_cities}] : {total}')

    driver.quit()

def main():
    create_file()
    run_browser()

if __name__ == '__main__':
    main()

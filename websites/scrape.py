import re
import numpy

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

url_fruit = "https://meny.no/varer/fisk-skalldyr"
total_items_one_page = 42

options = Options()
#options.headless = True

driver = webdriver.Firefox(options=options)
driver.get(url_fruit)

wait = WebDriverWait(driver, 10)
loadMore = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ws-product-view__footer")))
results = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/div[1]/div[4]")))
while not results.text:
    pass

# 'Show more' button press
pages = int(numpy.floor(int(re.search(r'\d+', results.text).group()) / 42))
for i in range(pages):
    loadMore.click()
    print(i)

items = driver.find_elements(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/ul/li/div/div/h3/a")
count = 1
for item in items:
    # Open list of every item
    item.click()
    print(count, ":")
    try:
        # Open the nutrition list 
        wait_item = WebDriverWait(driver, 2)
        nutrient_button = wait_item.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ws-product-data__section.ws-product-data__section--nutritional-content")))
        show_nutrient = WebDriverWait(nutrient_button, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "ngr-accordion-item__header--inline")))
        show_nutrient.click()
        
        # List nutrition list
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")
        reviews_selector = soup.find_all('li', class_='ws-nutritional-content__list-view-item')
        for item in reviews_selector:
            print(item.text)

    except TimeoutException:
        print("Ingen næringsinnhold")

    try:
        # Close list of item
        close_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".ngr-close-button.ngr-modal__close")))
        close_button.click()
    except TimeoutException:
        print("Timeout")

    count += 1
driver.close()
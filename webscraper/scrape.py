import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

import db.db_ as db_

url_fruit = "https://meny.no/varer/frukt-gront"
total_items_one_page = 42

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
driver.get(url_fruit)

wait = WebDriverWait(driver, 10)
loadMore = wait.until(
    EC.presence_of_element_located((By.CLASS_NAME, "ws-product-view__footer"))
)
results = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/div[1]/div[4]")
    )
)
while not results.text:
    pass

# 'Show more' button pressed
pages = int((int(re.search(r"\d+", results.text).group()) // 42))
for i in range(pages):
    loadMore.click()
    print(i)

items = driver.find_elements(
    By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/ul/li/div/div/h3/a"
)
count = 1
for item in items:
    # Open list of every item
    item.click()

    append_groceries = {
        "title": "",
        "description": "",
        "Energi": "",
        "Kalorier": "",
        "Fett": "",
        "Mettet fett": "",
        "Enumettet fett": "",
        "Flerumettet fett": "",
        "Karbohydrater": "",
        "Sukkerarter": "",
        "Stivelse": "",
        "Kostfiber": "",
        "Protein": "",
        "Salt": "",
    }
    descritions = wait.until(
        EC.presence_of_element_located(
            (
                By.CLASS_NAME,
                "ws-product-details__subtitle",
            )
        )
    )
    append_groceries["title"] = item.text
    append_groceries["description"] = descritions.text

    try:
        # Open the nutrition list
        wait_item = WebDriverWait(driver, 2)
        nutrient_button = wait_item.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".ws-product-data__section.ws-product-data__section--nutritional-content",
                )
            )
        )
        show_nutrient = WebDriverWait(nutrient_button, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, "ngr-accordion-item__header--inline")
            )
        )
        show_nutrient.click()

        # List nutrition list
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, "lxml")
        reviews_selector = soup.find_all(
            "li", class_="ws-nutritional-content__list-view-item"
        )

        for item in reviews_selector:
            nutrient, descritions = item.text.split(": ")
            desc = descritions.replace(",", ".")
            desc = re.search(r"[-+]?\d*\.\d+|\d+", desc).group()
            append_groceries[nutrient] = float(desc)

        db_.add_item(
            title=append_groceries["title"],
            description=append_groceries["description"],
            energy=append_groceries["Energi"],
            calories=append_groceries["Kalorier"],
            fat=append_groceries["Fett"],
            saturated_fat=append_groceries["Mettet fett"],
            unsaturated_fat=append_groceries["Enumettet fett"],
            polyunsaturated_fat=append_groceries["Flerumettet fett"],
            carbs=append_groceries["Karbohydrater"],
            sugar=append_groceries["Sukkerarter"],
            starch=append_groceries["Stivelse"],
            fiber=append_groceries["Kostfiber"],
            protein=append_groceries["Protein"],
            salt=append_groceries["Salt"],
        )

    except TimeoutException:
        print("Ingen næringsinnhold")
        db_.add_item(
            title=append_groceries["title"],
            description=append_groceries["description"]
        )

    try:
        # Close list of item
        close_button = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".ngr-close-button.ngr-modal__close")
            )
        )
        close_button.click()
    except TimeoutException:
        print("Timeout")

    count += 1
driver.close()

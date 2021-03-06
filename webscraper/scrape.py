import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import db.db_ as db_

url_fruit = "https://meny.no/varer/"
total_items_one_page = 42

options = webdriver.FirefoxOptions()

# Docker lines
# options.add_argument('--headless')
# driver = webdriver.Remote("http://selenium:4444/wd/hub", options=options)

# Debugging line
driver = webdriver.Firefox(options=options)


def get_sections(driver):
    wait = WebDriverWait(driver, 10)
    sections = wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "li.cw-categories__item.cw-categories__item--inactive a.cw-categories__title span.cw-categories__title__text",
            )
        )
    )

    items = driver.find_elements(
        By.CSS_SELECTOR,
        "li.cw-categories__item.cw-categories__item--inactive a.cw-categories__title span.cw-categories__title__text",
    )
    return items


def get_subsections(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "html.wsproductlistpage.webshoppage.pagetype--WSProductListPage.no-js body.notloggedin div.page div.cw-main-wrapper div.cw-split.cw-section div.cw-categories div#mobile_products_nav.cw-categories__body ul.cw-categories__list li.cw-categories__item.cw-categories__item--active ul.cw-categories__list li.cw-categories__item.cw-categories__item--inactive a.cw-categories__title span.cw-categories__title__text",
            )
        )
    )

    items = driver.find_elements(
        By.CSS_SELECTOR,
        "html.wsproductlistpage.webshoppage.pagetype--WSProductListPage.no-js body.notloggedin div.page div.cw-main-wrapper div.cw-split.cw-section div.cw-categories div#mobile_products_nav.cw-categories__body ul.cw-categories__list li.cw-categories__item.cw-categories__item--active ul.cw-categories__list li.cw-categories__item.cw-categories__item--inactive a.cw-categories__title span.cw-categories__title__text",
    )
    return items


def get_elements(section, subsection, driver):
    # Show more button found
    wait = WebDriverWait(driver, 10)
    loadMore = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "ws-product-view__footer"))
    )

    # Find total amount of products to calculate how many pages to laod
    results = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".ws-product-filter__item.ws-product-filter__item--total")
        )
    )

    # screenshot = driver.save_screenshot('test.png')
    while not results.text:
        pass

    # 'Show more' button pressed
    pages = int((int(re.search(r"\d+", results.text).group()) // 42))
    for i in range(pages):
        loadMore.click()
        print(i)

    items = driver.find_elements(
        By.XPATH,
        "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/ul/li/div/div/h3/a",
    )
    count = 1
    for item in items:
        # Open list of every item
        item.click()

        append_groceries = {
            "price": "",
            "title": "",
            "section": "",
            "subsection": "",
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

        price = wait.until(
            EC.cli(
                (
                    By.CLASS_NAME,
                    "ws-price__main",
                )
            )
        )
        kroner = [int(s) for s in price.text.split() if s.isdigit()]
        try:
            append_price = kroner[0] + kroner[1] / 100
        except IndexError:
            append_price = kroner[0]
        append_groceries["price"] = append_price
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
                price=append_groceries["price"],
                title=append_groceries["title"],
                section=section,
                subsection=subsection,
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
            print("Ingen n??ringsinnhold")
            db_.add_item(
                price=append_groceries["price"],
                title=append_groceries["title"],
                description=append_groceries["description"],
                section=section,
                subsection=subsection,
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


def main():
    driver.get(url_fruit)
    ignore_section = [
        "Ukemeny",
        "Jacobs Utvalgte 3for2",
        "Faste Knallkj??p",
        "Matskatter fra Norge",
        "Handle til bedrift?",
    ]
    ignore_subsection = []

    subsections = None
    i = 0
    j = 0
    section = get_sections(driver)
    while True:
        if i > len(section):
            break
        if section[i].text not in ignore_section:
            section_name = section[i].text
            ignore_section.append(section_name)
            section[i].click()
            subsections = get_subsections(driver)
            i = 0
            while True:
                if j > len(subsections):
                    break
                if subsections[j].text not in ignore_section:
                    subsection_name = subsections[j].text
                    ignore_subsection.append(subsection_name)
                    subsections[j].click()
                    get_elements(section_name, subsection_name, driver)
                    subsections = get_subsections(driver)
                    j = 0
                else:
                    j += 1
            section = get_sections(driver)
        else:
            i += 1


if __name__ == "__main__":
    main()
    driver.close()

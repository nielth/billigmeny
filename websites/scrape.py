import re
import time
import numpy

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

url_fruit = "https://meny.no/varer/frukt-gront"
total_items_one_page = 42

options = Options()
options.headless = True

driver = webdriver.Firefox(options=options)
driver.get(url_fruit)
time.sleep(1)
loadMore = driver.find_element(By.CLASS_NAME, "ws-product-view__footer")

results = driver.find_element(By.XPATH, "/html/body/div[1]/div[4]/div/main/div/div/div[3]/div/div[1]/div[4]")
pages = int(numpy.floor(int(re.search(r'\d+', results.text).group()) / 42))
pass
for i in range(pages):
    loadMore.click()
    print(i)
    time.sleep(1)

driver.close()
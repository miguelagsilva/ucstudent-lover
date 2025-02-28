from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import json

with open('tokens.json', 'r') as f:
    session_token = json.load(f)['session.token']

service = Service(GeckoDriverManager().install())
options = Options()
driver = webdriver.Firefox(service=service, options=options)

def selenium_request(url, click_selectors=None, skip_selectors=None, timeout=4000):
    driver.get(url)
    driver.implicitly_wait(timeout)

    if skip_selectors:
        for skip_selector in skip_selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, skip_selector))
                )
                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                print(f"Could not click skip element with selector {skip_selector}: {e}")

    if click_selectors:
        for click_selector in click_selectors:
            try:
                element = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, click_selector))
                )
                driver.execute_script("arguments[0].click();", element)
            except ElementClickInterceptedException:
                print(f"Element with selector {click_selector} was intercepted. Trying to click using JavaScript.")
                element = driver.find_element(By.CSS_SELECTOR, click_selector)
                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                print(f"Could not click element with selector {click_selector}: {e}")
            driver.wait(5000)

    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')

def setup_ucstudent_page(url):
    driver.get(url)
    driver.execute_script(f"window.localStorage.setItem('session.token', '{session_token}');")
    driver.refresh()


if __name__ == '__main__':
    url = 'https://ucstudent.uc.pt'
    timeout = 5000
    setup_ucstudent_page(url)

    CLICK_SELECTOR_SALA_VIRTUAL = 'button[arial-label="Sala virtual"]'
    CLICK_SELECTOR_LOCAL = "//button[contains(text(), 'Local')]"
    selenium_request(url, click_selectors=[CLICK_SELECTOR_SALA_VIRTUAL, CLICK_SELECTOR_LOCAL], timeout=timeout)

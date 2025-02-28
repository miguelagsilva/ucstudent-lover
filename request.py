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
options.add_argument('--headless')
driver = webdriver.Firefox(service=service, options=options)

def selenium_request(url, click_selectors=None, timeout=4000):
    driver.get(url)
    driver.implicitly_wait(timeout)

    if click_selectors:
        for click_selector in click_selectors:
            try:
                if isinstance(click_selector, tuple):
                    element = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable(click_selector)
                    )
                else:
                    element = WebDriverWait(driver, timeout).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, click_selector))
                    )

                driver.execute_script("arguments[0].click();", element)
            except Exception as e:
                print(f"Could not click element with selector {click_selector}: {e}")

            driver.implicitly_wait(2)

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

    click_selectors = [
        'button[aria-label="Sala virtual"]',
        (By.XPATH, "//button[contains(text(), 'Local')]"),
        (By.XPATH, "//button[contains(text(), 'Confirmar')]"),
    ]

    selenium_request(url, click_selectors=click_selectors, timeout=timeout)

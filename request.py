import requests
from discord_webhook import DiscordWebhook
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
import os

with open('tokens.json', 'r') as f:
    session_token = json.load(f)['session.token']

service = Service(GeckoDriverManager().install())
options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(service=service, options=options)

url = 'https://ucstudent.uc.pt'
timeout = 5000

def send_discord_message(message, file=None):
    webhook = DiscordWebhook(url=os.environ['DISCORD_WEBHOOK_URL'], content=message)
    if file is not None:
        with open(file, "rb") as f:
            webhook.add_file(file=f.read(), filename="screenshot.png")
    webhook.execute()

def mark_presence(click_selectors=None):
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
            if click_selector == click_selectors[-1]:
                driver.implicitly_wait(10)
                driver.save_screenshot("screenshot.png")
                send_discord_message(message='A presence was marked successfully!', file='screenshot.png')
        except Exception as e:
            print(f"Could not click element with selector {click_selector}: {e}")
            break

        driver.implicitly_wait(2)

    html = driver.page_source
    return BeautifulSoup(html, 'html.parser')

def setup_ucstudent_page():
    driver.get(url)
    driver.execute_script(f"window.localStorage.setItem('session.token', '{session_token}');")
    driver.refresh()
    driver.implicitly_wait(timeout)


if __name__ == '__main__':
    setup_ucstudent_page()

    click_selectors = [
        'button[aria-label="Ficheiros"]',
        #'button[aria-label="Sala virtual"]',
        #(By.XPATH, "//button[contains(text(), 'Local')]"),
        #(By.XPATH, "//button[contains(text(), 'Confirmar')]"),
    ]

    mark_presence(click_selectors=click_selectors)

from discord_webhook import DiscordWebhook
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import json
import os
import time

# Load session token
with open("tokens.json", "r") as f:
    session_token = json.load(f).get("session.token", "")

# WebDriver setup
service = Service(GeckoDriverManager().install())
options = Options()
options.add_argument("--headless")  # Uncomment for headless mode
driver = webdriver.Firefox(service=service, options=options)

# Constants
URL = "https://ucstudent.uc.pt"
TIMEOUT = 20
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def send_discord_message(message, file=None):
    """Send a message to Discord webhook with optional screenshot attachment."""
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ DISCORD_WEBHOOK_URL not set!")
        return

    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, content=message)
    if file and os.path.exists(file):
        with open(file, "rb") as f:
            webhook.add_file(file=f.read(), filename="screenshot.png")
    webhook.execute()


def click_selection(xpath):
    """Click an element using XPath safely."""
    print(f"🔍 Attempting to click: {xpath}")
    try:
        element = WebDriverWait(driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", element)
        print(f"✅ Clicked: {xpath}")
    except Exception as e:
        print(f"❌ Could not click element {xpath}: {e}")
        raise e


def setup_ucstudent_page():
    """Navigate to the page and set session token."""
    driver.get(URL)
    driver.execute_script(f"window.localStorage.setItem('session.token', '{session_token}');")
    driver.refresh()
    time.sleep(5)  # Allow JavaScript to load
    driver.refresh()


def mark_presence():
    """Mark presence in the class if not already marked."""
    click_selectors = [
        "//button[@arial-label='Entrar na sala virtual']",
        "//button[contains(@class, 'is-dark') and span[contains(text(), 'Local')]]",
        "//button[span[contains(text(), 'Marcar presença')]]",
    ]

    for idx, click_selector in enumerate(click_selectors):
        print(f"➡️ Processing step {idx + 1}: {click_selector}")

        try:
            click_selection(click_selector)
            send_discord_message(message="✅ Presence was marked successfully.")
        except Exception as e:
            if idx == 1:
                print("✅ Presence already marked. Skipping...")
                send_discord_message(message="✅ Presence already marked.")
                return
            else:
                print(f"⚠️ Skipping step {idx + 1} due to failure.")
                send_discord_message(message=f"⚠️ Presence could not be marked. {str(e)}")


if __name__ == "__main__":
    setup_ucstudent_page()

    mark_presence()

    driver.save_screenshot("screenshot.png")
    send_discord_message(message="📸 Screenshot of session", file="screenshot.png")
    driver.quit()

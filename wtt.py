import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

download_dir = os.path.abspath('./downloads')
os.makedirs(download_dir, exist_ok=True)

firefox_profile_path = webdriver.FirefoxProfile()
firefox_profile_path.set_preference('browser.download.folderList', 2)
firefox_profile_path.set_preference('browser.download.dir', download_dir)
firefox_profile_path.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.ms-excel')
firefox_profile_path.set_preference('browser.download.manager.showWhenStarting', False)

# gecko_service = Service('your geckoodriver :D')
gecko_service = Service('/Users/timtr/geckodriver')

firefox_options = Options()
firefox_options.profile = firefox_profile_path
firefox_options.add_argument('--headless')
firefox_options.add_argument('--disable-gpu')
firefox_options.add_argument('--no-sandbox')

def init_driver():
    """Initialize the WebDriver and WebDriverWait."""
    driver = webdriver.Firefox(service=gecko_service, options=firefox_options)
    wait = WebDriverWait(driver, 10)
    return driver, wait

def download_ical(wait):
    buttons = wait.until(ec.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only')
    ))
    time.sleep(1)
    buttons[2].click()

    time.sleep(2)
    downloaded_files = os.listdir(download_dir)
    return downloaded_files

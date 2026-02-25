import os
import time
import glob
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('urnik.wtt')

download_dir = os.path.abspath('./downloads')
os.makedirs(download_dir, exist_ok=True)

GECKODRIVER_PATH = os.getenv('GECKODRIVER_PATH', 'geckodriver')


def _create_firefox_options():
    """Create fresh Firefox options with download preferences."""
    firefox_profile = webdriver.FirefoxProfile()
    firefox_profile.set_preference('browser.download.folderList', 2)
    firefox_profile.set_preference('browser.download.dir', download_dir)
    firefox_profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/vnd.ms-excel')
    firefox_profile.set_preference('browser.download.manager.showWhenStarting', False)

    options = Options()
    options.profile = firefox_profile
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    return options


def init_driver():
    """Initialize the WebDriver and WebDriverWait."""
    gecko_service = Service(GECKODRIVER_PATH)
    options = _create_firefox_options()
    driver = webdriver.Firefox(service=gecko_service, options=options)
    wait = WebDriverWait(driver, 10)
    logger.debug('Firefox WebDriver initialised')
    return driver, wait


def _wait_for_new_download(existing_files, timeout=15):
    """Wait for a new .ics file to appear in the download directory."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        current_files = set(glob.glob(os.path.join(download_dir, '*.ics')))
        new_files = current_files - existing_files
        if new_files:
            return new_files.pop()
        time.sleep(0.5)
    raise TimeoutError('Timed out waiting for .ics download')


def download_ical(wait):
    """Download iCal from the current page. Returns list of downloaded files."""
    buttons = wait.until(ec.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only')
    ))
    time.sleep(1)
    buttons[2].click()

    time.sleep(2)
    downloaded_files = os.listdir(download_dir)
    return downloaded_files


def download_ical_from_url(driver, wait, url, index):
    """Navigate to a URL and download its iCal file.

    Returns the path to the renamed downloaded file (calendar_{index}.ics).
    """
    existing_files = set(glob.glob(os.path.join(download_dir, '*.ics')))

    driver.get(url)
    logger.debug('Navigated to URL: %s', url)

    buttons = wait.until(ec.presence_of_all_elements_located(
        (By.CSS_SELECTOR, 'button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-only')
    ))
    time.sleep(1)
    buttons[2].click()

    # Wait for the new file to appear
    new_file = _wait_for_new_download(existing_files)

    # Rename to avoid collisions between multiple downloads
    target_path = os.path.join(download_dir, f'calendar_{index}.ics')
    os.rename(new_file, target_path)
    logger.info('Downloaded timetable %d → %s', index + 1, target_path)
    return target_path


def download_all_icals(urls):
    """Download iCal files from all given URLs.

    Returns a list of file paths to the downloaded .ics files.
    """
    driver, wait = init_driver()
    downloaded = []

    try:
        for i, url in enumerate(urls):
            logger.info('Downloading timetable %d/%d ...', i + 1, len(urls))
            path = download_ical_from_url(driver, wait, url, i)
            downloaded.append(path)
    finally:
        driver.quit()
        logger.debug('WebDriver closed')

    return downloaded

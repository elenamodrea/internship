from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from log import message_logger
import time


def initialize():
    # Set Chrome options to start in full-screen mode
    chrome_options = Options()
    chrome_options.add_argument("--start-fullscreen")

    # Configure Chrome drive
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    message_logger("Chrome drive configured", "info")
    return driver


def use_youtube(driver):
    # Launch YouTube
    driver.get("https://www.youtube.com")
    time.sleep(5)
    message_logger("Launched Youtube", "info")
    # Close cookies pop-up
    try:
        accept_button = WebDriverWait(driver, 5).until(
            ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Accept all')]]"))
        )
        accept_button.click()
        message_logger("Clicked on accept all button to close the cookies pop-up", "info")
    except Exception as e:
        message_logger(f"Could not find or click 'Accept All' button: {e}", "error")

    # Wait for cookies to be visible
    time.sleep(3)


def search_video(driver, query):
    # Search a video
    search_box = driver.find_element(By.NAME, "search_query")
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    message_logger(f"Searching video with title: {query}", "info")

    # Wait for videos result
    WebDriverWait(driver, 10).until(
        ec.presence_of_element_located((By.ID, "video-title"))
    )

    message_logger("Waiting for video results", "info")


def click_video(driver):
    # Click on video
    first_video = driver.find_element(By.ID, "video-title")
    first_video.click()
    message_logger("Clicked on the first video", "info")

    message_logger("Clicked on the first video", "info")

    # Wait for the video
    message_logger("Wait for the video to be played", "info")
    time.sleep(120)

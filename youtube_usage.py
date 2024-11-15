import sys

from selenium import webdriver
from selenium.common import WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from youtube_logger import YoutubeLogger
import time
import requests


class YoutubeUsage:
    def __init__(self):
        self.youtube_logger = YoutubeLogger(file_path="log_script.log", file_name="log_script.log")
        # Set Chrome options to start in full-screen mode
        chrome_options = Options()
        chrome_options.add_argument("--start-fullscreen")

        # self.check_network()
        # Configure Chrome drive
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Chrome driver configured")
        except WebDriverException as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Error during driver setup: {e}")
            sys.exit(1)
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Unexpected error: {e}")
            sys.exit(1)

    def check_network(self):
        try:
            requests.head(url="https://www.google.com", timeout=5)
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Network connection is available.")
        except requests.ConnectionError:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, "Network connection is not "
                                                                                   "available.")
            sys.exit(1)

    def use_youtube(self):
        # Launch YouTube
        try:
            self.driver.get("https://www.youtube.com")
            time.sleep(5)
            page_state = self.driver.execute_script('return document.readyState;')
            if page_state == 'complete':
                self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Launched Youtube")
                # Close cookies pop-up
                try:
                    accept_button = WebDriverWait(self.driver, 5).until(
                        ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Accept all')]]"))
                    )
                    accept_button.click()
                    self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Clicked on accept all "
                                                                                          "button to close the "
                                                                                          "cookies pop-up")
                    time.sleep(3)
                except Exception as e:
                    self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                    f"Could not find or click 'Accept All' button: {e}")
            else:
                self.youtube_logger.log_message(self.youtube_logger.Level.WARNING.value,
                                                "YouTube page wasn't loaded in 5 "
                                                "seconds")
                sys.exit(1)
        except WebDriverException as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Error: Network is unavailable. Browser cannot load the page: {e}")
            self.driver.quit()
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Unexpected error: {e}")
            self.driver.quit()

    def search_video(self):
        query: str = "Selenium"
        # Search a video
        search_box = self.driver.find_element(By.NAME, "search_query")
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)

        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        f"Searching video with title: {query}")

        # Wait for videos result
        WebDriverWait(self.driver, 10).until(
            ec.presence_of_element_located((By.ID, "video-title"))
        )
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "Waiting for video results")

    def click_video(self):
        # Click on video
        first_video = self.driver.find_element(By.ID, "video-title")
        first_video.click()
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "Clicked on the first video")

        # Wait for the video
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "Wait for the video to be played")
        time.sleep(30)

    def usage(self):
        self.use_youtube()
        self.search_video()
        self.click_video()
        self.driver.close()

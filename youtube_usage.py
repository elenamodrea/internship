import threading
import time
from selenium import webdriver
from selenium.common import WebDriverException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from youtube_logger import YoutubeLogger


class YoutubeUsage:
    def __init__(self, youtube_logger: YoutubeLogger):
        """
        initialize the YoutubeUsage class and configure the Chrome driver
        :param youtube_logger: used for logging information
        :return: None
        """
        self.youtube_logger = youtube_logger
        # Set Chrome options to start in maximized mode
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        self.driver = None
        # used to stop the video after 2 minutes have passed
        self.stop_youtube = threading.Event()
        # Configure Chrome driver
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Chrome driver configured")
        except WebDriverException as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Error during driver setup: {e}")
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Unexpected error: {e}")

    def __use_youtube(self):
        """
        Method used to launch YouTube and accept the cookies pop-up
        :return: None
        """
        # Launch YouTube
        try:
            self.driver.get("https://www.youtube.com")
            WebDriverWait(self.driver, 5).until(
                lambda driver: driver.execute_script('return document.readyState;') == 'complete'
            )

            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Launched Youtube")
            # Close cookies pop-up
            try:
                # Wait max 5 seconds for the button 'Accept all' to appear
                accept_button = WebDriverWait(self.driver, 5).until(
                    ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Accept all')]]"))
                )
                accept_button.click()
                self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                                "Clicked on accept all button to close the cookies pop-up")
                # Wait for 3 second to close the pop-up
                time.sleep(3)
            except Exception as e:
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                f"Could not find or click 'Accept All' button: {e}")
                raise Exception("Could not find or click 'Accept All'")

        except TimeoutException:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            "YouTube page wasn't loaded in 5 seconds")
            self.driver.quit()
            raise TimeoutException("YouTube page wasn't loaded in 5 seconds")
        except WebDriverException as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Error: Browser cannot load the page: {e}")
            self.driver.quit()
            raise WebDriverException("Browser cannot load the page: " + str(e))
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Unexpected error: {e}")
            self.driver.quit()
            raise

    def __search_video(self):
        """
        Method used to search a video using the query and wait for video results
        :return: None
        """
        query: str = "Selenium python"
        try:
            # Search a video
            search_box = self.driver.find_element(By.NAME, "search_query")
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)

            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                            f"Searching video with title: {query}")

            # Wait max 10 seconds for videos result
            WebDriverWait(self.driver, 10).until(
                ec.presence_of_element_located((By.ID, "video-title"))
            )
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                            "Waiting for video results")
        except TimeoutException:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            "Timeout exception occurred while waiting for video results")
            raise TimeoutException("Timeout exception occurred while waiting for video results")
        except WebDriverException:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            "Network connection lost. Please check your internet and try again.")
            raise WebDriverException("Network connection lost. Please check your internet and try again.")
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Exception occurred while waiting for video: {e}")
            raise

    def __click_video(self):
        """
        Method used to click the first video in the video results and put it in full-screen mode
        Also it checks if the video has stopped and close the premium pop-up if it appears.
        :return: None
        """
        # Click on the first video
        first_video = self.driver.find_element(By.ID, "video-title")
        first_video.click()

        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "Clicked on the first video")

        # Wait for the video to be played
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "Waiting for the video to play")

        try:
            # Wait for full-screen button to appear and click on it
            full_screen_button = WebDriverWait(self.driver, 5).until(
                ec.element_to_be_clickable((By.XPATH, "//button[@class='ytp-fullscreen-button ytp-button']"))
            )
            full_screen_button.click()
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                            "Video is now in full screen.")
        except TimeoutException:
            self.youtube_logger.log_message(self.youtube_logger.Level.WARNING.value,
                                            f"Unable to click full-screen button:")

        # Continuously check if the video is stuck until the program stops
        while not self.stop_youtube.is_set():
            if self.driver is None or not self.driver.session_id:  # Ensure driver is valid
                self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Browser closed. Exiting loop.")
                break
            self.__premium_popup()
            if self.is_video_stuck():
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                "The video is stuck, check playback or the driver is closed")
                raise Exception("The video is stuck, check playback or the driver is closed.")
            time.sleep(1)  # Check every second

    def __premium_popup(self):
        """
        Method used to check if there is a premium pop-up visible and close it if it is
        :return: None
        """
        try:
            # Wait for the pop-up to appear within a second
            no_premium_button = WebDriverWait(self.driver, 1).until(
                ec.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'No thanks')]]"))
            )
            # If the pop-up appears, click the "No thanks" button to close it
            no_premium_button.click()
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Pop-up closed successfully.")
        # if there is no pop-up visible it is not a problem
        except TimeoutException:
            pass
        except Exception:
            pass

    def is_video_stuck(self):
        """
        Method used to check if the video is stuck, and it doesn't progress
        :return True: if the video progressed
        :return False: if the video is stuck
        """
        # if the driver doesn't exist anymore return the method
        if self.driver is None or not self.driver.session_id:
            return False
        try:
            # get the video that is playing
            video_element = self.driver.find_element(By.CSS_SELECTOR, "video")
            # get the current time of the video
            current_time = self.driver.execute_script("return arguments[0].currentTime;", video_element)

            # Initialize previous_time and stuck_count if they do not exist
            if not hasattr(self, "_previous_time"):
                self._previous_time = current_time
                # Initialize counter for stuck checks
                self._stuck_count = 0

            # Check if the video has not progressed
            if current_time == self._previous_time:
                self._stuck_count += 1
                if self._stuck_count >= 3:  # If it is stuck for 3 consecutive checks
                    self.youtube_logger.log_message(self.youtube_logger.Level.WARNING.value,
                                                    "The video might be stuck (no progress detected).")
                    # Reset previous time
                    self._previous_time = current_time
                    return True
            else:
                # Reset the stuck count if the video is progressing
                self._stuck_count = 0

            # Update the previous time for next iteration
            self._previous_time = current_time
            return False

        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                            f"Error checking video progress: {e}")
            raise Exception("Error checking video progress")

    def usage(self, stop_event: threading.Event):
        """
        Method that performs the full process of interacting with YouTube using Selenium.
        It launches YouTube, searches for a video, clicks on it, and continuously monitors
        the video playback until a stop condition is met.
        :param stop_event: a threading.Event used to signal when the browser should stop
        :return: None
        """
        # if the driver isn't configured then don't proceed and raise an Exception
        if self.driver is not None:
            # initialize timer to wait for 2 minutes
            timeout_thread = threading.Timer(120, self.__timeout_reached)
            self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Started Selenium.")
            # Start the timer
            timeout_thread.start()
            try:
                # Exit if stop_event is set
                if stop_event.is_set():
                    raise Exception

                self.__use_youtube()

                if stop_event.is_set():
                    raise Exception

                self.__search_video()

                if stop_event.is_set():
                    raise Exception

                self.__click_video()

                if stop_event.is_set():
                    raise Exception

            except TimeoutException as e:
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                f"Timeout Error during usage: {e}")
                # set the event to stop the video playback
                self.stop_youtube.set()
                # Close the browser
                self.driver.quit()
                # stop the timeout due to the error
                timeout_thread.cancel()
                # raise the exception to be caught in main
                raise
            except WebDriverException as e:
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value,
                                                f"WebDriver Error during usage: {e}")
                # set the event to stop the video playback
                self.stop_youtube.set()
                # Close the browser
                self.driver.quit()
                # stop the timeout due to the error
                timeout_thread.cancel()
                # raise the exception to be caught in main
                raise
            except Exception as e:
                self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Error during usage: {e}")
                # set the event to stop the video playback
                self.stop_youtube.set()
                # Close the browser
                self.driver.quit()
                # stop the timeout due to the error
                timeout_thread.cancel()
                # raise the exception to be caught in main
                raise
        else:
            raise Exception("No driver")

    def __timeout_reached(self):
        """
        Method used when the timeout is reached to close the browser
        :return: None
        """
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                        "120 seconds have passed. Stopping execution.")
        # set the event to stop the video playback
        self.stop_youtube.set()
        if self.driver:
            # Close the browser
            self.driver.quit()
            self.driver = None

from youtube_usage import initialize, use_youtube, search_video, click_video
from log import message_logger
import time


def main():
    driver = initialize()
    try:
        use_youtube(driver)

        # Get search query from the user
        query = input("Enter youtube title: ")
        message_logger(f"Entered youtube query: {query}", "info")
        search_video(driver, query)
        click_video(driver)
        time.sleep(5)

    except Exception as e:
        message_logger(f"Unexpected error: {e}", 'error')

    finally:
        driver.quit()
        message_logger("Ended the session", 'info')


if __name__ == "__main__":
    main()

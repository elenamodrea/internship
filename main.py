import threading
import time

from selenium.common import TimeoutException

from audio_video_helper import AudioVideoHelper
from youtube_usage import YoutubeUsage
from audio_recorder import AudioRecorder
from screen_recorder import ScreenRecorder
from youtube_logger import YoutubeLogger


def main():
    """
    Main function to initialize and manage the execution of audio and video recording,
    as well as interaction with YouTube through Selenium.
    Creates a shared event used to signal stopping the threads.
    Monitors the threads.
    Ensures all threads are joined and resources are cleaned up after execution.
    """
    # Initialize classes
    youtube_logger = YoutubeLogger(file_path="log_script.log", file_name="log_script.log")
    audio_recorder = AudioRecorder(youtube_logger)
    screen_recorder = ScreenRecorder(youtube_logger)
    youtube_usage = YoutubeUsage(youtube_logger)
    audio_video_helper = AudioVideoHelper(youtube_logger)

    # Create a shared event for stopping threads
    stop_event = threading.Event()

    # Define target functions with exception handling
    def safe_audio_record():
        try:
            audio_recorder.record_audio(stop_event)
        except Exception as e:
            audio_recorder.youtube_logger.log_message(audio_recorder.youtube_logger.Level.ERROR.value,
                                                      f"Audio recording thread stopped due to error: {e}")
            # Signal other threads to stop
            stop_event.set()

    def safe_video_record():
        try:
            screen_recorder.recording(stop_event)
        except Exception as e:
            screen_recorder.youtube_logger.log_message(screen_recorder.youtube_logger.Level.ERROR.value,
                                                       f"Video recording thread stopped due to error: {e}")
            # Signal other threads to stop
            stop_event.set()

    def safe_youtube_usage():
        try:
            youtube_usage.usage(stop_event)
        except TimeoutException as e:
            youtube_usage.youtube_logger.log_message(
                youtube_usage.youtube_logger.Level.ERROR.value,
                f"Timeout occurred in YouTube usage: {e}"
            )
            # Signal other threads to stop
            stop_event.set()
        except Exception as e:
            youtube_usage.youtube_logger.log_message(youtube_usage.youtube_logger.Level.ERROR.value,
                                                     f"YouTube usage stopped due to error: {e}")
            # Signal other threads to stop
            stop_event.set()
        finally:
            youtube_usage.youtube_logger.log_message(
                youtube_usage.youtube_logger.Level.INFO.value,
                "YouTube thread has completed its execution."
            )

    # Start youtube_usage, audio and video recording in separate threads
    audio_thread = threading.Thread(target=safe_audio_record)
    video_thread = threading.Thread(target=safe_video_record)
    youtube_thread = threading.Thread(target=safe_youtube_usage)

    try:
        audio_thread.start()
        video_thread.start()
        youtube_thread.start()

        # Monitor threads and stop if the event is set
        while not stop_event.is_set():
            if not (audio_thread.is_alive() and video_thread.is_alive() and youtube_thread.is_alive()):
                break
            time.sleep(0.1)

            # If the stop_event is set exit gracefully
        if stop_event.is_set():
            youtube_logger.log_message(youtube_usage.youtube_logger.Level.ERROR.value, "Exited the program due to an "
                                                                                       "error")

    finally:
        # Ensure threads finish and resources are cleaned up
        audio_thread.join()
        video_thread.join()
        youtube_thread.join()
        if youtube_usage.driver is not None:
            youtube_usage.driver.quit()
        audio_video_helper.merge_audio_video()
        audio_video_helper.analyze_audio("audio_record.wav")


if __name__ == "__main__":
    main()

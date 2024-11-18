import threading
import time
import cv2
import numpy as np
import pyautogui
from youtube_logger import YoutubeLogger


class ScreenRecorder:
    def __init__(self, youtube_logger: YoutubeLogger):
        """
        Initializes the ScreenRecorder class and sets up the video recording parameters: screen resolution,
        the codec for video encoding initializes the video writer object, and sets the recording duration.

       :param youtube_logger: used for logging information
       :return: None
        """
        self.youtube_logger = youtube_logger
        # display screen resolution
        self.screen_size = tuple(pyautogui.size())
        # define the codec
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        # sets the number of frames per second
        self.fps = 24.0
        # create the video write object
        self.out = cv2.VideoWriter("output.avi", self.fourcc, self.fps, self.screen_size)
        # record time in seconds
        self.record_seconds = 120

    def recording(self, stop_event: threading.Event):
        """
            Records the screen for 2 minutes and writes the frames to a video file.
            It stops either when 2 minutes are reached or when the `stop_event` is triggered.

            :param stop_event: a threading.Event used to signal when the recording should stop.
            :return: None
            """
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Started recording video")
        # track the start time
        start_time = time.time()
        # get the total number of the frames
        total_frames = int(self.record_seconds * self.fps)
        current_frame = 0
        try:
            while current_frame < total_frames:
                # if the event is set, the recording stops
                if stop_event.is_set():
                    self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value,
                                                    "Video recording stopped due to an event signal.")
                    break
                # take a screenshot
                img = pyautogui.screenshot()
                frame = np.array(img)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.out.write(frame)
                current_frame += 1

                elapsed_time = time.time() - start_time
                # Stop recording once the desired time has passed
                if elapsed_time >= self.record_seconds:
                    break

                # Maintain FPS timing
                time_to_wait = (current_frame + 1) / self.fps - elapsed_time
                if time_to_wait > 0:
                    time.sleep(time_to_wait)
        except Exception as e:
            self.youtube_logger.log_message(self.youtube_logger.Level.ERROR.value, f"Error while recording video: {e}")
            raise

        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Video recording ended")
        self.out.release()
        cv2.destroyAllWindows()

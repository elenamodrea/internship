import time

import cv2
import numpy as np
import pyautogui
from youtube_logger import YoutubeLogger


class ScreenRecorder:
    def __init__(self):
        self.youtube_logger = YoutubeLogger(file_path="log_script.log", file_name="log_script.log")
        # display screen resolution
        self.screen_size = tuple(pyautogui.size())
        # define the codec
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.fps = 24.0
        # create the video write object
        self.out = cv2.VideoWriter("output.avi", self.fourcc, self.fps, self.screen_size)
        # record time in seconds
        self.record_seconds = 30

    def recording(self):
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Started recording video")
        for i in range(int(self.record_seconds * self.fps)):
            # make a screenshot
            img = pyautogui.screenshot()
            # convert these pixels to a proper numpy array to work with OpenCV
            frame = np.array(img)
            # convert colors from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # write the frame
            self.out.write(frame)
        # make sure everything is closed when exited
        self.youtube_logger.log_message(self.youtube_logger.Level.INFO.value, "Video recording ended")
        cv2.destroyAllWindows()
        self.out.release()

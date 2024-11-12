import time

import cv2
import numpy as np
import pyautogui


def recording():
    # display screen resolution, get it using pyautogui itself
    screen_size = tuple(pyautogui.size())
    # define the codec
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    # frames per second
    fps = 24.0
    # create the video write object
    out = cv2.VideoWriter("output.avi", fourcc, fps, screen_size)
    # the time you want to record in seconds
    record_seconds = 120

    for i in range(int(record_seconds * fps)):
        # make a screenshot
        img = pyautogui.screenshot()
        # convert these pixels to a proper numpy array to work with OpenCV
        frame = np.array(img)
        # convert colors from BGR to RGB
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # write the frame
        out.write(frame)
    # make sure everything is closed when exited
    cv2.destroyAllWindows()
    out.release()


class ScreenRecorder:
    pass

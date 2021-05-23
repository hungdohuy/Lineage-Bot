import numpy as np
import os
import pygetwindow as pgw

from threading import Lock, Thread
from mss import mss
from time import time


class WindowCapture:

    # properties
    stopped = True
    lock = None
    screenshot = None
    w = 0
    h = 0
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0
    buff_bar_pos = (0, 0)
    fps = 1
    screen = mss()
    region = None

    def __init__(self, window_title, border_pixels, titlebar_pixels):
        self.lock = Lock()
        l2windows = pgw.getWindowsWithTitle(window_title)[0]
        self.offset_x, self.offset_y = l2windows.topleft

        self.cropped_x = border_pixels + self.offset_x
        self.cropped_y = titlebar_pixels + self.offset_y

        self.w = l2windows.width
        self.h = l2windows.height
        self.region = {'top': self.offset_y, 'left': self.offset_x,
                       'width': self.w, 'height': self.h}

    def set_buff_bar_pos(self, buff_bar_pos):
        self.buff_bar_pos = buff_bar_pos

    def get_screenshot(self):
        img = np.array(self.screen.grab(self.region))
        # hide buff bar
        # (y:h+y, x:w+x)
        img[int(self.buff_bar_pos[1]):105 + int(self.buff_bar_pos[1]),
            int(self.buff_bar_pos[0]):325 + int(self.buff_bar_pos[0])] = (0, 0, 0, 0)
        return img

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        while not self.stopped:
            start = time()
            screenshot = self.get_screenshot()
            with self.lock:
                self.screenshot = screenshot
            self.fps = round(1.0 / (time() - start), 1)

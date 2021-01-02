import numpy as np


class Frame:
    def __init__(self, screen: np.ndarray, duration: int = 1):
        self.screen = screen
        self.duration = duration

    def output(self):
        return np.array([self.screen] * self.duration, dtype=np.uint8)

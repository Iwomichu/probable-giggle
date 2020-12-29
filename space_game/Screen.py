from typing import Tuple

from numpy import zeros, array, uint8
from pygame.surfarray import make_surface
from pygame import Surface


class Screen:
    def __init__(self, width: int, height: int, n_channels: int) -> None:
        self.width = width
        self.height = height
        self.n_channels = n_channels
        self.screen = zeros((self.width, self.height, self.n_channels), dtype=uint8)

    def reset_screen(self) -> None:
        self.screen = zeros((self.width, self.height, self.n_channels), dtype=uint8)

    def draw_rect(self, x: int, width: int, y: int, height: int, pxl: Tuple[int, int, int]) -> None:
        self.screen[x:x+width, y:y+height] = array(pxl)

    def convert_to_pygame_surface(self) -> Surface:
        return make_surface(self.screen)

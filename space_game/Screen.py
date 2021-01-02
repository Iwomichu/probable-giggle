from typing import Tuple

from PIL.Image import fromarray
from numpy import zeros, array, uint8, expand_dims
from pygame.surfarray import make_surface
from pygame import Surface


class Screen:
    def __init__(self, width: int, height: int, n_channels: int, scaled_height: int, scaled_width: int) -> None:
        self.width = width
        self.height = height
        self.n_channels = n_channels
        self.screen = zeros((self.width, self.height, self.n_channels), dtype=uint8)
        self.scaled_height = scaled_height
        self.scaled_width = scaled_width

    def reset_screen(self) -> None:
        self.screen = zeros((self.width, self.height, self.n_channels), dtype=uint8)

    def draw_rect(self, x: int, width: int, y: int, height: int, pxl: Tuple[int, int, int]) -> None:
        self.screen[x:x+width, y:y+height] = array(pxl)

    def convert_to_pygame_surface(self) -> Surface:
        return make_surface(self.screen)

    def process_map(self):
        array_processed = array(fromarray(self.screen).convert('L').resize(
            size=(self.scaled_height, self.scaled_width)))
        return expand_dims(array_processed, axis=-1)

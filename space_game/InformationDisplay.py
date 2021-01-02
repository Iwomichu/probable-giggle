from typing import Any

from space_game.Screen import Screen
from space_game.interfaces.Drawable import Drawable
from space_game.Player import Player


def calculate_relative_value(current_value, min_value, max_value, to_int=False, steps=5):
    new_value = (current_value - min_value) / (max_value - min_value)
    if to_int:
        new_value = round(new_value*steps)
    return new_value


class InformationDisplay(Drawable):
    def __init__(self, player_1: Player, player_2: Player, config):
        self.player_1 = player_1
        self.player_2 = player_2
        self.config = config

    def draw(self, screen: Screen):
        screen.draw_rect(
            0,
            20 * max(self.player_1.hitpoints, 0),
            0,
            20,
            (255, 255, 255)
        )
        screen.draw_rect(
            0,
            20 * max(self.player_2.hitpoints, 0),
            self.config.height - 20,
            20,
            (255, 255, 255)
        )

        screen.draw_rect(
            20 * self.config.max_hitpoints + 10,
            20 * self.player_1.ammo_left,
            0,
            20,
            (255, 255, 255)
        )
        screen.draw_rect(
            20 * self.config.max_hitpoints + 10,
            20 * self.player_2.ammo_left,
            self.config.height - 20,
            20,
            (255, 255, 255)
        )

        screen.draw_rect(
            20 * self.config.max_hitpoints + 20 * self.config.ammo_maximum + 20,
            (20 * 4) if self.player_1.shoot_countdown else 0,
            0,
            20,
            (255, 255, 255)
        )
        screen.draw_rect(
            20 * self.config.max_hitpoints + 20 * self.config.ammo_maximum + 20,
            (20 * 4) if self.player_2.shoot_countdown else 0,
            self.config.height - 20,
            20,
            (255, 255, 255)
        )

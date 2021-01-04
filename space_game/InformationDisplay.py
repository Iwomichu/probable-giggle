from typing import Any

from space_game.Config import Config
from space_game.Screen import Screen
from space_game.interfaces.Drawable import Drawable
from space_game.Player import Player


def calculate_relative_value(current_value, min_value, max_value, to_int=False, steps=5):
    new_value = (current_value - min_value) / (max_value - min_value)
    if to_int:
        new_value = round(new_value*steps)
    return new_value


class InformationDisplay(Drawable):
    def __init__(self, player_1: Player, player_2: Player, config: Config):
        self.player_1 = player_1
        self.player_2 = player_2
        self.config = config

    def draw(self, screen: Screen):
        screen.draw_rect(
            0,
            self.config.information_display_box_size * max(self.player_1.hitpoints, 0),
            0,
            self.config.information_display_box_size,
            (255, 255, 255)
        )
        screen.draw_rect(
            0,
            self.config.information_display_box_size * max(self.player_2.hitpoints, 0),
            self.config.height - self.config.information_display_box_size,
            self.config.information_display_box_size,
            (255, 255, 255)
        )

        screen.draw_rect(
            self.config.information_display_box_size * self.config.max_hitpoints + self.config.information_display_box_size,
            self.config.information_display_box_size * self.player_1.ammo_left,
            0,
            self.config.information_display_box_size,
            (255, 255, 255)
        )
        screen.draw_rect(
            self.config.information_display_box_size * self.config.max_hitpoints + self.config.information_display_box_size,
            self.config.information_display_box_size * self.player_2.ammo_left,
            self.config.height - self.config.information_display_box_size,
            self.config.information_display_box_size,
            (255, 255, 255)
        )

        screen.draw_rect(
            self.config.information_display_box_size * self.config.max_hitpoints + self.config.information_display_box_size * self.config.ammo_maximum + self.config.information_display_box_size,
            (self.config.information_display_box_size * 4) if self.player_1.shoot_countdown else 0,
            0,
            self.config.information_display_box_size,
            (255, 255, 255)
        )
        screen.draw_rect(
            self.config.information_display_box_size * self.config.max_hitpoints + self.config.information_display_box_size * self.config.ammo_maximum + self.config.information_display_box_size,
            (self.config.information_display_box_size * 4) if self.player_2.shoot_countdown else 0,
            self.config.height - self.config.information_display_box_size,
            self.config.information_display_box_size,
            (255, 255, 255)
        )

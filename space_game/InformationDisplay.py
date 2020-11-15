from typing import Any

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

    def draw(self, window: Any):
        p1_hp = self.config.font.render(f"{'X' * self.player_1.hitpoints}", 1, (255, 255, 255))
        p2_hp = self.config.font.render(f"{'X' *self.player_2.hitpoints}", 1, (255, 255, 255))
        window.blit(p1_hp, (5 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_hp, (5 * self.config.scale, self.config.height - 25 * self.config.scale))
        p1_ammo = self.config.font.render(f"{'█' * self.player_1.ammo_left}", 1, (255, 255, 255))
        p2_ammo = self.config.font.render(f"{'█' * self.player_2.ammo_left}", 1, (255, 255, 255))
        window.blit(p1_ammo, (70 * self.config.scale, 10))
        window.blit(p2_ammo, (70 * self.config.scale, self.config.height - 25))
        p1_cooldown = self.config.font.render(f"{'X' if self.player_1.shoot_countdown != 0 else 'OK'}", 1,
                                              (255, 255, 255))
        p2_cooldown = self.config.font.render(f"{'X' if self.player_2.shoot_countdown != 0 else 'OK'}", 1,
                                              (255, 255, 255))
        window.blit(p1_cooldown, (160 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_cooldown, (160 * self.config.scale, self.config.height - 25 * self.config.scale))

        p1_left_velocity = -calculate_relative_value(self.player_1.entity.horizontal_velocity, 0, self.config.max_velocity, True)
        p1_right_velocity = calculate_relative_value(self.player_1.entity.horizontal_velocity, 0, self.config.max_velocity, True)
        p1_up_velocity = -calculate_relative_value(self.player_1.entity.vertical_velocity, 0, self.config.max_velocity, True)
        p1_down_velocity = calculate_relative_value(self.player_1.entity.vertical_velocity, 0, self.config.max_velocity, True)
        p2_left_velocity = -calculate_relative_value(self.player_2.entity.horizontal_velocity, 0, self.config.max_velocity, True)
        p2_right_velocity = calculate_relative_value(self.player_2.entity.horizontal_velocity, 0, self.config.max_velocity, True)
        p2_up_velocity = -calculate_relative_value(self.player_2.entity.vertical_velocity, 0, self.config.max_velocity, True)
        p2_down_velocity = calculate_relative_value(self.player_2.entity.vertical_velocity, 0, self.config.max_velocity, True)

        p1_right_velocity_rendered = self.config.font.render(f"{'>'*p1_right_velocity}", 1,
                                                       (255, 255, 255))
        p1_left_velocity_rendered = self.config.font.render(f"{'<'*p1_left_velocity}", 1,
                                                       (255, 255, 255))
        p1_up_velocity_rendered = self.config.font.render(f"{'^'*p1_up_velocity}", 1,
                                                       (255, 255, 255))
        p1_down_velocity_rendered = self.config.font.render(f"{'v'*p1_down_velocity}", 1,
                                                       (255, 255, 255))
        p2_right_velocity_rendered = self.config.font.render(f"{'>'*p2_right_velocity}", 1,
                                                       (255, 255, 255))
        p2_left_velocity_rendered = self.config.font.render(f"{'<'*p2_left_velocity}", 1,
                                                       (255, 255, 255))
        p2_up_velocity_rendered = self.config.font.render(f"{'^'*p2_up_velocity}", 1,
                                                       (255, 255, 255))
        p2_down_velocity_rendered = self.config.font.render(f"{'v'*p2_down_velocity}", 1,
                                                       (255, 255, 255))
        window.blit(p1_left_velocity_rendered, ((260 - 10 * p1_left_velocity) * self.config.scale, 10 * self.config.scale))
        window.blit(p1_right_velocity_rendered, (260 * self.config.scale, 10 * self.config.scale))
        window.blit(p1_up_velocity_rendered, (335 * self.config.scale, 10 * self.config.scale))
        window.blit(p1_down_velocity_rendered, (335 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_left_velocity_rendered, ((260 - 10 * p2_left_velocity) * self.config.scale, self.config.height - 25 * self.config.scale))
        window.blit(p2_right_velocity_rendered, (260 * self.config.scale, self.config.height - 25 * self.config.scale))
        window.blit(p2_up_velocity_rendered, (335 * self.config.scale, self.config.height - 25 * self.config.scale))
        window.blit(p2_down_velocity_rendered, (335 * self.config.scale, self.config.height - 25 * self.config.scale))

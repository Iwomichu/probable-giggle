from typing import Any

from space_game.interfaces.Drawable import Drawable
from space_game.Player import Player


class InformationDisplay(Drawable):
    def __init__(self, player_1: Player, player_2: Player, config):
        self.player_1 = player_1
        self.player_2 = player_2
        self.config = config

    def draw(self, window: Any):
        p1_hp = self.config.font.render(f"HP: {self.player_1.hitpoints}", 1, (255, 255, 255))
        p2_hp = self.config.font.render(f"HP: {self.player_2.hitpoints}", 1, (255, 255, 255))
        window.blit(p1_hp, (5 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_hp, (5 * self.config.scale, self.config.height - 25 * self.config.scale))
        p1_ammo = self.config.font.render(f"Ammo: {self.player_1.ammo_left}", 1, (255, 255, 255))
        p2_ammo = self.config.font.render(f"Ammo: {self.player_2.ammo_left}", 1, (255, 255, 255))
        window.blit(p1_ammo, (50 * self.config.scale, 10))
        window.blit(p2_ammo, (50 * self.config.scale, self.config.height - 25))
        p1_cooldown = self.config.font.render(f"CD: {'X' if self.player_1.shoot_countdown != 0 else 'OK'}", 1,
                                              (255, 255, 255))
        p2_cooldown = self.config.font.render(f"CD: {'X' if self.player_2.shoot_countdown != 0 else 'OK'}", 1,
                                              (255, 255, 255))
        window.blit(p1_cooldown, (110 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_cooldown, (110 * self.config.scale, self.config.height - 25 * self.config.scale))
        p1_vertical_velocity = self.config.font.render(f"vertical velocity: {self.player_1.entity.vertical_velocity}", 1,
                                                       (255, 255, 255))
        p2_vertical_velocity = self.config.font.render(f"vertical velocity: {self.player_2.entity.vertical_velocity}", 1,
                                                       (255, 255, 255))
        window.blit(p1_vertical_velocity, (150 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_vertical_velocity,
                                (150 * self.config.scale, self.config.height - 25 * self.config.scale))
        p1_horizontal_velocity = self.config.font.render(f"horizontal velocity: {self.player_1.entity.horizontal_velocity}",
                                                         1, (255, 255, 255))
        p2_horizontal_velocity = self.config.font.render(f"horizontal velocity: {self.player_2.entity.horizontal_velocity}",
                                                         1, (255, 255, 255))
        window.blit(p1_horizontal_velocity, (275 * self.config.scale, 10 * self.config.scale))
        window.blit(p2_horizontal_velocity,
                                (275 * self.config.scale, self.config.height - 25 * self.config.scale))

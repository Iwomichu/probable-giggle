from dataclasses import dataclass

import pygame

from space_game.domain_names import Constraint

pygame.init()


@dataclass()
class Config:
    scale = 1
    width = 400 * scale
    height = 400 * scale
    player_size = 25 * scale
    player_1_width_constraint = Constraint(0, width)
    player_1_height_constraint = Constraint(25 * scale, height / 2)
    player_2_width_constraint = Constraint(0, width)
    player_2_height_constraint = Constraint(height / 2, height - 25 * scale)
    player_1_color = (255, 0, 0)
    player_2_color = (0, 0, 255)
    player_1_bullet_color = (255, 127, 0)
    player_2_bullet_color = (0, 127, 255)
    bullet_width = 3 * scale
    bullet_height = 5 * scale
    shoot_cooldown = 10
    ammo_maximum = 10
    ammo_countdown = 80
    max_velocity = 8.
    bullet_velocity = 10.
    window = pygame.display.set_mode((width, height))
    fps = 20
    font = pygame.font.SysFont("arial", 10 * scale)
    player_acceleration = .25
    ai_input_lag = 0  # amount of frames AI has to wait to act
    scaled_width = 64
    scaled_height = 64

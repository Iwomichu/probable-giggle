from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict, Any

from yaml import safe_load, YAMLError

import pygame

from constants import CONFIGS_DIRECTORY
from space_game.domain_names import Constraint

pygame.init()


@dataclass
class Config:
    scale: int
    width: int
    height: int
    player_size: int
    player_1_width_constraint: Constraint
    player_1_height_constraint: Constraint
    player_2_width_constraint: Constraint
    player_2_height_constraint: Constraint
    player_1_color: Tuple[int]
    player_2_color: Tuple[int]
    player_1_bullet_color: Tuple[int]
    player_2_bullet_color: Tuple[int]
    bullet_width: int
    bullet_height: int
    shoot_cooldown: int
    ammo_maximum: int
    ammo_countdown: int
    max_velocity: int
    bullet_velocity: int
    fps: int
    player_acceleration: int
    ai_input_lag: int  # amount of frames AI has to wait to act
    scaled_width: int
    scaled_height: int
    max_hitpoints: int
    information_display_box_size: int

    @staticmethod
    def default():
        with open(CONFIGS_DIRECTORY / "space_game_config.default.yml", 'r') as f:
            try:
                config_file = safe_load(f)
                return Config.from_config_dict(config_file)
            except YAMLError as exc:
                print("space game config loading failed. stacktrace:")
                print(exc)

    @staticmethod
    def custom(path: Path):
        with open(path, 'r') as f:
            try:
                config_file = safe_load(f)
                return Config.from_config_dict(config_file)
            except YAMLError as exc:
                print("space game config loading failed. stacktrace:")
                print(exc)

    @staticmethod
    def unified():
        return Config.custom(CONFIGS_DIRECTORY / "unified_space_game_config.yml")

    @staticmethod
    def from_config_dict(config_dict: Dict[str, Any]):
        return Config(
            scale=config_dict['scale'],
            width=config_dict['base_width'],
            height=config_dict['base_height'],
            scaled_height=config_dict['compressed_height'],
            scaled_width=config_dict['compressed_width'],
            fps=config_dict['fps'],
            ai_input_lag=config_dict['ai_input_lag'],
            bullet_width=config_dict['bullet']['base_width'],
            bullet_height=config_dict['bullet']['base_height'],
            bullet_velocity=config_dict['bullet']['velocity'],
            ammo_maximum=config_dict['ammo']['maximum'],
            ammo_countdown=config_dict['ammo']['countdown'],
            shoot_cooldown=config_dict['ammo']['cooldown'],
            max_velocity=min(config_dict['player_1']['velocity'], config_dict['player_2']['velocity']),
            max_hitpoints=min(config_dict['player_1']['max_hitpoints'], config_dict['player_2']['max_hitpoints']),
            player_acceleration=min(config_dict['player_1']['acceleration'], config_dict['player_2']['acceleration']),
            player_size=min(config_dict['player_1']['base_size'], config_dict['player_2']['base_size']),
            player_1_width_constraint=Constraint(*config_dict['player_1']['x_constraint']),
            player_2_width_constraint=Constraint(*config_dict['player_2']['x_constraint']),
            player_1_height_constraint=Constraint(*config_dict['player_1']['y_constraint']),
            player_2_height_constraint=Constraint(*config_dict['player_2']['y_constraint']),
            player_1_bullet_color=tuple(config_dict['player_1']['bullet_color']),
            player_2_bullet_color=tuple(config_dict['player_2']['bullet_color']),
            player_1_color=tuple(config_dict['player_1']['color']),
            player_2_color=tuple(config_dict['player_2']['color']),
            information_display_box_size=config_dict['information_display_box_size']
        )


default_config = Config.default()

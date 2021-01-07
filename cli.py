from enum import Enum, auto
from pathlib import Path

import click

from space_game.Config import Config
from constants import CONFIGS_DIRECTORY
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameGymAPIEnvironment import SpaceGameEnvironment
from models.DQN.Config import Config as DQNConfig
from models.DQN.single_agent_training import train_model


@click.group()
def cli():
    pass


@cli.command()
@click.option('--game-config-file', default='space_game_config.default.yml', help='Filename of desired config for SpaceGame')
@click.option('--env-config-file', default='gym_api_env_config.default.yml', help='Filename of desired config for GymApi')
@click.option('--dqn-config-file', default='dqn_config.default.yml', help='Filename of desired config for Custom DQN')
def train_custom_dqn(game_config_file, env_config_file, dqn_config_file):
    space_game_config = Config.custom(CONFIGS_DIRECTORY / game_config_file)
    gym_api_env_config = SpaceGameEnvironmentConfig.custom(CONFIGS_DIRECTORY / env_config_file)
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / dqn_config_file)

    gym_api_env = SpaceGameEnvironment(game_config=space_game_config, environment_config=gym_api_env_config)
    train_model(env=gym_api_env, dqn_config=dqn_config)


if __name__ == '__main__':
    cli()

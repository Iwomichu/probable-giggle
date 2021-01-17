import click
import torch

from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from space_game.Config import Config
from constants import CONFIGS_DIRECTORY
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameGymAPIEnvironment import SpaceGameEnvironment
from models.DQN.Config import Config as DQNConfig
from models.DQN.single_agent_training import train_model
from models.DQN.self_play_training import train_model


@click.group()
def cli():
    pass


@cli.command()
@click.option('--game-config-file', default='unified_space_game_config.yml', help='Filename of desired config for SpaceGame')
@click.option('--env-config-file', default='unified_gym_api_env_config.yml', help='Filename of desired config for GymApi')
@click.option('--dqn-config-file', default='unified_dqn_config.yml', help='Filename of desired config for Custom DQN')
def train_custom_dqn(game_config_file, env_config_file, dqn_config_file):
    space_game_config = Config.custom(CONFIGS_DIRECTORY / game_config_file)
    gym_api_env_config = SpaceGameEnvironmentConfig.custom(CONFIGS_DIRECTORY / env_config_file)
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / dqn_config_file)

    gym_api_env = SpaceGameEnvironment(game_config=space_game_config, environment_config=gym_api_env_config)
    train_model(env=gym_api_env, dqn_config=dqn_config)


@cli.command()
@click.option('--saved-model-path', default=None, help='Filepath to trained DQN model')
def unified_self_play_dqn(saved_model_path: str):
    model = torch.load(saved_model_path) if saved_model_path else None

    space_game_config = Config.unified()
    gym_api_env_config = SpaceGameEnvironmentConfig.unified()
    dqn_config = DQNConfig.unified()

    self_play_env = SpaceGameSelfPlayEnvironment(space_game_config=space_game_config,
                                                 environment_config=gym_api_env_config)
    train_model(
        env=self_play_env,
        dqn_config=dqn_config,
        old_model=model
    )


if __name__ == '__main__':
    cli()

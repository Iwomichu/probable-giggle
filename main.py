import torch

# from space_game.Config import Config as GameConfig
# from space_game.Game import game
from constants import SAVED_MODELS_DIRECTORY, CONFIGS_DIRECTORY
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from models.DQN.self_play_training import train
from models.DQN.Config import Config as DQNConfig


def self_play_dqn_training():
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = False
    env = SpaceGameSelfPlayEnvironment(environment_config=env_config)
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / "custom_dqn_config.yml")
    trained_model = train(env=env, dqn_config=dqn_config)
    saving_path = SAVED_MODELS_DIRECTORY / "selfplay_dqn.pt"
    torch.save(trained_model, saving_path)


if __name__ == '__main__':
    self_play_dqn_training()

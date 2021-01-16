from datetime import datetime, timezone
from itertools import product
from pathlib import Path

import torch

from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from space_game.Game import Game
from space_game.Player import create_human_player_2, create_player_1
from space_game.PlayerTuple import PlayerTuple
from space_game.ai.CDQNController import CDQNController
from space_game.Config import Config
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameGymAPIEnvironment import SpaceGameEnvironment
from models.DQN.single_agent_training import train_model as single_train_model
from models.DQN.self_play_training import train_model as self_play_train_model
from models.DQN.Config import Config as DQNConfig
from constants import SAVED_MODELS_DIRECTORY, CONFIGS_DIRECTORY
from space_game.ai.RandomAI import RandomAI
from space_game.domain_names import Side


def space_game_only():
    game_config = Config.custom(CONFIGS_DIRECTORY / "bigger_space_game_config.yml")
    game = Game(game_config)
    game.start()


def train_dqn():
    game_config = Config.custom(CONFIGS_DIRECTORY / "bigger_space_game_config.yml")
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = False
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / "custom_dqn_config.yml")

    env = SpaceGameEnvironment(environment_config=env_config, game_config=game_config)
    single_train_model(env, dqn_config)


def space_game_with_c_dqn():
    game_config = Config.unified()
    game = Game(game_config)
    p1 = create_player_1(game_config, game.game_controller.event_manager)
    p2, p2_controller = create_human_player_2(game_config, game.game_controller.event_manager)
    c_dqn_controller = CDQNController(game.game_controller.event_manager, game_config,
                                      p1, p2, Side.UP, game.game_controller.screen,
                                      dqn_path=SAVED_MODELS_DIRECTORY / "CustomDQN_09-34-06_13-01-2021/dqn_down.pt")
    game.add_player_1(PlayerTuple(p1, None, c_dqn_controller))
    game.add_player_2(PlayerTuple(p2, p2_controller, None))
    game.start()


def self_play_dqn_training():
    game_config = Config.unified()
    env_config = SpaceGameEnvironmentConfig.unified()
    env_config.render = False
    env = SpaceGameSelfPlayEnvironment(space_game_config=game_config, environment_config=env_config)
    dqn_config = DQNConfig.unified()
    self_play_train_model(env=env, dqn_config=dqn_config)


def dqn_train_scenario_1():
    game_config = Config.custom(CONFIGS_DIRECTORY / "bigger_space_game_config.yml")
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = False
    env_config.use_simplified_environment_actions = True
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / "custom_dqn_config.yml")
    single_agent_env = SpaceGameEnvironment(environment_config=env_config, game_config=game_config)
    model = single_train_model(single_agent_env, dqn_config)
    dqn_config.games_total = 100
    self_play_env = SpaceGameSelfPlayEnvironment(environment_config=env_config, space_game_config=game_config)
    self_play_train_model(env=self_play_env, dqn_config=dqn_config, old_model=model)


def self_play_old_model(model_path: Path):
    model = torch.load(model_path)
    game_config = Config.custom(CONFIGS_DIRECTORY / "unified_space_game_config.yml")
    env_config = SpaceGameEnvironmentConfig.custom(CONFIGS_DIRECTORY / "continue_unified_gym_api_env_config.yml")
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / "continue_training_unified_dqn_config.yml")
    env = SpaceGameSelfPlayEnvironment(environment_config=env_config, space_game_config=game_config)
    gammas = [.999999]
    batch_sizes = [128]
    eps_decays = [.3]
    for gamma in gammas:
        dqn_config.gamma = gamma
        for batch_size in batch_sizes:
            dqn_config.batch_size = batch_size
            for eps_decay in eps_decays:
                dqn_config.eps_decay = eps_decay * dqn_config.games_total * 200
                run_id = f"C_DQN_{gamma}_{batch_size}_{eps_decay}_{datetime.now(tz=timezone.utc).strftime('%H-%M-%S_%d-%m-%Y')}"
                self_play_train_model(env, dqn_config, old_model=model, custom_train_id=run_id)


if __name__ == '__main__':
    self_play_dqn_training()

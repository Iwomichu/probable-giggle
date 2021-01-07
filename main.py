from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from space_game.Game import Game
from space_game.Player import create_human_player_2, create_player_1
from space_game.PlayerTuple import PlayerTuple
from space_game.ai.CDQNController import CDQNController
from space_game.Config import Config
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameGymAPIEnvironment import SpaceGameEnvironment
from models.DQN.single_agent_training import train_model
from models.DQN.self_play_training import train
from models.DQN.Config import Config as DQNConfig
from constants import SAVED_MODELS_DIRECTORY, CONFIGS_DIRECTORY
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
    train_model(env, dqn_config)


def space_game_with_c_dqn():
    game_config = Config.custom(CONFIGS_DIRECTORY / "bigger_space_game_config.yml")
    game = Game(game_config)
    p1 = create_player_1(game_config, game.game_controller.event_manager)
    p2, p2_controller = create_human_player_2(game_config, game.game_controller.event_manager)
    c_dqn_controller = CDQNController(game.game_controller.event_manager, game_config,
                                      p1, p2, Side.UP, game.game_controller.screen,
                                      dqn_path=SAVED_MODELS_DIRECTORY / "CustomDQN_09-16-16_07-01-2021" / "dqn.pt")
    game.add_player_1(PlayerTuple(p1, None, c_dqn_controller))
    game.add_player_2(PlayerTuple(p2, p2_controller, None))
    game.start()


def self_play_dqn_training():
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = False
    env = SpaceGameSelfPlayEnvironment(environment_config=env_config)
    dqn_config = DQNConfig.custom(CONFIGS_DIRECTORY / "custom_dqn_config.yml")
    train(env=env, dqn_config=dqn_config)


if __name__ == '__main__':
    train_dqn()

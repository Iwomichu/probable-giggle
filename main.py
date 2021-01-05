from space_game.Game import Game
from space_game.Player import create_human_player_2, create_player_1
from space_game.PlayerTuple import PlayerTuple
from space_game.Config import Config
from common.DQNWrapper import DQNWrapper
from constants import SAVED_MODELS_DIRECTORY, CONFIGS_DIRECTORY

if __name__ == '__main__':
    game_config = Config.custom(CONFIGS_DIRECTORY / "bigger_space_game_config.yml")
    game = Game(game_config)
    DQNWrapper.from_file(SAVED_MODELS_DIRECTORY / "c_dqn.pt")
    # p2, p2_kb = create_human_player_2()

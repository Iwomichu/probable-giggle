from space_game.Config import Config as GameConfig
from space_game.Game import game

if __name__ == '__main__':
    game_conf = GameConfig.default()
    game_conf.player_size = 32
    game_conf.bullet_width = 16
    game_conf.bullet_height = 16
    game_conf.ai_input_lag = 5
    game_conf.max_velocity = 14
    game_conf.bullet_velocity = 16

    game(game_conf)

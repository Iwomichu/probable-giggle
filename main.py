# from space_game.Config import Config as GameConfig
# from space_game.Game import game
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from models.DQN.self_play_training import train

if __name__ == '__main__':
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = True
    env = SpaceGameSelfPlayEnvironment(environment_config=env_config)
    train(env)

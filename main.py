# from space_game.Config import Config as GameConfig
# from space_game.Game import game
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from env.SpaceGameSelfPlayEnvironment import SpaceGameSelfPlayEnvironment
from models.DQN.self_play_training import train
from models.DQN.Config import Config as DQNConfig

if __name__ == '__main__':
    env_config = SpaceGameEnvironmentConfig.default()
    env_config.render = False
    dqn_config = DQNConfig.default()
    dqn_config.epoch_duration = 50
    dqn_config.n_test_runs = 5
    env = SpaceGameSelfPlayEnvironment(environment_config=env_config)
    train(env, visualize_test=True, dqn_config=dqn_config)

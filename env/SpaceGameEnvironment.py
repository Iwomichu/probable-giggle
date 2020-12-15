import gym
import pygame

from env.EnvironmentAction import EnvironmentAction, EnvironmentActionToAIActionMapping
from env.RewardSystem import RewardSystem
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping
from space_game.Config import Config
from space_game.ai.DecisionBasedController import DecisionBasedController
from space_game.domain_names import Side
from space_game.GameController import GameController
from space_game.Player import create_player_1, create_player_2
from space_game.ai.AIController import process_map


class SpaceGameEnvironment(gym.Env):
    def __init__(self):
        super(SpaceGameEnvironment, self).__init__()
        self.running = True
        self.clock = pygame.time.Clock()
        self.config = Config()
        self.game_controller = GameController(self.config)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # AGENT INITIALIZATION
        self.agent = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent)
        self.reward_system = RewardSystem(self.config, self.agent)
        self.reward_system.register(self.game_controller.event_manager)

        # OPPONENT INITIALIZATION
        self.opponent = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.ai_2 = SpaceGameEnvironmentConfig.OpponentControllerType(
            self.game_controller.event_manager,
            self.config,
            self.opponent
        )

        self.history = []
        self.action_space = gym.spaces.Discrete(len(AIActionToEventMapping))
        self.observation_space = gym.spaces.Box(high=0, low=255, shape=(64, 64, 3))

    def reset(self):
        self.game_controller = GameController(self.config)
        self.clock = pygame.time.Clock()

        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # AGENT INITIALIZATION
        self.agent = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent)
        self.reward_system = RewardSystem(self.config, self.agent)
        self.reward_system.register(self.game_controller.event_manager)

        # OPPONENT INITIALIZATION
        self.opponent = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.ai_2 = DecisionBasedController(
            self.game_controller.event_manager,
            self.config,
            self.opponent,
            self.agent,
            Side.DOWN
        )
        self.game_controller.__add_player__(self.opponent)
        self.ai_2.register(self.game_controller.event_manager)

        return process_map(self.config.window)

    def step(self, action: EnvironmentAction):
        self.clock.tick(self.config.fps)

        # AGENT CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[action]
        for event in AIActionToEventMapping[action_parsed](id(self.agent)):
            self.game_controller.event_manager.add_event(event)
        self.game_controller.__refresh__()

        # REWARD CALCULATION
        self.steps_left -= 1
        done = self.reward_system.is_game_over()
        reward = self.reward_system.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done = True

        info = {"agent_hp": self.agent.hitpoints, "opponent_hp": self.opponent.hitpoints}
        return process_map(self.config.window), reward, done, info

    def render(self, mode='human'):
        pass


if __name__ == "__main__":
    from stable_baselines.deepq.policies import CnnPolicy
    from stable_baselines import DQN

    env = SpaceGameEnvironment()
    model = DQN(CnnPolicy, env, verbose=1)
    for i in range(1000):
        model.learn(total_timesteps=10**4)
        model.save("deepq_breakout")
        print("model_saved")

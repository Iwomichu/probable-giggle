from typing import Union

import gym
from numpy import uint8

from env.EnvironmentAction import EnvironmentActionToAIActionMapping
from env.EnvironmentAction import EnvironmentAction
from env.RewardSystem import RewardSystem
from env.SimplifiedEnvironmentAction import SimplifiedEnvironmentAction
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping
from space_game.Config import Config
from space_game.domain_names import Side
from space_game.GameController import GameController
from space_game.Player import create_player_1, create_player_2


class SpaceGameEnvironment(gym.Env):
    def __init__(
            self,
            environment_config: SpaceGameEnvironmentConfig = SpaceGameEnvironmentConfig(),
            game_config: Config = None,
            previously_done_steps=0
    ):
        super(SpaceGameEnvironment, self).__init__()
        if game_config is None:
            game_config = Config.default()
        self.running = True
        self.game_config = game_config
        self.environment_config = environment_config
        self.EnvironmentAction = SimplifiedEnvironmentAction \
            if self.environment_config.use_simplified_environment_actions else EnvironmentAction
        self.renderable = environment_config.render
        self.game_controller = GameController(self.game_config, self.renderable)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps
        self.games = 0

        # AGENT INITIALIZATION
        self.agent = create_player_1(
            self.game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent)
        self.reward_system = RewardSystem(self.environment_config, self.game_config, self.agent, previously_done_steps)
        self.reward_system.register(self.game_controller.event_manager)

        # OPPONENT INITIALIZATION
        self.opponent = create_player_2(
            self.game_config,
            self.game_controller.event_manager
        )
        self.ai_2 = self.environment_config.OpponentControllerType(
            self.game_controller.event_manager,
            self.game_config,
            self.opponent,
            self.agent,
            Side.DOWN,
            self.game_controller.screen
        )

        self.history = []
        self.action_space = gym.spaces.Discrete(len(self.EnvironmentAction))
        self.observation_space = gym.spaces.Box(high=255, low=0, shape=(64, 64, 1), dtype=uint8)

    def reset(self, game_index=None):
        self.games += 1
        game_index = game_index if game_index else self.games
        self.game_controller = GameController(self.game_config, self.renderable)

        self.steps_left = self.environment_config.max_steps

        # AGENT INITIALIZATION
        self.agent = create_player_1(
            self.game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent)
        self.reward_system = RewardSystem(self.environment_config, self.game_config, self.agent, game_index)
        self.reward_system.register(self.game_controller.event_manager)

        # OPPONENT INITIALIZATION
        self.opponent = create_player_2(
            self.game_config,
            self.game_controller.event_manager
        )
        self.ai_2 = self.environment_config.OpponentControllerType(
            self.game_controller.event_manager,
            self.game_config,
            self.opponent,
            self.agent,
            Side.DOWN,
            self.game_controller.screen
        )
        self.game_controller.__add_player__(self.opponent)
        self.ai_2.register(self.game_controller.event_manager)

        return self.game_controller.screen.process_map()

    def step(self, action: Union[EnvironmentAction, SimplifiedEnvironmentAction]):
        if self.renderable:
            self.game_controller.render_screen()
        # AGENT CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[action]
        for event in AIActionToEventMapping[action_parsed](id(self.agent)):
            self.game_controller.event_manager.add_event(event)
        for _ in range(self.environment_config.step_delay):
            self.game_controller.__refresh__()

        # REWARD CALCULATION
        self.steps_left -= 1
        done = self.reward_system.is_game_over()
        reward = self.reward_system.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done = True

        info = {"agent_hp": self.agent.hitpoints, "opponent_hp": self.opponent.hitpoints}
        return self.game_controller.screen.process_map(), reward, done, info

    def render(self, mode='human'):
        pass

    def get_n_actions(self):
        return len(self.EnvironmentAction)

    def sample_observation_space(self):
        return self.game_controller.screen.process_map()

import numpy as np
import pygame

from typing import Tuple

from env.EnvironmentAction import EnvironmentActionToAIActionMapping, EnvironmentAction
from env.RewardSystem import RewardSystem
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.GameController import GameController
from space_game.Config import Config
from space_game.Player import create_player_1, create_player_2
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping

Reward = float
Observation = np.ndarray
Actions = np.ndarray
Action = EnvironmentAction
Done = bool
PlayerReturnTuple = Tuple[Reward, Observation, Done]


class SpaceGameSelfPlayEnvironment:
    @staticmethod
    def get_n_actions():
        return len(EnvironmentAction)

    @staticmethod
    def convert_observation(state: Observation) -> Observation:
        """
        Converts observation from the perspective of player_1
        to the perspective of player_2 (invert colors and rotate screen)
        :param state: Map seen as player_1
        :return: Map seen as player_2
        """
        return np.flip(state, axis=1)

    @staticmethod
    def inverse_movement(action: EnvironmentAction) -> EnvironmentAction:
        """
        Inverses action along X axis (UP <-> DOWN)

        :param action: Original action
        :return: Inversed action (UP = DOWN)
        """
        inversion_dict = {
            EnvironmentAction.MoveDown: EnvironmentAction.MoveUp,
            EnvironmentAction.MoveDownShoot: EnvironmentAction.MoveUpShoot,
            EnvironmentAction.MoveLeftDown: EnvironmentAction.MoveLeftUp,
            EnvironmentAction.MoveLeftDownShoot: EnvironmentAction.MoveLeftUpShoot,
            EnvironmentAction.MoveRightDown: EnvironmentAction.MoveRightUp,
            EnvironmentAction.MoveRightDownShoot: EnvironmentAction.MoveRightUpShoot,
            EnvironmentAction.MoveUp: EnvironmentAction.MoveDown,
            EnvironmentAction.MoveUpShoot: EnvironmentAction.MoveDownShoot,
            EnvironmentAction.MoveLeftUp: EnvironmentAction.MoveLeftDown,
            EnvironmentAction.MoveLeftUpShoot: EnvironmentAction.MoveLeftDownShoot,
            EnvironmentAction.MoveRightUp: EnvironmentAction.MoveRightDown,
            EnvironmentAction.MoveRightUpShoot: EnvironmentAction.MoveRightDownShoot
        }
        return inversion_dict.get(action) if action in inversion_dict else action

    def __init__(self, space_game_config: Config = None, environment_config: SpaceGameEnvironmentConfig = None):
        self.space_game_config = space_game_config if space_game_config is not None else Config.default()
        self.environment_config = environment_config \
            if environment_config is not None else SpaceGameEnvironmentConfig.default()
        self.running = True
        self.clock = pygame.time.Clock()
        self.game_controller = GameController(self.space_game_config, renderable=self.environment_config.render)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # UP SIDE INITIALIZATION
        self.agent_1 = create_player_1(
            self.space_game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_1)
        self.reward_system_1 = RewardSystem(self.environment_config, self.space_game_config, self.agent_1)
        self.reward_system_1.register(self.game_controller.event_manager)

        # DOWN SIDE INITIALIZATION
        self.agent_2 = create_player_2(
            self.space_game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_2)
        self.reward_system_2 = RewardSystem(self.environment_config, self.space_game_config, self.agent_2)
        self.reward_system_2.register(self.game_controller.event_manager)

        self.history = []

    def reset(self) -> Tuple[Observation, Observation]:
        """
        Reload game internals
        :return: Map of newly created game
        """

        self.running = True
        self.clock = pygame.time.Clock()
        self.game_controller = GameController(self.space_game_config, renderable=self.environment_config.render)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # UP SIDE INITIALIZATION
        self.agent_1 = create_player_1(
            self.space_game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_1)
        self.reward_system_1 = RewardSystem(self.environment_config, self.space_game_config, self.agent_1)
        self.reward_system_1.register(self.game_controller.event_manager)

        # DOWN SIDE INITIALIZATION
        self.agent_2 = create_player_2(
            self.space_game_config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_2)
        self.reward_system_2 = RewardSystem(self.environment_config, self.space_game_config, self.agent_2)
        self.reward_system_2.register(self.game_controller.event_manager)

        current_observation = self.game_controller.screen.process_map()

        return current_observation, SpaceGameSelfPlayEnvironment.convert_observation(current_observation)

    def step(self, actions: Tuple[Action, Action]) -> Tuple[PlayerReturnTuple, PlayerReturnTuple]:
        """
        Apply actions to players and resolve current frame
        :param actions: Action chosen by trained model
        :return:
        Tuple of step-information tuples for each player containing
        rewards derived from resolved frame, refreshed observation and information about game's finish.
        """
        if self.environment_config.render:
            self.game_controller.render_screen()

        # UP SIDE CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[actions[0]]
        for event in AIActionToEventMapping[action_parsed](id(self.agent_1)):
            self.game_controller.event_manager.add_event(event)

        # DOWN SIDE CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[SpaceGameSelfPlayEnvironment.inverse_movement(actions[1])]
        for event in AIActionToEventMapping[action_parsed](id(self.agent_2)):
            self.game_controller.event_manager.add_event(event)

        for _ in range(self.environment_config.step_delay):
            self.game_controller.__refresh__()

        self.steps_left -= 1

        # UP SIDE REWARD CALCULATION
        done_1: Done = self.reward_system_1.is_game_over()
        reward_1 = self.reward_system_1.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done_1 = True

        # DOWN SIDE REWARD CALCULATION
        done_2: Done = self.reward_system_2.is_game_over()
        reward_2 = self.reward_system_2.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done_2 = True

        observation = self.game_controller.screen.process_map()
        return (reward_1, observation, done_1), \
               (reward_2, SpaceGameSelfPlayEnvironment.convert_observation(observation), done_2)

    def sample_observation_space(self):
        return self.game_controller.screen.process_map()

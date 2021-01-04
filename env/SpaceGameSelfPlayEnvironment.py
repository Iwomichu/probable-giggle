import numpy as np
import pygame

from typing import Tuple

from env.EnvironmentAction import EnvironmentActionToAIActionMapping, EnvironmentAction
from env.RewardSystem import RewardSystem
from env.SpaceGameEnvironmentConfig import SpaceGameEnvironmentConfig
from space_game.GameController import GameController, process_map
from space_game.Config import Config
from space_game.Player import create_player_1, create_player_2
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping

Reward = float
Observation = np.ndarray
Actions = np.ndarray
Action = EnvironmentAction
Done = bool


class SpaceGameSelfPlayEnvironment:
    @staticmethod
    def convert_observation(state: Observation) -> Observation:
        """
        Converts observation from the perspective of player_1
        to the perspective of player_2 (invert colors and rotate screen)
        :param state: Map seen as player_1
        :return: Map seen as player_2
        """
        return np.flip(state)

    def __init__(self):
        self.config = Config()
        self.running = True
        self.clock = pygame.time.Clock()
        self.game_controller = GameController(self.config)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # UPPER SIDE INITIALIZATION
        self.agent_1 = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_1)
        self.reward_system_1 = RewardSystem(self.config, self.agent_1)
        self.reward_system_1.register(self.game_controller.event_manager)

        # LOWER SIDE INITIALIZATION
        self.agent_2 = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_2)
        self.reward_system_2 = RewardSystem(self.config, self.agent_2)
        self.reward_system_2.register(self.game_controller.event_manager)

        self.history = []

    def reset(self) -> Tuple[Observation, Observation]:
        """
        Reload game internals
        :return: Map of newly created game
        """

        self.running = True
        self.clock = pygame.time.Clock()
        self.game_controller = GameController(self.config)
        self.steps_left = SpaceGameEnvironmentConfig.max_steps

        # UPPER SIDE INITIALIZATION
        self.agent_1 = create_player_1(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_1)
        self.reward_system_1 = RewardSystem(self.config, self.agent_1)
        self.reward_system_1.register(self.game_controller.event_manager)

        # LOWER SIDE INITIALIZATION
        self.agent_2 = create_player_2(
            self.config,
            self.game_controller.event_manager
        )
        self.game_controller.__add_player__(self.agent_2)
        self.reward_system_2 = RewardSystem(self.config, self.agent_2)
        self.reward_system_2.register(self.game_controller.event_manager)

        current_observation = process_map(self.game_controller.screen)

        return current_observation, SpaceGameSelfPlayEnvironment.convert_observation(current_observation)

    def step(
            self,
            actions: Tuple[Action, Action]
    ) -> Tuple[Tuple[Reward, Observation, Done], Tuple[Reward, Observation, Done]]:
        """
        Apply actions to players and resolve current frame
        :param actions: Action chosen by trained model
        :return:
        Tuple of step-information tuples for each player containing
        rewards derived from resolved frame, refreshed observation and information about game's finish.
        """
        self.clock.tick(self.config.fps)

        # UPPER SIDE CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[actions[0]]
        for event in AIActionToEventMapping[action_parsed](id(self.agent_1)):
            self.game_controller.event_manager.add_event(event)

        # LOWER SIDE CHOICE HANDLING
        action_parsed = EnvironmentActionToAIActionMapping[actions[1]]
        for event in AIActionToEventMapping[action_parsed](id(self.agent_2)):
            self.game_controller.event_manager.add_event(event)

        self.game_controller.__refresh__()
        self.steps_left -= 1

        # UPPER REWARD CALCULATION
        done_1: Done = self.reward_system_1.is_game_over()
        reward_1 = self.reward_system_1.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done_1 = True

        # LOWER REWARD CALCULATION
        done_2: Done = self.reward_system_2.is_game_over()
        reward_2 = self.reward_system_2.get_reward_and_reset() + SpaceGameEnvironmentConfig.step_reward
        if self.steps_left == 0:
            done_2 = True

        observation = process_map(self.game_controller.screen)
        return (reward_1, observation, done_1), \
               (reward_2, SpaceGameSelfPlayEnvironment.convert_observation(observation), done_2)

from pathlib import Path

import numpy as np

from space_game.Screen import Screen
from space_game.ai.AIController import AIController
from space_game.Config import Config
from space_game.Player import Player
from space_game.domain_names import Side
from space_game.managers.EventManager import EventManager
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping
from common.DQNWrapper import DQNWrapper

import torch


class CDQNController(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player,
                 opponent: Player, side: Side, screen: Screen, *,
                 dqn_model: torch.nn.Module = None, dqn_wrapper: DQNWrapper = None, dqn_path: Path = None):
        super().__init__(event_manager, config, player, opponent, side, screen)
        self.side = side
        if dqn_wrapper is not None:
            self.dqn_wrapper = dqn_wrapper
        else:
            if dqn_model is not None:
                self.dqn_wrapper = DQNWrapper(dqn_model)
            else:
                self.dqn_wrapper = DQNWrapper.from_file(dqn_path)

    def react(self):
        current_map = self.get_current_map()
        if self.side == Side.UP:
            choice = self.dqn_wrapper.predict(current_map)
        else:
            choice = self.dqn_wrapper.predict(np.flip(current_map, axis=1).copy())

        for event in AIActionToEventMapping[choice](id(self.player)):
            self.event_manager.add_event(event)

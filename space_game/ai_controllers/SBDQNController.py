from stable_baselines import DQN

from space_game.ai_controllers.AIController import AIController
from space_game.Config import Config
from space_game.Player import Player
from space_game.managers.EventManager import EventManager
from space_game.AIActionToEventMapping import AIActionToEventMapping


class SBDQNController(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player, dqn_model: DQN):
        super().__init__(event_manager, config, player)
        self.dqn = dqn_model

    def react(self):
        current_map = self.get_current_map()
        choice, _ = self.dqn.predict(current_map)
        for event in AIActionToEventMapping[choice](id(self.player)):
            self.event_manager.add_event(event)


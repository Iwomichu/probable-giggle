from space_game.ai.AIController import AIController
from space_game.Config import Config
from space_game.Player import Player
from space_game.managers.EventManager import EventManager
from space_game.ai.AIActionToEventMapping import AIActionToEventMapping


class AlwaysShootingAI(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player):
        super().__init__(event_manager, config, player)

    def react(self):
        current_map = self.get_current_map()
        choice = 0
        for event in AIActionToEventMapping[choice](id(self.player)):
            self.event_manager.add_event(event)

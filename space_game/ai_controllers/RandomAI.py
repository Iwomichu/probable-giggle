from random import randrange

from space_game.ai_controllers.AIController import AIController
from space_game.Config import Config
from space_game.Player import Player
from space_game.managers.EventManager import EventManager
from space_game.AIActionToEventMapping import AIActionToEventMapping


class RandomAI(AIController):
    def __init__(self, event_manager: EventManager, config: Config, player: Player):
        super().__init__(event_manager, config, player)

    def react(self):
        current_map = self.get_current_map()
        choice = randrange(start=0, stop=len(AIActionToEventMapping))
        for event in AIActionToEventMapping[choice](id(self.player)):
            self.event_manager.add_event(event)

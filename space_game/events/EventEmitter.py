from space_game.managers.EventManager import EventManager


class EventEmitter:
    def __init__(self, event_manager: EventManager):
        self.event_manager = event_manager

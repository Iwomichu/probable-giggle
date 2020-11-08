from dataclasses import dataclass

from space_game.events.Event import Event


@dataclass
class UpdateAIControllersEvent(Event):
    pass

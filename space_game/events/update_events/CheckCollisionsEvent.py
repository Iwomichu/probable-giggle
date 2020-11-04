from dataclasses import dataclass

from space_game.events.Event import Event


@dataclass
class CheckCollisionsEvent(Event):
    pass

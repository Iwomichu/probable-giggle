from dataclasses import dataclass

from space_game.AccelerationDirection import AccelerationDirection
from space_game.events.Event import Event
from space_game.domain_names import ObjectId


@dataclass
class PlayerAcceleratedEvent(Event):
    player_id: ObjectId = None
    direction: AccelerationDirection = None

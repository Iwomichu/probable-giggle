from dataclasses import dataclass

from space_game.events.Event import Event
from space_game.domain_names import ObjectId


@dataclass
class CollisionOccurredEvent(Event):
    participant_1_id: ObjectId = None
    participant_2_id: ObjectId = None
from dataclasses import dataclass

from space_game.domain_names import ObjectId
from space_game.events.Event import Event


@dataclass
class NewStatefulAddedEvent(Event):
    stateful_id: ObjectId

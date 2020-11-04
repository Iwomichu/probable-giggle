from dataclasses import dataclass

from space_game.events.Event import Event
from space_game.domain_names import ObjectId, HitPoint


@dataclass
class DamageDealtEvent(Event):
    damaged_id: ObjectId = None
    amount: HitPoint = None
from dataclasses import dataclass

from space_game.domain_names import ObjectId
from space_game.events.Event import Event
from space_game.Projectile import Projectile


@dataclass
class ProjectileFiredEvent(Event):
    projectile_id: ObjectId = None

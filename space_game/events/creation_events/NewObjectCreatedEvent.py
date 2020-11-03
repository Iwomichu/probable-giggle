from dataclasses import dataclass
from typing import Any

from space_game.events.Event import Event


@dataclass
class NewObjectCreatedEvent(Event):
    new_object: Any

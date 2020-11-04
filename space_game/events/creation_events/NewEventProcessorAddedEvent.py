from dataclasses import dataclass
from typing import Any

from space_game.domain_names import ObjectId
from space_game.events.Event import Event


@dataclass
class NewEventProcessorAddedEvent(Event):
    processor_id: ObjectId
    event_type: Any

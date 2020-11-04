from dataclasses import dataclass

from space_game.domain_names import KeyId
from space_game.events.Event import Event


@dataclass
class KeyPressedEvent(Event):
    key_id: KeyId

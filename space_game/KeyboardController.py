from typing import Any
from dataclasses import dataclass

KeyId = Any


@dataclass
class KeyboardController:
    LEFT: KeyId
    RIGHT: KeyId
    UP: KeyId
    DOWN: KeyId
    SHOOT: KeyId

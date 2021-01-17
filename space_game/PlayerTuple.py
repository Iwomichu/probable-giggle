from dataclasses import dataclass
from typing import Optional

from space_game.KeyboardController import KeyboardController
from space_game.Player import Player
from space_game.ai.AIController import AIController


@dataclass
class PlayerTuple:
    player: Player
    keyboard_controller: Optional[KeyboardController] = None
    ai_controller: Optional[AIController] = None

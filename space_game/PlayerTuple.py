from dataclasses import dataclass

from space_game.KeyboardController import KeyboardController
from space_game.Player import Player
from space_game.ai.AIController import AIController


@dataclass
class PlayerTuple:
    player: Player
    keyboard_controller: KeyboardController = None
    ai_controller: AIController = None

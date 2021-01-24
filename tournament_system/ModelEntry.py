from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, ClassVar

from space_game.Screen import Screen
from space_game.ai.AIController import AIController
from space_game.ai.CDQNController import CDQNController
from space_game.ai.SBDQNController import SBDQNController
from space_game.domain_names import Side
from space_game.managers.EventManager import EventManager
from space_game.Config import Config
from space_game.Player import Player

ModelID = int
ModelInstance = Any


@dataclass
class ModelEntry:
    id: ModelID = field(init=False)
    create_controller: Callable[[EventManager, Config, Player, Player, Side, Screen], AIController]
    entry_count: ClassVar[int] = 0

    def __init__(self):
        self.id = ModelEntry.entry_count
        ModelEntry.entry_count += 1


class SBDQNEntry(ModelEntry):
    def __init__(self, *, model: ModelInstance = None, model_path: Path = None):
        super().__init__()
        self.create_controller = lambda em, c, p1, p2, side, screen: SBDQNController(em, c, p1, p2, side, screen, sb_dqn_model=model, sb_dqn_path=model_path)


class CDQNEntry(ModelEntry):
    def __init__(self, *, model: ModelInstance = None, model_path: Path = None):
        super().__init__()
        self.create_controller = lambda em, c, p1, p2, side, screen: CDQNController(em, c, p1, p2, side, screen, dqn_model=model, dqn_path=model_path)

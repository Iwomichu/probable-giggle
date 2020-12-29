from dataclasses import dataclass
from enum import Enum, auto

from tournament_system.ModelEntry import ModelEntry
from tournament_system.RoundStat import RoundStat


class RoundResult(Enum):
    FIRST_PLAYER_WIN = auto()
    SECOND_PLAYER_WIN = auto()
    DRAW = auto()


@dataclass
class RoundReport:
    result: RoundResult
    first_model: ModelEntry
    second_model: ModelEntry
    stat: RoundStat = RoundStat()

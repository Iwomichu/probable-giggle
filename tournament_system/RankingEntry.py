from dataclasses import dataclass

from tournament_system.ModelEntry import ModelEntry


@dataclass
class RankingEntry:
    model_entry: ModelEntry
    wins_count: int
    loses_count: int
    draws_count: int

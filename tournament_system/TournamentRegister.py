from typing import Dict, List
from itertools import combinations

import numpy as np

from tournament_system.ModelEntry import ModelEntry, ModelInstance, ModelID
from tournament_system.RankingEntry import RankingEntry
from tournament_system.RoundReport import RoundReport, RoundResult
from tournament_system.RoundStat import RoundStat


def one_round(fst_model: ModelEntry, snd_model: ModelEntry) -> RoundReport:
    match_result = np.random.choice([
        RoundResult.DRAW, RoundResult.FIRST_PLAYER_WIN, RoundResult.SECOND_PLAYER_WIN
    ], 1)[0]
    stats = RoundStat()
    return RoundReport(match_result, fst_model, snd_model, stats)


def calculate_ranking_points(ranking_entry: RankingEntry) -> int:
    return ranking_entry.wins_count * 3 + ranking_entry.draws_count


class TournamentRegister(object):
    def __init__(self, length_of_learning: int, rounds_in_the_game: int, *models: ModelInstance):
        self.ranking_table: List[RankingEntry] = []
        self.results_of_tournament: List[RoundReport] = []
        self.length_of_learning = length_of_learning
        self.rounds_in_the_game = rounds_in_the_game
        self.models: Dict[ModelID, ModelEntry] = {idx: ModelEntry(idx, model) for idx, model in enumerate(models)}
        self.next_model_id = len(self.models)
        print(self.models)

    def add_model(self, model: ModelInstance) -> None:
        if model in self.models:
            raise Exception("model already exist!")
        self.models[self.next_model_id] = (ModelEntry(self.next_model_id, model))
        self.next_model_id += 1
        print(self.models)

    def remove_model_by_id(self, id_to_remove: ModelID) -> None:
        del self.models[id_to_remove]
        print(self.models)

    def remove_model_by_model(self, model: ModelInstance) -> None:
        for idx, model_ in self.models.items():
            if model_.model == model:
                del self.models[idx]
                break
        print(self.models)

    def tournament(self) -> None:
        games = combinations(self.models.values(), 2)
        for match in games:
            self.results_of_tournament.append(one_round(match[0], match[1]))
        for result in self.results_of_tournament:
            print(result)

    def get_wins(self, model_id: ModelID) -> int:
        wins = [
            result
            for result in self.results_of_tournament
            if (result.first_model.id == model_id and result.result == RoundResult.FIRST_PLAYER_WIN) or
               (result.second_model.id == model_id and result.result == RoundResult.SECOND_PLAYER_WIN)
        ]
        return len(wins)

    def get_loses(self, model_id: ModelID) -> int:
        losses = [
            result
            for result in self.results_of_tournament
            if (result.second_model.id == model_id and result.result == RoundResult.FIRST_PLAYER_WIN) or
               (result.first_model.id == model_id and result.result == RoundResult.SECOND_PLAYER_WIN)
        ]
        return len(losses)

    def get_draws(self, model_id: ModelID) -> int:
        draws = [
            result
            for result in self.results_of_tournament
            if (result.result == RoundResult.DRAW and result.second_model.id == model_id and result.first_model.id)
        ]
        return len(draws)

    def ranking(self) -> None:
        for model_ in self.models.values():
            self.ranking_table.append(
                RankingEntry(model_, self.get_wins(model_.id), self.get_loses(model_.id), self.get_draws(model_.id)))
        self.ranking_table.sort(key=calculate_ranking_points)
        for position in reversed(self.ranking_table):
            print(position)


if __name__ == '__main__':
    dqn = "dummy dqn"
    cdqn = "dummy cdqn"
    cnn = "dummy cnn"

    tournament = TournamentRegister(100, 10, dqn, cdqn, cnn)
    tournament.tournament()
    tournament.ranking()

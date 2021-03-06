from typing import Dict, List
from itertools import combinations

from space_game.Config import Config
from space_game.Game import Game
from space_game.Player import create_player_1, create_player_2
from space_game.PlayerTuple import PlayerTuple
from space_game.Winner import Winner
from space_game.domain_names import Side
from tournament_system.ModelEntry import ModelEntry, ModelInstance, ModelID
from tournament_system.RankingEntry import RankingEntry
from tournament_system.RoundReport import RoundReport, RoundResult
from tournament_system.RoundStat import RoundStat


def one_round(fst_model: ModelEntry, snd_model: ModelEntry, game_in_round:int) -> RoundReport:
    points = 0
    for i in range(game_in_round):
        game_config = Config.unified()
        game = Game(game_config, max_game_length=2000)
        p1 = create_player_1(game_config, game.game_controller.event_manager)
        p2 = create_player_2(game_config, game.game_controller.event_manager)
        c1 = fst_model.create_controller(game.game_controller.event_manager, game_config,
                                          p1, p2, Side.UP, game.game_controller.screen)
        c2 = snd_model.create_controller(game.game_controller.event_manager, game_config,
                                          p2, p1, Side.DOWN, game.game_controller.screen)
        game.add_player_1(PlayerTuple(p1, None, c1))
        game.add_player_2(PlayerTuple(p2, None, c2))
        winner = game.start()

        if winner == Winner.PLAYER1:
            points += 1
        elif winner == Winner.PLAYER2:
            points -= 1
    stats = RoundStat()
    if points == 0:
        return RoundReport(RoundResult.DRAW, fst_model, snd_model, stats)
    if points > 0:
        return  RoundReport(RoundResult.FIRST_PLAYER_WIN, fst_model, snd_model, stats)
    return  RoundReport(RoundResult.SECOND_PLAYER_WIN, fst_model, snd_model, stats)


def calculate_ranking_points(ranking_entry: RankingEntry) -> int:
    return ranking_entry.wins_count * 3 + ranking_entry.draws_count


class TournamentRegister(object):
    def __init__(self, length_of_learning: int, rounds_in_the_game: int):
        self.ranking_table: List[RankingEntry] = []
        self.results_of_tournament: List[RoundReport] = []
        self.length_of_learning = length_of_learning
        self.rounds_in_the_game = rounds_in_the_game
        self.models: Dict[ModelID, ModelEntry] = {}
        self.next_model_id = len(self.models)
        print(self.models)

    def add_model(self, model_entry: ModelEntry) -> None:
        self.models[self.next_model_id] = model_entry
        self.next_model_id += 1
        print(self.models)

    def remove_model_by_id(self, id_to_remove: ModelID) -> None:
        del self.models[id_to_remove]
        print(self.models)

    def tournament(self) -> None:
        games = combinations(self.models.values(), 2)
        for match in games:
            self.results_of_tournament.append(one_round(match[0], match[1],self.rounds_in_the_game))
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
            if (result.result == RoundResult.DRAW and (result.first_model.id == model_id or result.second_model.id == model_id))
        ]
        return len(draws)

    def ranking(self) -> None:
        for model_ in self.models.values():
            self.ranking_table.append(
                RankingEntry(model_, self.get_wins(model_.id), self.get_loses(model_.id), self.get_draws(model_.id)))
        self.ranking_table.sort(key=calculate_ranking_points)
        for position in reversed(self.ranking_table):
            print(position)

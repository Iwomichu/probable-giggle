from collections import namedtuple
import numpy as np
Model = namedtuple('Model_with_id', ('model', 'id'))
Result_of_one_round = namedtuple('Result_of_one_round', ('match_result', 'first_model', 'second_model', 'stats'))
Ranking = namedtuple('Ranking', ('model', 'model_id', 'won_matches', 'lost_matches', 'draws'))


class TournamentRegister(object):
    """tournament class: everywhere we have 'model', we have model like DQN. Other cases we have namedtuple Model. It
    is marked in functions."""

    def __init__(self, length_of_learning: int, rounds_in_the_game: int, *models: tuple):
        self.ranking_table = []
        self.results_of_tournament = []
        self.length_of_learning = length_of_learning
        self.rounds_in_the_game = rounds_in_the_game
        if len(models) == 0:
            self.models = []
        else:
            self.models = [Model(model[0], model[1]) for model in models]
        print(self.models)

    def add_model(self, model):
        for model_ in self.models:
            if model_.model == model[0]:
                raise Exception("model already exist!")
            elif model_.id == model[1]:
                raise Exception("this id is used by other model!")
        self.models.append(Model(model[0], model[1]))
        print(self.models)

    def remove_model_by_id(self, id_to_remove: str):
        for model_ in self.models:
            if model_.id == id_to_remove:
                self.models.remove(model_)
        print(self.models)

    def remove_model_by_model(self, model):
        for model_ in self.models:
            if model_.model == model:
                self.models.remove(model_)
        print(self.models)

    def one_round(self, fst_model: Model, snd_model: Model):
        match_result = np.random.choice(["draw", fst_model.id, snd_model.id], 1)[0]
        stats = 0
        return Result_of_one_round(match_result, fst_model, snd_model, stats)

    def tournament(self):
        how_many_players = len(self.models)
        games = [(self.models[player1_index], self.models[player2_index])\
                 for player1_index in range(how_many_players) for player2_index in range(player1_index+1, how_many_players)]
        for match in games:
            self.results_of_tournament.append(self.one_round(match[0], match[1]))
        for i in self.results_of_tournament:
            print(i.match_result)

    def get_wins(self, model_id):
        won_games = 0
        for match in self.results_of_tournament:
            if match.match_result == model_id:
                won_games += 1
        return won_games

    def get_loses(self, model_id):
        loses_games = 0
        for match in self.results_of_tournament:
            if (match.first_model.id == model_id or match.second_model.id == model_id) and (match.match_result != model_id and match.match_result != 'draw'):
                loses_games += 1
        return loses_games

    def get_draws(self, model_id):
        draws = 0
        for match in self.results_of_tournament:
            if match.match_result == 'draw' and (match.first_model.id == model_id or match.second_model.id == model_id):
                draws += 1
        return draws

    def ranking(self):
        for model_ in self.models:
            self.ranking_table.append(
                Ranking(model_.model, model_.id, self.get_wins(model_.id), self.get_loses(model_.id), self.get_draws(model_.id)))
        self.ranking_table.sort(key=lambda x: x.won_matches * 3 + x.draws)
        for position in reversed(self.ranking_table):
            print(position)


import math
from enum import IntEnum
from random import choice, shuffle

from nbformat import current_nbformat

from src.base.game import Game, Turn
from src.base.player import Player, RandomPlayer
from src.zombie.zombieDiceGame import ZombieDiceGame
from src.zombie.zombieDicePlayers import (GreedyZombie, IntelligentZombie,
                                          RandomZombie, SafeZombie)


class TieBreaker(IntEnum):
    random = 0
    keep_playing = 1
    check_draws = 2
    earliest_win = 3

class Bracket:
    def __init__(self, players, number_games, gameClass=Game, tiebreaker=TieBreaker.keep_playing):
        self.players = players
        self.gameClass = gameClass
        self.number_games = number_games
        self.tiebreaker = tiebreaker

        self.history = []
        self.break_tie_calls = 0

    def play(self):
        self.game = self.gameClass(self.players)
        for _ in range(self.number_games):
            winners = self.play_single_game(self.game)
            self.__register_game__(winners)
            self.shuffle_players()
        return self.get_winners()

    def play_single_game(self, game):
        for player in self.players:
            player.reset()
        winners = game.play()
        game.reset()
        return winners

    def break_tie(self, players):
        self.break_tie_calls += 1
        if self.break_tie_calls < 5:
            if self.tiebreaker == TieBreaker.keep_playing:
                return self.__tiebreaker_keep_playing__()
            elif self.tiebreaker == TieBreaker.check_draws:
                return self.__tiebreaker_check_draws__(players)
            elif self.tiebreaker == TieBreaker.earliest_win:
                return self.__tiebreaker_earliest_win__(players)
            else:
                raise NotImplemented
        else:
            return self.__tiebreaker_random__(players)

    def shuffle_players(self):
        shuffle(self.players)

    def get_winners(self):
        winners = [player for player in self.players if player.get_wins() == max([p.get_wins() for p in self.players])]
        while len(winners) >= 2:
            winners = self.break_tie(winners)
        return winners

    def __tiebreaker_keep_playing__(self):
        winners = self.play_single_game(self.game)
        self.__register_game__(winners)
        self.shuffle_players()
        return self.get_winners()

    def __tiebreaker_check_draws__(self, players):
        draws = [(player, player.get_draws()) for player in players]
        winner = max(draws, key=lambda d : d[1])[0]
        return [winner]

    def __tiebreaker_earliest_win__(self, players):
        for past_winner in self.history:
            for player in players:
                if len(past_winner) == 1 and past_winner[0] == str(player):
                    return [player]

    def __tiebreaker_random__(self, players):
        return [choice(players)]

    def __register_game__(self, winners):
        self.history.append(tuple([str(winner) for winner in winners]))

class Tournament:
    def __init__(self, players, size_bracket, number_games, gameClass=Game, 
        randomPlayerClass=RandomPlayer, tiebreaker='keep_playing') -> None:

        #Players related
        self.players = players
        self.randomPlayerClass = randomPlayerClass

        #Game related
        self.size_bracket = size_bracket
        self.number_games = number_games
        self.gameClass = gameClass
        self.tiebreaker = tiebreaker

        #Tournament related
        self.contestants = []

    def preleminary_selection(self, number_prep_games=100):
        number_contestants = int(math.pow(self.size_bracket, 
            math.floor(math.log(len(self.players), self.size_bracket))))
        results = []
        for index, player in enumerate(self.players):
            players = [player] + [self.randomPlayerClass(f'random{i}') for i in range(self.size_bracket-1)]
            bracket = Bracket(players, number_prep_games, self.gameClass)
            bracket.play()
            results.append((index, player.get_wins()))
        results.sort(key=lambda d : -d[1])
        results = results[:number_contestants]
        self.contestants = [self.players[index] for index, _ in results]
        print([(p,p.get_wins()) for p in self.contestants])
        return self.contestants

    def play(self):
        assert(len(self.contestants)%self.size_bracket==0)
        shuffle(self.contestants)
        while(len(self.contestants) > 1):
            current_winners = []
            for contestant in self.contestants:
                contestant.reset_wins()
                contestant.increment_tournament_position()
            for index, player in enumerate(self.contestants):
                if (index+1)%self.size_bracket==0:
                    players = self.contestants[index-self.size_bracket+1:index+1]
                    bracket = Bracket(players, self.number_games, self.gameClass)
                    winners = bracket.play()
                    assert(len(winners) == 1)
                    current_winners.append(winners[0])
            self.contestants = current_winners
        self.contestants[0].increment_tournament_position()
        return self.contestants


if __name__ == "__main__":
    number_games = 100
    players = ([RandomZombie('MyRandom' + str(i), seed=i) for i in range(300)] + 
        [GreedyZombie('Greedy' + str(i)) for i in range(300)] + 
        [SafeZombie('Safe' + str(i)) for i in range(300)] + 
        [IntelligentZombie('OldAI'+ str(i), 'stats/best_player_feedforward_1', 'config-feedforward') for i in range(300)] + 
        [IntelligentZombie('AI'+ str(i), 'stats/winner-feedforward', 'config-feedforward') for i in range(300)])
    tournament = Tournament(players, 4, number_games, ZombieDiceGame, RandomZombie)
    tournament.preleminary_selection()
    w = tournament.play()
    print(w)
    print('\n'.join([f"{str(player)}:{player.get_tournament_position()}" for player in players]))
